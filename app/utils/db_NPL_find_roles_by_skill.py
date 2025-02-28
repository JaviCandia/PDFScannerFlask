import os
import psycopg2
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Cargar variables de entorno desde `.env`
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
        print(f"❌ Error al conectar con la base de datos: {e}")
        return None

def find_roles_for_scrum_master(min_experience=5, top_n=5, output_file="scrum_master_roles.json"):
    """Busca roles de Scrum Master con más de 5 años de experiencia usando embeddings."""
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Perfil de búsqueda para Scrum Master con más de 5 años de experiencia
    search_text = "Big Data with more than 5 years of experience in Agile methodologies, team leadership, and project delivery."
    search_embedding = model.encode(search_text)
    
    # Consulta SQL para obtener roles relevantes
    query_roles = """
    SELECT role_id, role_name, description, main_skill, project, secondary_skill, embedding <=> %s::vector AS similarity
    FROM roles
    WHERE role_name ILIKE %s OR main_skill ILIKE %s OR secondary_skill ILIKE %s OR description ILIKE %s
    ORDER BY similarity
    LIMIT %s;
    """
    
    cursor.execute(query_roles, (search_embedding.tolist(), "%Scrum Master%", "%5 years%", top_n))
    roles = cursor.fetchall()
    
    results = []
    
    for role in roles:
        role_id, role_name, description, main_skill, project, secondary_skill, similarity = role
        
        results.append({
            "role_id": role_id,
            "role_name": role_name,
            "description": description,
            "main_skill": main_skill,
            "project": project,
            "secondary_skill": secondary_skill,
            "similarity_score": round(similarity, 4)
        })
    
    # Cerrar conexión con la BD
    conn.close()
    
    # Guardar resultados en un archivo JSON
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Resultados guardados en {output_file}")
    return results

# Ejecutar búsqueda de roles de Scrum Master y guardar en JSON
scrum_master_roles = find_roles_for_scrum_master(top_n=5, output_file="scrum_master_roles.json")

# También imprimimos en consola
print(json.dumps(scrum_master_roles, indent=4, ensure_ascii=False))
