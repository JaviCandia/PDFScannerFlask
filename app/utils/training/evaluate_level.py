import numpy as np
from sentence_transformers import SentenceTransformer, util

#  Cargar el modelo entrenado
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

#  Ejemplos representativos por nivel (CL12 - CL7)
reference_levels = {
    "CL12": "Junior Developer with 1 year of experience in React and JavaScript.",
    "CL11": "Fullstack Engineer with 3 years of experience in React and Node.js.",
    "CL10": "Backend Developer with 5 years of experience in Python and Django.",
    "CL9": "Software Engineer with 7 years of experience in microservices and AWS.",
    "CL8": "Tech Lead with 10 years of experience in distributed architectures.",
    "CL7": "Engineering Manager with 15 years of experience leading agile teams."
}

#  Generar embeddings de referencia
reference_embeddings = {level: model.encode(desc) for level, desc in reference_levels.items()}

#  Descripción del candidato a evaluar
test_description = "Senior Backend Developer with 8 years of experience in React."

#  Generar embedding de la consulta
test_embedding = model.encode(test_description)

#  Calcular similitudes con cada nivel
similarities = {
    level: util.cos_sim(test_embedding, emb).item()
    for level, emb in reference_embeddings.items()
}

#  Obtener el nivel más similar
predicted_level = max(similarities, key=similarities.get)

#  Mostrar resultados
print("\n Evaluación de Nivel del Candidato:")
print(f" Descripción: {test_description}")
print(" Similitudes con cada nivel:")
for level, score in similarities.items():
    print(f"   - {level}: {score:.4f}")

print(f"\n Nivel prediccion: {predicted_level}")
