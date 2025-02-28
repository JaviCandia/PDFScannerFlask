import os
import json
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from tabulate import tabulate
import spacy
from keybert import KeyBERT
from spacy.symbols import ORTH
from dotenv import load_dotenv

# --------------------------
# 1️⃣ Cargar lista de tecnologías desde archivo JSON
# --------------------------
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

# --------------------------
# 2️⃣ Cargar modelo de embeddings
# --------------------------
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

# --------------------------
# 3️⃣ Cargar modelos NLP (spaCy y KeyBERT)
# --------------------------
nlp = spacy.load("en_core_web_sm")

# 📌 Solución para reconocer ".NET" correctamente
nlp.tokenizer.add_special_case(".NET", [{ORTH: ".NET"}])

# 📌 Modelo de KeyBERT optimizado
kw_model = KeyBERT(model="paraphrase-MiniLM-L6-v2")

# --------------------------
# 4️⃣ Cargar variables de entorno desde `.env`
# --------------------------
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Configuración de la conexión a PostgreSQL
db_config = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT
}

# --------------------------
# 5️⃣ Función para extraer keywords con spaCy y filtrar tecnologías
# --------------------------
def extract_keywords_spacy(text, num_keywords=10):
    doc = nlp(text)
    keywords = set()

    for token in doc:
        if token.text.lower() in IT_TECHNOLOGIES:  # Buscar directamente en IT_TECHNOLOGIES
            keywords.add(token.text.lower())

    return list(keywords)[:num_keywords]

# --------------------------
# 6️⃣ Función para extraer keywords con KeyBERT y filtrar tecnologías
# --------------------------
def extract_keywords_bert(text, num_keywords=10):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')

    # 📌 Convertir keywords extraídas a minúsculas y filtrarlas con IT_TECHNOLOGIES
    filtered_keywords = [kw[0].lower() for kw in keywords if kw[0].lower() in IT_TECHNOLOGIES]

    return filtered_keywords[:num_keywords]

# --------------------------
# 7️⃣ Definir el perfil del candidato
# --------------------------
candidate_profile = """
Test Engineer Senior Analyst with 15 years of experience in Quality Engineering, specializing in Functional Testing, Automation Testing, and Mobile Testing.
"""

# --------------------------
# 8️⃣ Extraer keywords dinámicamente (elige entre spaCy o KeyBERT)
# --------------------------
use_keybert = True  # Cambia a False para usar spaCy en lugar de KeyBERT

if use_keybert:
    dynamic_keywords = extract_keywords_bert(candidate_profile)
else:
    dynamic_keywords = extract_keywords_spacy(candidate_profile)

search_terms = ["%" + keyword + "%" for keyword in dynamic_keywords]

# 📌 Verificar las palabras clave extraídas
print("🔍 Keywords extraídas:", dynamic_keywords)

# --------------------------
# 9️⃣ Generar embedding del candidato
# --------------------------
embedding_candidato = model.encode(candidate_profile)
embedding_candidato = embedding_candidato / np.linalg.norm(embedding_candidato)  # Normalización

# 📌 Convertir embedding a formato compatible con PostgreSQL
embedding_str = "[" + ", ".join(map(str, embedding_candidato)) + "]"

# --------------------------
# 🔟 Determinar si se usa búsqueda con keywords o semántica
# --------------------------
if dynamic_keywords:  # 📌 Si se encontraron palabras clave, usar `ILIKE`
    query = """
        SELECT role_id, role_name, project, location, description, main_skill, secondary_skill, 
               embedding <=> %s::vector AS similarity
        FROM roles
        WHERE (
            role_name ILIKE ANY(%s) 
            OR main_skill ILIKE ANY(%s) 
            OR secondary_skill ILIKE ANY(%s) 
            OR description ILIKE ANY(%s)
        )
        ORDER BY similarity ASC
        LIMIT 5;
    """
    params = (embedding_str, search_terms, search_terms, search_terms, search_terms)

else:  # 📌 Si no se encontraron keywords, usar búsqueda semántica con embeddings
    print("🔍 No se encontraron palabras clave, ejecutando búsqueda semántica...")
    
    query = """
        SELECT role_id, role_name, project, location, description, main_skill, unnest(string_to_array(secondary_skill, '|')) AS secondary_skill, 
               embedding <=> %s::vector AS similarity
        FROM roles
        ORDER BY similarity ASC
        LIMIT 10;
    """
    params = (embedding_str,)
    


# --------------------------
# 🔟 Conectar a PostgreSQL y ejecutar la consulta optimizada
# --------------------------
with psycopg2.connect(**db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        resultados = cursor.fetchall()

# --------------------------
# 1️⃣1️⃣ Mostrar resultados en tabla
# --------------------------
for row in resultados:
    print(f"🔍 Similaridad: {row[-1]} - Role: {row[1]}")

if resultados:
    headers = ["role_id", "Puesto", "Proyecto", "Ubicación", "Descripción", "Habilidad Principal", "Habilidad Secundaria", "Similitud"]
    table_data = [
        [role_id, role_name, project, location, description[:120] + "...", main_skill, secondary_skill, round(similarity, 4)]
        for role_id, role_name, project, location, description, main_skill, secondary_skill, similarity in resultados
    ]

    print("\n **Resultados de búsqueda:**\n")
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
else:
    print("❌ No se encontraron posiciones relevantes en la base de datos.")
