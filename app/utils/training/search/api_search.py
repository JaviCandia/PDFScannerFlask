
import os
import json
import psycopg2
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Initialize FastAPI
app = FastAPI(
    title="Job Matching API with Level Prediction",
    description="Find similar job roles and predict the Level based on candidate descriptions.",
    version="1.0",
)

# Load the embedding model (for job role search)
model_roles = SentenceTransformer("models/all-mpnet-base-v2")

# Load the trained model for Levels
model_levels = SentenceTransformer("models/all-mpnet-base-v2")

# Load reference levels from level.json
with open("app/utils/training/level.json", "r", encoding="utf-8") as file:
    level_reference = json.load(file)

# Convert reference embeddings
level_embeddings = {entry["level"]: model_levels.encode(entry["description"]) for entry in level_reference}

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
        print(f"Error connecting to the database: {e}")
        return None

# Define the request format with an example for documentation
class CandidateProfile(BaseModel):
    description: str = Field(
        ...,
        title="Candidate Profile Description",
        description="A brief description of the candidate's experience and skills.",
        example="I am a frontend developer with 3 years of experience in React, Redux, and Tailwind CSS."
    )

@app.post("/search_roles_with_level", summary="Search for similar roles and predict Level")
async def search_roles_with_level(profile: CandidateProfile):
    """
    Receives a candidate description and returns:
    
    - The **most similar job roles** based on embeddings.
    - The **estimated Level** of the candidate (CL12 to CL7).
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "Could not connect to the database"}

    cursor = conn.cursor()

    # Generate candidate embedding for job role search
    embedding_roles = model_roles.encode(profile.description).tolist()
    embedding_str = "[" + ", ".join(map(str, embedding_roles)) + "]"

    # Execute the query with the embedding in PostgreSQL
    try:
        cursor.execute("""
            SELECT role_id, role_name, project, description, main_skill, secondary_skill, location, contact, embedding <=> %s::vector AS similarity, level
            FROM roles
            ORDER BY similarity
            LIMIT 5;
        """, (embedding_str,))

        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Generate embedding to predict the candidate's Level
        embedding_level = model_levels.encode(profile.description)  # Convert to matrix
        
        # Compare with reference levels and find the closest match
        predicted_level = "Unknown"
        highest_similarity = -1
        for level, ref_embedding in level_embeddings.items():
            similarity = np.dot(embedding_level, ref_embedding) / (np.linalg.norm(embedding_level) * np.linalg.norm(ref_embedding))
            if similarity > highest_similarity:
                highest_similarity = similarity
                predicted_level = level
        
        # Format the response with the most similar job roles and the estimated Level
        roles = [
            {
                "role_id": role[0],
                "role_name": role[1],
                "project": role[2],
                "description": role[3][:180] + "...",  # Limit description length
                "main_skill": role[4],
                "secondary_skill": role[5],
                "location": role[6],
                "contact": role[7],
                "similarity": float(role[8]),  # Convert to float
                "level": role[9]  # Include job role Level
            }
            for role in results
        ]

        return {
            "query": profile.description,
            "predicted_CL": predicted_level,
            "matches": roles
        }

    except Exception as e:
        return {"error": f"Error executing query: {e}"}

# Run with: uvicorn app.utils.training.api_search:app --host 0.0.0.0 --port 8000
