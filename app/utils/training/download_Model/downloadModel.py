from sentence_transformers import SentenceTransformer

# Download the model from Hugging Face
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Save the model in a local folder for offline use
model_path = "models/all-mpnet-base-v2"
model.save(model_path)

print(f"Model saved in: {model_path}")