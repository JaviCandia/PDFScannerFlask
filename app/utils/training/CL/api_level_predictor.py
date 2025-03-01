import json
import faiss
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

#  Inicializar la API
app = FastAPI(title="Level Predictor API", description="Predice el nivel CL de un candidato basado en su descripción.")

#  Cargar el modelo entrenado
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

#  Cargar TODOS los datos de referencia desde un JSON
with open("/app/utils/training/CL/level.json", "r", encoding="utf-8") as file:
    reference_data = json.load(file)

#  Generar embeddings para todos los datos
embedding_matrix = np.array([model.encode(item["description"]) for item in reference_data])

#  Crear el índice FAISS para búsqueda rápida
index = faiss.IndexFlatL2(embedding_matrix.shape[1])  # Vector de 768 dimensiones
index.add(embedding_matrix)

#  Definir el formato de la solicitud
class DescriptionRequest(BaseModel):
    description: str

@app.post("/predict_level")
async def predict_level(request: DescriptionRequest):
    """
     Recibe una descripción y devuelve el nivel más cercano (CL12 - CL7).
    """
    # Generar embedding de la consulta
    test_embedding = np.array([model.encode(request.description)])

    # Buscar el nivel más cercano en FAISS
    distances, indices = index.search(test_embedding, 1)

    # Obtener el mejor resultado
    best_match_idx = indices[0][0]
    best_match = reference_data[best_match_idx]

    return {
        "description": request.description,
        "predicted_level": best_match["level"],
        "best_match": best_match["description"],
        "distance": float(distances[0][0])  # 🔥 Conversión a `float` nativo
    }

# ejecutar la api en terminal ejecutar: uvicorn app.utils.training.api_training:app --host 0.0.0.0 --port 8000
# ejecutat en web http://0.0.0.0:8000/docs