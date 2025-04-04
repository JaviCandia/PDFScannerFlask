import os
import json
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
from keybert import KeyBERT
from spacy.symbols import ORTH
from dotenv import load_dotenv

# Loading technologies from JSON
def load_technologies_from_json(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            return set(map(str.lower, data.get("technologies", [])))  # Convertir a minúsculas
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error al cargar el JSON: {e}")
        return set()

TECHNOLOGIES_JSON_PATH = "app/utils/technologies.json"
IT_TECHNOLOGIES = load_technologies_from_json(TECHNOLOGIES_JSON_PATH)

# Loading embedding models
model_path = "models/all-mpnet-base-v2" 
model = SentenceTransformer(model_path)

# Loading NLP models (spaCy and KeyBERT)
nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT(model="paraphrase-MiniLM-L6-v2")

# Adding "".NET" special case
nlp.tokenizer.add_special_case(".NET", [{ORTH: ".NET"}])

# Loading .env variables
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

db_config = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT
}


def extract_keywords_spacy(text, num_keywords=10):
    doc = nlp(text)
    keywords = set()

    for token in doc:
        if token.text.lower() in IT_TECHNOLOGIES:
            keywords.add(token.text.lower())

    return list(keywords)[:num_keywords]

def extract_keywords_bert(text, num_keywords=10):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')

    filtered_keywords = [kw[0].lower() for kw in keywords if kw[0].lower() in IT_TECHNOLOGIES]

    return filtered_keywords[:num_keywords]

def search_roles_by_embedding(candidate_profile, use_keybert=False):
    # Normalize the candidate profile text
    candidate_profile_cleaned = candidate_profile.lower().replace("-", " ")

    # Generate embedding of the candidate profile
    embedding_candidato = model.encode(candidate_profile_cleaned)
    embedding_candidato = embedding_candidato / np.linalg.norm(embedding_candidato)  # Normalización

   # Convert embedding to PostgreSQL compatible format
    embedding_str = "[" + ", ".join(map(str, embedding_candidato)) + "]"

    if use_keybert:
        dynamic_keywords = extract_keywords_bert(candidate_profile)
    else:
        dynamic_keywords = extract_keywords_spacy(candidate_profile)

    search_terms = ["%" + keyword + "%" for keyword in dynamic_keywords]

    if dynamic_keywords:
        query = """
            SELECT role_name, secondary_skill, embedding <=> %s::vector AS similarity
            FROM roles
            WHERE (
                role_name ILIKE ANY(%s) 
                OR main_skill ILIKE ANY(%s) 
                OR secondary_skill ILIKE ANY(%s) 
                OR description ILIKE ANY(%s)
            )
            ORDER BY similarity ASC
            LIMIT 10;
        """
        params = (embedding_str, search_terms, search_terms, search_terms, search_terms)
    else:
        query = """
            SELECT role_name, secondary_skill, embedding <=> %s::vector AS similarity
            FROM roles
            ORDER BY similarity ASC
            LIMIT 10;
        """
        params = (embedding_str,)

    # Execute query in postgres
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

    return [
        {
            "role_name": role_name, 
            "secondary_skill": secondary_skill, 
            "similarity": round(similarity, 4)
        }
        for role_name, secondary_skill, similarity in results
    ]
