import os
import json
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from flask_cors import CORS

from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain_core.prompts import PromptTemplate

from output_parsers import feedback_parser

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:3000"}})

# Preinitialize the LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Load roles from JSON file
with open("roles-light.json", "r", encoding="utf-8") as file:
    roles = json.load(file)

def create_document(pdf):
    pdf_reader = PdfReader(pdf)
    text = "".join(page.extract_text() for page in pdf_reader.pages)

    # Filter content: remove blank lines
    text = "\n".join(line for line in text.split("\n") if line.strip())

    # Create a Document instance with the full text
    document = Document(page_content=text, metadata={})
    return [document]

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "cv" not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400

    pdf_file = request.files["cv"]
    documents = create_document(pdf_file)

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

                3. *List the companies where the candidate has worked for*
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

        res_dict = res.to_dict()

        return jsonify(res_dict)

if __name__ == "__main__":
    app.run(port=5000)