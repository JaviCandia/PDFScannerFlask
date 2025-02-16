import openai
import os
import psycopg2
import json

# Configurar API Key de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")  # Asegúrate de definirla antes de ejecutar

# Nueva función para generar embeddings con OpenAI (versión 1.0+)
def generate_embedding(text):
    client = openai.OpenAI()  # Crear cliente compatible con la nueva API
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding  # Nueva forma de acceder a los embeddings

# Prueba generando un embedding
embedding = generate_embedding("Ejemplo de texto")
print(f"Tamaño del vector generado: {len(embedding)}")  # Debería imprimir 1536


# Configurar conexión a PostgreSQL
conn = psycopg2.connect(
    dbname="vector_db",
    user="postgres",
    password="CHOCO.com1",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Cargar datos desde un archivo JSON
with open("/Users/julio.c.gomez.valdez/Documents/Demanda/demand_output.json", "r", encoding="utf-8") as file:
    data_list = json.load(file)  # El archivo debe contener un array de objetos JSON

# Query de inserción
query = """
INSERT INTO roles (
    role_id, role_name, project, description, industry, location, location_type,
    level, level2, main_skill, secondary_skill, contact, start_date, end_date, capability, embedding
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (role_id) DO NOTHING;;
"""

# Procesar todos los datos del JSON
values = []
for data in data_list:
    # Asegurar que "description" esté presente
    description = data.get("description", "No description available")
    
    # Generar embedding con OpenAI
    embedding = generate_embedding(description)

    # Agregar a la lista de valores
    values.append((
        data.get("roleId"), data.get("roleName"), data.get("project"), description,
        data.get("industry"), data.get("location"), data.get("locationType"), data.get("level"),
        data.get("level2"), data.get("mainSkill"), data.get("secondarySkill"), data.get("contact"),
        data.get("startDate"), data.get("endDate"), data.get("capability"), embedding
    ))

# Inserción en lotes para mejor rendimiento
if values:
    cursor.executemany(query, values)
    conn.commit()
    print(f"Se insertaron {len(values)} registros correctamente.")
else:
    print("No se insertaron registros debido a datos faltantes.")

# Cerrar conexión
cursor.close()
conn.close()
