import psycopg2
from sentence_transformers import SentenceTransformer
from tabulate import tabulate  # Para mejorar la visualización :)

# Cargar el modelo local
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

# Configuración de la conexión a PostgreSQL
db_config = {
    "dbname": "vector_db",
    "user": "postgres",
    "password": "",  # Reemplazar con credenciales seguras
    "host": "localhost",
    "port": "5432"
}

# Perfil del candidato
candidate_profile = "Big Data with more than 5 years of experience in Agile methodologies, team leadership, and project delivery."

# Generar embedding del candidato
embedding_candidato = model.encode(candidate_profile).tolist()

# Convertir el embedding a un formato compatible con PostgreSQL
embedding_str = "[" + ", ".join(map(str, embedding_candidato)) + "]"

# Conectar a PostgreSQL y ejecutar la consulta
with psycopg2.connect(**db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT role_id, role_name, project, location, description, main_skill, secondary_skill, 
                   embedding <=> %s::vector AS similarity
            FROM roles
            WHERE role_name ILIKE %s OR main_skill ILIKE %s OR secondary_skill ILIKE %s OR description ILIKE %s
            ORDER BY similarity
            LIMIT 5;
        """, (embedding_str, "%Big Data%", "%%Big Data%", "%%Big Data%", "%%Big Data%"))

        # Obtener los resultados
        resultados = cursor.fetchall()

# Verificar si hay resultados
table_data = []
if resultados:
    headers = ["role_id", "Puesto", "Proyecto", "Ubicación", "Descripción", "Habilidad Principal", "Habilidad Secundaria", "Similitud"]
    table_data = [
        [role_id, role_name, project, location, description[:120] + "...", main_skill, secondary_skill, round(similarity, 4)]
        for role_id, role_name, project, location, description, main_skill, secondary_skill, similarity in resultados
    ]

    print("\n **Resultados de búsqueda para posiciones de React:**\n")
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
else:
    print("No se encontraron posiciones de React en la base de datos.")


# Cerrar conexión
cursor.close()
conn.close()
