import os
import psycopg2
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

#  Cargar variables de entorno desde `.env`
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
JSON_FILE_PATH = os.getenv("JSON_FILE_PATH")

#  Verificar si las variables de entorno están definidas correctamente
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, JSON_FILE_PATH]):
    raise ValueError(" ERROR: Faltan variables de entorno. Verifica el archivo .env")

#  Cargar el modelo de embeddings
model = SentenceTransformer("models/all-mpnet-base-v2")

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
    print(" Conexión exitosa a la base de datos")
except Exception as e:
    raise RuntimeError(f" ERROR: No se pudo conectar a la base de datos: {e}")

#  Cargar los roles desde el archivo JSON
try:
    with open(JSON_FILE_PATH+"demand_output.json", "r", encoding="utf-8") as file:
        job_roles = json.load(file)
    print(f" Se cargaron {len(job_roles)} registros desde el archivo JSON")
except Exception as e:
    raise RuntimeError(f" ERROR: No se pudo cargar el archivo JSON: {e}")

#  Query SQL para insertar o actualizar
query = """
INSERT INTO roles (
    role_id, role_name, project, description, industry, location, location_type,
    level, level2, main_skill, secondary_skill, contact, start_date, end_date,
    capability, opportunity_type, embedding
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (role_id) DO UPDATE 
SET embedding = EXCLUDED.embedding,
    project = EXCLUDED.project,
    description = EXCLUDED.description,
    industry = EXCLUDED.industry,
    location = EXCLUDED.location,
    location_type = EXCLUDED.location_type,
    level = EXCLUDED.level,
    level2 = EXCLUDED.level2,
    main_skill = EXCLUDED.main_skill,
    secondary_skill = EXCLUDED.secondary_skill,
    contact = EXCLUDED.contact,
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    capability = EXCLUDED.capability,
    opportunity_type = EXCLUDED.opportunity_type;
"""

#  Procesar cada rol y almacenarlo en la base de datos
for job in job_roles:
    try:
        # Generar embedding usando la descripción y habilidades
        text_to_embed = f"{job['roleName']} - {job['description']} - Skills: {job['mainSkill']} {job['secondarySkill']}"
        embedding = model.encode(text_to_embed).tolist()

        cursor.execute(query, (
            job["roleId"], job["roleName"], job["project"], job["description"], job["industry"],
            job["location"], job["locationType"], job["level"], job["level2"], job["mainSkill"],
            job["secondarySkill"], job["contact"], job["startDate"], job["endDate"],
            job["capability"], job["opportunity_type"], embedding
        ))

    except Exception as e:
        print(f" ERROR al insertar el role_id {job['roleId']}: {e}")

#  Guardar los cambios en la base de datos
conn.commit()
print(f" {len(job_roles)} registros insertados/actualizados correctamente.")

#  Cerrar conexión
cursor.close()
conn.close()
print(" Conexión cerrada con éxito")
