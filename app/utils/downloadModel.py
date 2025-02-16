from sentence_transformers import SentenceTransformer

# Descargar el modelo de Hugging Face
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Guardar el modelo en una carpeta local para usarlo sin conexión
model_path = "models/all-mpnet-base-v2"
model.save(model_path)

print(f"Modelo guardado en: {model_path}")
