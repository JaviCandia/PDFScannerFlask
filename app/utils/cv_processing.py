import json
import hashlib
import base64
import threading
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.utils.feedback_parser import feedback_parser
from app.utils.templates import MATCH_TEMPLATE
from app.utils.db_insert_candidate import insert_candidates_to_db

# Preinitialize the LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Function to encode a string in URL-safe Base64 without padding
def safe_base64_encode(value):
    encoded = base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")
    return encoded

# Top-level function to process and upload candidate data to the DB
def process_and_upload_to_db(res_dict):
    try:
        print("Processing candidate and inserting into DB...")
        # Ensure that res_dict is a list
        if isinstance(res_dict, dict):
            candidate_list = [res_dict]
        else:
            candidate_list = res_dict
        # Call the reusable insertion function
        insert_candidates_to_db(candidate_list)
        print("Candidate insertion completed.")
    except Exception as e:
        print(f"Error uploading candidate to DB: {e}")

def cache_or_generate_response(documents, redis_client):
    pdf_content_key = "pdf_" + hashlib.md5(documents.page_content.encode()).hexdigest()
    cached_response = redis_client.get(pdf_content_key)

    # Return data from Redis if exists
    if cached_response:
        return json.loads(cached_response)

    # Generate a new response using OpenAI
    new_match_prompt = PromptTemplate(
        input_variables=["documents"],
        partial_variables={
            "format_instructions": feedback_parser.get_format_instructions
        },
        template=MATCH_TEMPLATE,
    )

    chain = new_match_prompt | llm | feedback_parser
    res = chain.invoke(input={"documents": documents})
    res_dict = res.to_dict()

    # Start a background thread to insert candidate data into the DB
    threading.Thread(target=process_and_upload_to_db, args=(res_dict,)).start()

    # Store the response in Redis with an expiration time
    expiration_time = 180  # 180 seconds for testing
    redis_client.setex(pdf_content_key, expiration_time, json.dumps(res_dict))

    # Return a simple status response
    return {"status": "Candidate processed"}
