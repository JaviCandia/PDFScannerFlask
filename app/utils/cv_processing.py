import os
import json
import hashlib
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.utils.feedback_parser import feedback_parser
from app.utils.templates import MATCH_TEMPLATE  # Importar el template

# Preinitialize the LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Load roles from JSON file
with open("roles-light.json", "r", encoding="utf-8") as file:
    roles = json.load(file)


def generate_vector(text):
    from transformers import BertTokenizer, BertModel

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    vector = outputs.last_hidden_state[:, 0, :].squeeze().tolist()

    return vector


def cache_or_generate_response(documents, redis_client, index):
    pdf_content_key = "pdf_" + hashlib.md5(documents.page_content.encode()).hexdigest()
    cached_response = redis_client.get(pdf_content_key)

    # Return data from redis
    if cached_response:
        return json.loads(cached_response), True

    # Return data from OpenAI
    if roles:
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

        new_match_prompt = PromptTemplate(
            input_variables=["documents", "roles"],
            partial_variables={
                "format_instructions": feedback_parser.get_format_instructions
            },
            template=MATCH_TEMPLATE,
        )

        chain = new_match_prompt | llm | feedback_parser
        res = chain.invoke(input={"documents": documents, "roles": roles})

        res_dict = res.to_dict()

        expiration_time = 300  # 1800 = 30 minutes
        redis_client.setex(pdf_content_key, expiration_time, json.dumps(res_dict))

        # Vectorize the CV and store in Pinecone along with metadata
        vector = generate_vector(documents.page_content)

        metadata = {
            "candidate_name": res_dict.get("candidate_name"),
            "candidate_level": res_dict.get("candidate_level"),
            "main_skills": res_dict.get("main_skills"),
            "companies": res_dict.get("companies"),
        }

        index.upsert([(pdf_content_key, vector, metadata)])

        return res_dict

# TODO: CAMBIAR A AZURE
# TODO: Buscar los chunks, traerlos como contexto (nombre, skills, etc.), mandarle eso al LLM para que te responda en lenguaje humano.