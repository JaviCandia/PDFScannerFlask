import json
import hashlib
import base64
import threading
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.utils.feedback_parser import feedback_parser
from app.utils.templates import MATCH_TEMPLATE
from app.utils.db_insert_candidate import insert_candidates_to_db




# Preinitialize the LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Load roles from JSON file
with open("masked_data.json", "r", encoding="utf-8") as file:
    roles = json.load(file)

# Function to encode a string in URL-safe Base64 without padding
def safe_base64_encode(value):
    encoded = base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")
    return encoded

# Convert PDF to Vector
def generate_vector(text):
    from transformers import BertTokenizer, BertModel

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    vector = outputs.last_hidden_state[:, 0, :].squeeze().tolist()

    return vector

# Function to process and upload the document to Azure in a background thread
def process_and_upload_to_db(documents, res_dict, search_client):
    try:
        # Generate the vector
        #vector = generate_vector(documents.page_content)
        # Prepare the document to index
        print(" Procesando documentos y subiendo a la base de datos...")
        # Asegurar que `res_dict` es una lista
        if isinstance(res_dict, dict):  # Si es un solo candidato, conviértelo en una lista
            res_dict = [res_dict]


        # Llamar a la función de inserción reutilizable
        insert_candidates_to_db(res_dict)
       

        print(" Procesamiento completado.")
    except Exception as e:
        # Handle errors if necessary
        print(f"Error uploading to db: {e}")

def cache_or_generate_response(documents, redis_client, search_client):
    pdf_content_key = "pdf_" + hashlib.md5(documents.page_content.encode()).hexdigest()
    cached_response = redis_client.get(pdf_content_key)

    # Return data from redis (if exists)
    if cached_response:
        return json.loads(cached_response)

    # If no cached response, generate a new one using OpenAI
    if roles:
        new_match_prompt = PromptTemplate(
            input_variables=["documents", "roles"],
            partial_variables={
                "format_instructions": feedback_parser.get_format_instructions
            },
            template=MATCH_TEMPLATE,
        )

        # OpenAI Process
        chain = new_match_prompt | llm | feedback_parser
        res = chain.invoke(input={"documents": documents, "roles": roles})
        res_dict = res.to_dict()
    
        # Start a thread to process and upload the vector to db
        threading.Thread(target=process_and_upload_to_db, args=(documents, res_dict, search_client)).start()

        # Store the response in Redis with an expiration time
        expiration_time = 180  # 1800 = 30 minutes
        redis_client.setex(pdf_content_key, expiration_time, json.dumps(res_dict))



        # Return res_dict immediately
        return res_dict

# TODO: Buscar los chunks, traerlos como contexto (nombre, skills, etc.), mandarle eso al LLM para que te responda en lenguaje humano.