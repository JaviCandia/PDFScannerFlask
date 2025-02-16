import os
import psycopg2
import json
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

# Connect to PostgreSQL
def get_db_connection():
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

# Load candidate data from JSON
with open("app/utils/candidates.json", "r", encoding="utf-8") as file:
    candidates = json.load(file)

# Insert or update candidates in the candidate table
def insert_candidates():
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()

    query_insert_candidate = """
    INSERT INTO candidate (
        name, phone, email, state, city, english_level, education, years_experience, summary,
        companies, level, skills, main_skills, certs, previous_roles, resume_type,
        rehire, cl, current_project, roll_on_date, roll_off_date, embedding
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (email) DO UPDATE 
    SET 
        summary = EXCLUDED.summary,
        years_experience = EXCLUDED.years_experience,
        skills = EXCLUDED.skills,
        main_skills = EXCLUDED.main_skills,
        certs = EXCLUDED.certs,
        previous_roles = EXCLUDED.previous_roles,
        embedding = EXCLUDED.embedding;
    """

    for candidate in candidates:
        # Generate embedding based on summary and skills
        skills_text = ", ".join(candidate["skills"]) if candidate["skills"] else "No skills provided"
        text_to_embed = f"{candidate['summary']} Skills: {skills_text}"
        embedding = model.encode(text_to_embed).tolist()

        # Generate Reference Embeddings for Skills in PostgreSQL
        embedding_str = "[" + ", ".join(map(str, embedding)) + "]"

        # Insert candidate into the database
        cursor.execute(query_insert_candidate, (
            candidate["name"], candidate["phone"], candidate["email"], candidate["state"], candidate["city"],
            candidate["english_level"], candidate["education"], candidate["years_experience"], candidate["summary"],
            candidate["companies"], candidate["level"], candidate["skills"], candidate["main_skills"],
            candidate["certs"], candidate["previous_roles"], candidate["resume_type"], candidate["rehire"],
            candidate["cl"], candidate["current_project"], candidate["roll_on_date"], candidate["roll_off_date"],
            embedding
        ))

        # Search for similar roles in the roles table
        query_search_roles = """
        SELECT role_id, role_name, project, description, main_skill, secondary_skill, location, contact, embedding <=> %s::vector AS similarity, level
        FROM roles
        WHERE role_name ILIKE %s OR main_skill ILIKE %s OR secondary_skill ILIKE %s
        ORDER BY similarity
        LIMIT 5;
        """

        # Search for the top 5 most similar roles using embeddings
        main_skill_filter = "%" + skills_text.split(",")[0] + "%" if skills_text else "%NoSkills%"
        cursor.execute(query_search_roles, (embedding_str, main_skill_filter, main_skill_filter, main_skill_filter))
        similar_roles = cursor.fetchall()

        print(f"\n Candidate {candidate['name']},\n summary: {candidate['summary']} \n skills: {candidate['skills']} \n \n inserted and role comparison completed. \n")
        for role in similar_roles:
            print(f"  ID: {role[0]}, Role: {role[1]}, Project: {role[2]}, Level: {role[9]}, Similarity: {role[8]:.4f}")

    # Save changes
    conn.commit()
    print(f" {len(candidates)} candidates inserted/updated successfully.")

    # Close connection
    cursor.close()
    conn.close()

# Execute the process
insert_candidates()
