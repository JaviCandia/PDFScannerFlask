import os
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Verify that environment variables are set
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    raise ValueError("ERROR: Faltan variables de entorno. Verifica el archivo .env")

# Load the embedding model
MODEL_NAME = "models/all-mpnet-base-v2"
model = SentenceTransformer(MODEL_NAME)

def get_db_connection():
    """Establishes a connection with the database."""
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
        print(f"Error connecting to the database: {e}")
        return None

def insert_roles_to_db(roles_list):
    """Inserts or updates roles in the database."""
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
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()

    for role in roles_list:
        try:
            text_to_embed = f"{role.get('roleName', '')} - {role.get('description', '')} - Skills: {role.get('mainSkill', '')} {role.get('secondarySkill', '')}"
            embedding = model.encode(text_to_embed).tolist()

            cursor.execute(query, (
                role.get("roleId"), role.get("roleName"), role.get("project"), role.get("description"),
                role.get("industry"), role.get("location"), role.get("locationType"), role.get("level"),
                role.get("level2"), role.get("mainSkill"), role.get("secondarySkill"), role.get("contact"),
                role.get("startDate"), role.get("endDate"), role.get("capability"),
                role.get("roleType"), role.get("roleStatus"), role.get("roleCreateDate"), role.get("opportunity_type"), embedding
            ))
            print(f"** Role {role.get('roleName')} inserted/updated successfully.")
        except Exception as e:
            print(f"Error inserting role_id {role.get('roleId')}: {e}")

    conn.commit()
    print(f"** {len(roles_list)} roles inserted/updated successfully.")
    cursor.close()
    conn.close()