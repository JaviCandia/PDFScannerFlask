import os
import psycopg2
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv


load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Cargar el modelo de embeddings
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

def get_db_connection():
    """Establece conexión con la base de datos PostgreSQL."""
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

def find_best_candidates_for_roles(top_n=5, output_file="matched_roles.json"):
    """Busca los mejores candidatos para cada rol basado en embeddings vectoriales mejorados y guarda el JSON."""

    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()

    # Obtener todos los roles con embeddings
    query_roles = """
    SELECT role_id, role_name, description, main_skill,project, secondary_skill
    FROM roles
    """
    
    cursor.execute(query_roles)
    roles = cursor.fetchall()  # Lista de roles en la BD

    results = []  # Almacena las coincidencias de roles con candidatos

    for role in roles:
        role_id, role_name, description, main_skill,project, secondary_skill = role

        print(f"\n Buscando candidatos para el rol: {role_name} (ID: {role_id})")

        # Generamos el nuevo embedding para el rol
        role_text = f"{role_name} - {description} - Skills: {main_skill}, {secondary_skill}"
        role_embedding = model.encode(role_text)

        # Consulta SQL para buscar candidatos con embeddings similares al rol
        query_candidates = """
        SELECT id, name, email, skills, summary, embedding
        FROM candidate
        """

        cursor.execute(query_candidates)
        candidates = cursor.fetchall()

        matched_candidates = []
        highest_similarity = 0  # Guardará la mejor similitud encontrada

        for candidate in candidates:
            candidate_id, candidate_name, email, skills, summary, candidate_embedding = candidate
            
            # Generamos el nuevo embedding del candidato incluyendo skills
            skills_text = ", ".join(skills) if skills else "No skills provided"
            candidate_text = f"{summary} Skills: {skills_text}"
            new_candidate_embedding = model.encode(candidate_text)

            # Calculamos la similitud coseno
            similarity = model.similarity(role_embedding, new_candidate_embedding)

            # Convertir Tensor a float antes de redondear
            similarity_score = round((1 - similarity).item(), 4)

            matched_candidates.append({
                "candidate_id": candidate_id,
                "name": candidate_name,
                "email": email,
                "skills": skills,
                "summary": summary,
                "similarity_score": similarity_score
            })

            # Guardamos la mayor similitud encontrada
            highest_similarity = max(highest_similarity, similarity_score)

        results.append({
            "role_id": role_id,
            "role_name": role_name,
            "description": description,
            "main_skill": main_skill,
            "project": project,
            "secondary_skill": secondary_skill,
            "highest_similarity": highest_similarity,  # Para ordenar después
            "matched_candidates": matched_candidates
        })

    # Cerrar conexión con la BD
    conn.close()

    # Ordenar roles por mayor `highest_similarity` primero
    results.sort(key=lambda x: x["highest_similarity"], reverse=True)

    # Guardar resultados en un archivo JSON
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)

    print(f"\n Resultados guardados en {output_file}")
    return results

# Ejecutar búsqueda de candidatos por rol y guardar en JSON
matched_roles = find_best_candidates_for_roles(top_n=5, output_file="matched_roles.json")

# También imprimimos en consola
print(json.dumps(matched_roles, indent=4, ensure_ascii=False))
