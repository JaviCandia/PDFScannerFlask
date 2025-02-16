import psycopg2
from sentence_transformers import SentenceTransformer
from tabulate import tabulate  #  Para mejorar la visualización :)

# Cargar el modelo local
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

# Conectar a PostgreSQL
conn = psycopg2.connect(
    dbname="vector_db", 
    user="postgres", 
    password="CHOCO.com1", 
    host="localhost", 
    port="5432"
)
cursor = conn.cursor()

# Perfil del candidato
candidate_profile = "Senior Frontend Developer with 5 years of experience in React, JavaScript, and Agile methodologies."

# Generar embedding del candidato
embedding_candidato = model.encode(candidate_profile).tolist()

# Convertir el embedding a un string compatible con PostgreSQL
embedding_str = "[" + ", ".join(map(str, embedding_candidato)) + "]"

# Ejecutar la consulta con el embedding correctamente formateado
cursor.execute("""
    SELECT role_id,role_name, project, description, main_skill, secondary_skill, location, embedding <=> %s::vector AS similarity
    FROM roles
    WHERE role_name ILIKE %s OR main_skill ILIKE %s OR secondary_skill ILIKE %s
    ORDER BY similarity
    LIMIT 5;
""", (embedding_str, "%React%", "%React%", "%React%"))

# Obtener los resultados
resultados = cursor.fetchall()

# Verificar si hay resultados
if not resultados:
    print(" No se encontraron posiciones de React en la base de datos.")
else:
    # Convertir resultados en una tabla más legible
    headers = ["role_id","Puesto", "Proyecto", "Ubicación", "Descripción", "Habilidad Principal", "Habilidad Secundaria", "Similitud"]
    table_data = [
        [role_id,role_name, project, location, description[:100] + "...", main_skill, secondary_skill, round(similarity, 4)]
        for role_id, role_name, project, description, main_skill, secondary_skill, location, similarity in resultados
    ]

    print("\n **Resultados de búsqueda para posiciones de React:**\n")
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

# Cerrar conexión
cursor.close()
conn.close()
