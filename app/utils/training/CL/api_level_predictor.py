import json
import faiss
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Initialize the API
app = FastAPI(title="Level Predictor API", description="Predicts the CL level of a candidate based on their description.")

# Load the trained model
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

# Load ALL reference data from a JSON
with open("/app/utils/training/CL/level.json", "r", encoding="utf-8") as file:
    reference_data = json.load(file)

# Generate embeddings for all data
embedding_matrix = np.array([model.encode(item["description"]) for item in reference_data])

# Create the FAISS index for quick search
index = faiss.IndexFlatL2(embedding_matrix.shape[1])  # 768-dimensional vector
index.add(embedding_matrix)

# Define the request format
class DescriptionRequest(BaseModel):
    description: str

@app.post("/predict_level")
async def predict_level(request: DescriptionRequest):
    """
    Receives a description and returns the closest level (CL12 - CL7).
    """
    # Generate query embedding
    test_embedding = np.array([model.encode(request.description)])

    # Search for the closest level in FAISS
    distances, indices = index.search(test_embedding, 1)

    # Get the best result
    best_match_idx = indices[0][0]
    best_match = reference_data[best_match_idx]

    return {
        "description": request.description,
        "predicted_level": best_match["level"],
        "best_match": best_match["description"],
        "distance": float(distances[0][0])  # Convert to native float
    }

# To run the API in terminal: uvicorn app.utils.training.api_training:app --host 0.0.0.0 --port 8000
# Access in web: http://0.0.0.0:8000/docs