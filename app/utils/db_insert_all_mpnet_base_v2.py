import os
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

#  Cargar variables de entorno desde `.env`
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

#  Verificar si las variables de entorno están definidas correctamente
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    raise ValueError("ERROR: Faltan variables de entorno. Verifica el archivo .env")

#  Cargar el modelo de embeddings
model = SentenceTransformer("models/all-mpnet-base-v2")

def insert_roles_to_db(res_dict):
    """ Inserta roles en la base de datos PostgreSQL """

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
        print("Conexión exitosa a la base de datos")
    except Exception as e:
        raise RuntimeError(f"ERROR: No se pudo conectar a la base de datos: {e}")

    query = """
    INSERT INTO roles (
        role_id, role_name, project, description, industry, location, location_type,
        level, level2, main_skill, secondary_skill, contact, start_date, end_date,
        capability, roletype, rolestatus, rolecreatedate, opportunity_type, embedding
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        roletype = EXCLUDED.roletype,
        rolestatus = EXCLUDED.rolestatus,
        rolecreatedate = EXCLUDED.rolecreatedate,
        opportunity_type = EXCLUDED.opportunity_type;
    """

    for job in res_dict:
        try:
            text_to_embed = f"{job.get('roleName', '')} - {job.get('description', '')} - Skills: {job.get('mainSkill', '')} {job.get('secondarySkill', '')}"
            embedding = model.encode(text_to_embed).tolist()

            cursor.execute(query, (
                job.get("roleId"), job.get("roleName"), job.get("project"), job.get("description"),
                job.get("industry"), job.get("location"), job.get("locationType"), job.get("level"),
                job.get("level2"), job.get("mainSkill"), job.get("secondarySkill"), job.get("contact"),
                job.get("startDate"), job.get("endDate"), job.get("capability"),
                job.get("roleType"), job.get("roleStatus"), job.get("roleCreateDate"), job.get("opportunity_type"), embedding
            ))

        except Exception as e:
            print(f"❌ ERROR al insertar role_id {job.get('roleId')}: {e}")

    conn.commit()
    print(f"✅ {len(res_dict)} registros insertados/actualizados correctamente.")

    #  Cerrar conexión
    cursor.close()
    conn.close()
    print("✅ Conexión cerrada con éxito")
