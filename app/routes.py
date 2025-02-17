import os
import redis
from flask import request, jsonify
from dotenv import load_dotenv
from app.utils.pdf_processing import create_document
from app.utils.cv_processing import cache_or_generate_response

# Load environment variables from .env file
load_dotenv()

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=os.getenv('REDIS_PORT', 6379),
    db=os.getenv('REDIS_DB', 0)
)

# Initialize Azure AI Search client
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
azure_search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
azure_search_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
search_client = SearchClient(
    endpoint=azure_search_endpoint,
    index_name=azure_search_index_name,
    credential=AzureKeyCredential(azure_search_api_key)
)

def create_routes(app):
    @app.route("/single-cv", methods=["POST"])
    def upload_single_cv():
        if "cv" not in request.files:
            return jsonify({"error": "No PDF uploaded"}), 400

        pdf_file = request.files["cv"]
        documents = create_document(pdf_file)[0]

        # Pass the search_client to cv_processing
        response = cache_or_generate_response(documents, redis_client, search_client)
        return jsonify(response)

    @app.route("/multiple-cvs", methods=["POST"])
    def upload_multiple_cvs():
        if "cvs" not in request.files:
            return jsonify({"error": "No PDFs uploaded"}), 400

        cvs_files = request.files.getlist("cvs")
        results = []
        for pdf_file in cvs_files:
            documents = create_document(pdf_file)[0]
            response = cache_or_generate_response(documents, redis_client, search_client)
            results.append(response)

        return jsonify(results)

# TODO: Crear un endpoint para actualizar data (no importa que esté cacheado en redis)