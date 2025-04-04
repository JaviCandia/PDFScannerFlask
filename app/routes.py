import os
import redis
from flask import request, jsonify
from dotenv import load_dotenv
from app.utils.document_processing import create_document
from app.utils.cv_processing import cache_or_generate_response
from app.utils.role_processing import process_demand_file
from app.utils.semantic_search_roles_processing import search_roles_by_embedding  # Se importa la nueva función

# Load environment variables from .env file
load_dotenv()

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=os.getenv('REDIS_PORT', 6379),
    db=os.getenv('REDIS_DB', 0)
)

def create_routes(app):
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

    @app.route('/role-semantic-search', methods=['POST'])
    def role_semantic_search():
        data = request.get_json()
        if not data or "candidate_profile" not in data:
            return jsonify({"error": "Missing 'candidate_profile' in request"}), 400

        candidate_profile = data["candidate_profile"]
        use_keybert = data.get("use_keybert", False)

        roles = search_roles_by_embedding(candidate_profile, use_keybert)

        status_msg = f"200, {len(roles)} roles found" if roles else "200, no roles found"
        return jsonify({"status": status_msg, "roles": roles})
