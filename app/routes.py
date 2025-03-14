import os
import redis
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename
import json
from dotenv import load_dotenv
from app.utils.pdf_processing import create_document
from app.utils.cv_processing import cache_or_generate_response
from app.utils.role_processing import process_demand_file

# Load environment variables from .env file
load_dotenv()

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=os.getenv('REDIS_PORT', 6379),
    db=os.getenv('REDIS_DB', 0)
)

def create_routes(app):
    # The single-cv endpoint is commented out as it is not used.
    # @app.route("/single-cv", methods=["POST"])
    # def upload_single_cv():
    #     if "cv" not in request.files:
    #         return jsonify({"error": "No PDF uploaded"}), 400
    #
    #     if not os.path.exists('demand_output.json'):
    #         return jsonify({"error": "Roles data not available. Please generate the roles data first."}), 400
    #
    #     pdf_file = request.files["cv"]
    #     documents = create_document(pdf_file)[0]
    #     response = cache_or_generate_response(documents, redis_client)
    #     return jsonify(response)

    @app.route("/multiple-cvs", methods=["POST"])
    def upload_multiple_cvs():
        if "cvs" not in request.files:
            return jsonify({"error": "No PDFs uploaded"}), 400

        if not os.path.exists('demand_output.json'):
            return jsonify({"error": "Roles data not available. Please generate the roles data first."}), 400

        cvs_files = request.files.getlist("cvs")
        count = 0
        for pdf_file in cvs_files:
            documents = create_document(pdf_file)[0]
            cache_or_generate_response(documents, redis_client)
            count += 1
        return jsonify({"status": f"200, {count} cvs processed"})

    @app.route('/process-demand', methods=['POST'])
    def process_demand():
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        status = process_demand_file(file)
        return jsonify(status)