import os
import redis
from flask import request, jsonify
from dotenv import load_dotenv
from app.utils.pdf_processing import create_document
from app.utils.cv_processing import cache_or_generate_response
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=os.getenv('REDIS_PORT', 6379),
    db=os.getenv('REDIS_DB', 0)
)

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Connect to the existing index
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pc.Index(index_name)

def create_routes(app):
    @app.route("/single-cv", methods=["POST"])
    def upload_single_cv():
        if "cv" not in request.files:
            return jsonify({"error": "No PDF uploaded"}), 400

        pdf_file = request.files["cv"]
        documents = create_document(pdf_file)[0]

        response = cache_or_generate_response(documents, redis_client, index)
        return jsonify(response)

    @app.route("/multiple-cvs", methods=["POST"])
    def upload_multiple_cvs():
        if "cvs" not in request.files:
            return jsonify({"error": "No PDFs uploaded"}), 400

        cvs_files = request.files.getlist("cvs")
        results = []
        for pdf_file in cvs_files:
            documents = create_document(pdf_file)[0]
            response = cache_or_generate_response(documents, redis_client, index)
            results.append(response)

        return jsonify(results)
