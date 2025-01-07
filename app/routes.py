from flask import request, jsonify
import json
import os
import redis
import hashlib
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.utils.pdf_processing import create_document
from app.utils.feedback_parser import feedback_parser

# Load environment variables from .env file
load_dotenv()

# Preinitialize the LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Load roles from JSON file
with open("roles-light.json", "r", encoding="utf-8") as file:
    roles = json.load(file)

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=os.getenv('REDIS_PORT', 6379),
    db=os.getenv('REDIS_DB', 0)
)

def create_routes(app):
    @app.route("/upload", methods=["POST"])
    def upload_pdf():
        if "cv" not in request.files:
            return jsonify({"error": "No PDF uploaded"}), 400

        pdf_file = request.files["cv"]
        documents = create_document(pdf_file)

        # Generate a unique key based on the content of the PDF
        pdf_content_key = "pdf_" + hashlib.md5(documents[0].page_content.encode()).hexdigest()

        # Check if the response for this PDF is already cached in Redis
        cached_response = redis_client.get(pdf_content_key)
        if cached_response:
            print("Se regresó data de Redis")
            return jsonify(json.loads(cached_response))

        if roles:
            os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

            new_match_prompt = PromptTemplate(
                input_variables=["documents", "roles"],
                partial_variables={
                    "format_instructions": feedback_parser.get_format_instructions
                },
                template="""
                    Based on the provided CV information: {documents}
                    and the following roles: {roles},

                    Please perform the following tasks:

                    1. **Understand the Candidate CV**
                    - Give me the name of the candidate.
                    - Determine the candidate's level based on their overall experience: Junior, Mid or Senior.

                    2. **List the Candidate's Main Skills and Experiences**:
                    - Identify and enumerate the 5 primary skills / technologies.

                    3. **List the companies where the candidate has worked for**
                    - Identify all the companies where the candidate has worked.

                    4. **Role Match**:
                    - For each role, provide:
                        - The role name.
                        - A short summary of the role description, 3 lines maximum.
                        - Identify a list of relevant skills from candidate's CV that directly fit the role (5 maximum).
                        - If there are no relevant skills, indicate with a single bullet:
                            * There are no skills that fit the job position.
                        - A match score from 0 to 100 indicating how well the candidate fits the role. 0 If there are no skills that fit.
                        - Start date of the role.

                    \n{format_instructions}
                """,
            )

            chain = new_match_prompt | llm | feedback_parser
            res = chain.invoke(input={"documents": documents, "roles": roles})

            print("Se hizo el llamado a OpenAI")
            res_dict = res.to_dict()

            # Cache the response in Redis with an expiration time (e.g., 30 minutes)
            expiration_time = 15  # 1800 seconds = 30 minutes
            redis_client.setex(pdf_content_key, expiration_time, json.dumps(res_dict))

            return jsonify(res_dict)