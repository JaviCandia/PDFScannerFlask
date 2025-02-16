import psycopg2
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

#  Cargar variables de entorno desde `.env`
load_dotenv()

#  Obtener credenciales desde el entorno
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

#  Cargar el modelo local
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

#  Conectar a PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print(" Conexión exitosa a PostgreSQL")
except Exception as e:
    print(f" Error al conectar con la base de datos: {e}")
    exit()

#  Perfil del candidato
candidate_profile = "Senior Frontend Developer with 5 years of experience in React, JavaScript, and Agile methodologies."

#  Generar embedding del candidato
embedding_candidato = model.encode(candidate_profile).tolist()

#  Convertir el embedding a un formato compatible con PostgreSQL (vector)
embedding_str = "[" + ", ".join(map(str, embedding_candidato)) + "]"

#  Ejecutar la consulta con el embedding
try:
    cursor.execute("""
        SELECT role_id, role_name, project, description, main_skill, secondary_skill, location, embedding <=> %s::vector AS similarity
        FROM roles
        WHERE role_name ILIKE %s OR main_skill ILIKE %s OR secondary_skill ILIKE %s
        ORDER BY similarity
        LIMIT 5;
    """, (embedding_str, "%Angular%", "%React%", "%React%"))

    #  Mostrar resultados
    resultados = cursor.fetchall()
    print("\n **Resultados de la búsqueda:**")
    for role in resultados:
        print(f" ID: {role[0]}, Rol: {role[1]}, Proyecto: {role[2]}, Ubicación: {role[6]}")
        print(f" Descripción: {role[3][:100]}...")  # Solo mostrar los primeros 100 caracteres
        print(f" Habilidades: {role[4]}, {role[5]}")
        print("-" * 60)

except Exception as e:
    print(f" Error ejecutando la consulta: {e}")

#  Cerrar conexión
cursor.close()
conn.close()
print(" Conexión cerrada")
