import os
import redis
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import json
from dotenv import load_dotenv
from app.utils.pdf_processing import create_document
from app.utils.cv_processing import cache_or_generate_response
from app.utils.generateJSON_util import convert_values, read_sheet_and_convert, selected_columns, column_mapping
from app.utils.masking_util import mask_data

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

        # Check if masked_data.json exists
        if not os.path.exists('masked_data.json'):
            return jsonify({"error": "Roles data not available. Please generate the roles data first."}), 400

        pdf_file = request.files["cv"]
        documents = create_document(pdf_file)[0]

        # Pass the search_client to cv_processing
        response = cache_or_generate_response(documents, redis_client, search_client)
        return jsonify(response)

    @app.route("/multiple-cvs", methods=["POST"])
    def upload_multiple_cvs():
        if "cvs" not in request.files:
            return jsonify({"error": "No PDFs uploaded"}), 400

        # Check if masked_data.json exists
        if not os.path.exists('masked_data.json'):
            return jsonify({"error": "Roles data not available. Please generate the roles data first."}), 400

        cvs_files = request.files.getlist("cvs")
        results = []
        for pdf_file in cvs_files:
            documents = create_document(pdf_file)[0]
            response = cache_or_generate_response(documents, redis_client, search_client)
            results.append(response)

        return jsonify(results)

    @app.route('/process-demand', methods=['POST'])
    def process_demand():
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        filename = secure_filename(file.filename)

        # Read the XLSB file and convert to JSON
        data_database = read_sheet_and_convert(file, "Database", selected_columns, column_mapping, "Database")
        data_1k = read_sheet_and_convert(file, "1k", selected_columns, column_mapping, "1k")
        final_data = data_database + data_1k

        # Convert to JSON
        json_data = final_data

        # Save output.json to return to front-end using jsonify
        output_json = jsonify(json_data)

        # Mask data and save masked_data.json in the backend root
        masked_data = mask_data(json_data)
        masked_json = json.dumps(masked_data, ensure_ascii=False, indent=4)
        masked_json_path = 'masked_data.json'
        with open(masked_json_path, 'w', encoding='utf-8') as f:
            f.write(masked_json)

        # Return output.json as response to front-end
        return output_json