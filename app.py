import os
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from app.routes import create_routes

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/single-cv": {"origins": "http://localhost:3000"},
        r"/multiple-cvs": {"origins": "http://localhost:3000"},
    },
)

# Register routes
create_routes(app)

if __name__ == "__main__":
    app.run(port=5000, debug=True)