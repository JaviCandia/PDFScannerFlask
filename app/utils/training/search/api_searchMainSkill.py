
import os
import psycopg2
import re
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

#  Cargar variables de entorno desde `.env`
load_dotenv()

#  Obtener credenciales de la base de datos desde variables de entorno
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

#  Inicializar FastAPI
app = FastAPI(
    title="Job Matching API",
    description="Search for job roles using AI embeddings and predict levels.",
    version="1.0.0"
)

#  Cargar el modelo local
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

#  Lista de tecnologías comunes para validación
TECH_KEYWORDS = [
    "React", "Redux", "Tailwind", "Angular", "Vue", "JavaScript", "Node.js", "TypeScript",
    "Django", "Flask", "Python", "Java", "Spring", "SQL", "PostgreSQL", "MongoDB", "Express",
    "GraphQL", "Kubernetes", "Docker", "AWS", "Azure", "CI/CD", "Microservices"
]

#  Conectar a PostgreSQL
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

#  Modelo de solicitud con ejemplos
class CandidateProfile(BaseModel):
    description: str = Field(
        ..., 
        example="I am a frontend developer with experience in React, Redux and Tailwind CSS."
    )
    mainSkill: Optional[List[str]] = Field(
        None, 
        example=["React", "Redux", "Tailwind"]
    )

@app.post("/search_roles", summary="Find job roles based on description and skills")
async def search_roles(profile: CandidateProfile):
    """
    **Description**: Receives a job description and an optional list of skills (`mainSkill`).  
    Returns the most similar job roles based on AI embeddings.
    
    **Usage**:  
    - If `mainSkill` is provided, those technologies will be used for the search.
    - If `mainSkill` is not provided, the API extracts technologies from `description`.

    **Example Request**:
    ```json
    {
        "description": "I am a frontend developer with experience in React, Redux and Tailwind CSS.",
        "mainSkill": ["React", "Redux", "Tailwind"]
    }
    ```
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}

    cursor = conn.cursor()

    #  Si el usuario no envía habilidades, extraerlas de la descripción
    skills_found = profile.mainSkill if profile.mainSkill else extract_skills(profile.description)

    print(f"🔍 Detected skills: {skills_found}")

    #  Generar embedding basado en la descripción
    embedding_candidate = model.encode(profile.description).tolist()
    embedding_str = "[" + ", ".join(map(str, embedding_candidate)) + "]"

    #  Construir la consulta SQL dinámicamente
    search_filters = " OR ".join(["role_name ILIKE %s OR main_skill ILIKE %s OR secondary_skill ILIKE %s"] * len(skills_found))
    search_values = sum(([f"%{skill}%", f"%{skill}%", f"%{skill}%"] for skill in skills_found), [])

    try:
        sql_query = f"""
            SELECT role_id, role_name, project, description, main_skill, secondary_skill, location, embedding <=> %s::vector AS similarity
            FROM roles
            WHERE {search_filters}
            ORDER BY similarity
            LIMIT 5;
        """
        
        cursor.execute(sql_query, (embedding_str, *search_values))
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        #  Formatear los resultados en JSON
        roles = [
            {
                "role_id": role[0],
                "role_name": role[1],
                "project": role[2],
                "description": role[3][:150] + "...",  # Limitar descripción a 150 caracteres
                "main_skill": role[4],
                "secondary_skill": role[5],
                "location": role[6],
                "similarity": float(role[7])  # Convertir a float para JSON
            }
            for role in resultados
        ]

        return {
            "query": profile.description,
            "main_skills_used": skills_found,
            "matches": roles
        }

    except Exception as e:
        return {"error": f"Error executing query: {e}"}

#  Función para extraer habilidades clave del perfil usando expresiones regulares
def extract_skills(description):
    found_skills = [tech for tech in TECH_KEYWORDS if re.search(rf"\b{tech}\b", description, re.IGNORECASE)]
    return found_skills if found_skills else ["React"]  # Por defecto, usar React si no se detecta nada


# uvicorn app.utils.training.api_searchMainSkill:app --host 0.0.0.0 --port 8000
