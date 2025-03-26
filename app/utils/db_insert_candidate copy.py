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

# Load the embedding model
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

def get_db_connection():
    """Establece una conexión con la base de datos."""
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
        print(f" Error connecting to the database: {e}")
        return None

def insert_candidates_to_db(candidates):
    """ Inserta o actualiza candidatos en la base de datos """


    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()

    query_insert_candidate = """
    INSERT INTO candidate (
        name, phone, email, state, city, english_level, education, years_experience, summary,
        companies, level, skills, main_skills, certs, previous_roles, resume_type,
        rehire, cl, current_project, roll_on_date, roll_off_date, candidate_type, recruiter, capability, status, embedding
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (email) DO UPDATE 
    SET 
        name = EXCLUDED.name,
        phone = EXCLUDED.phone,
        state = EXCLUDED.state,
        city = EXCLUDED.city,
        english_level = EXCLUDED.english_level,
        education = EXCLUDED.education,
        years_experience = EXCLUDED.years_experience,
        summary = EXCLUDED.summary,
        companies = EXCLUDED.companies,
        level = EXCLUDED.level,
        skills = EXCLUDED.skills,
        main_skills = EXCLUDED.main_skills,
        certs = EXCLUDED.certs,
        previous_roles = EXCLUDED.previous_roles,
        resume_type = EXCLUDED.resume_type,
        rehire = EXCLUDED.rehire,
        cl = EXCLUDED.cl,
        current_project = EXCLUDED.current_project,
        roll_on_date = EXCLUDED.roll_on_date,
        roll_off_date = EXCLUDED.roll_off_date,
        candidate_type = EXCLUDED.candidate_type,
        recruiter = EXCLUDED.recruiter,
        capability = EXCLUDED.capability,
        status = EXCLUDED.status,
        embedding = EXCLUDED.embedding;
    """

    if not isinstance(candidates, list):  # Validar que sea una lista
        print("⚠️ Warning: 'candidates' no es una lista. No se insertarán datos.")
        return

    for candidate in candidates:
        try:
            # Generate embedding based on summary and skills
            skills_text = ", ".join(candidate.get("skills", [])) if candidate.get("skills") else "No skills provided"
            text_to_embed = f"{candidate.get('summary', '')} Skills: {skills_text}"
            embedding = model.encode(text_to_embed).tolist()

            cursor.execute(query_insert_candidate, (
                candidate.get("name"), candidate.get("phone"), candidate.get("email"), candidate.get("state"), candidate.get("city"),
                candidate.get("english_level"), candidate.get("education"), candidate.get("years_experience"), candidate.get("summary"),
                candidate.get("companies"), candidate.get("level"), candidate.get("skills"), candidate.get("main_skills"),
                candidate.get("certs"), candidate.get("previous_roles"), candidate.get("resume_type"), candidate.get("rehire"),
                candidate.get("cl"), candidate.get("current_project"), candidate.get("roll_on_date"), candidate.get("roll_off_date"),
                candidate.get("candidate_type"), candidate.get("recruiter"), candidate.get("capability"), candidate.get("status"), embedding
            ))

            print(f"** Candidate {candidate.get('name')} inserted/updated successfully.")

        except Exception as e:
            print(f" Error inserting candidate {candidate.get('name')}: {e}")

    # Save changes
    conn.commit()
    print(f"** {len(candidates)} candidates inserted/updated successfully.")

    # Close connection
    cursor.close()
    conn.close()
