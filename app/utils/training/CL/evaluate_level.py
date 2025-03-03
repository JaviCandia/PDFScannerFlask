import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load the trained model
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

# Representative examples by level (CL12 - CL7)
reference_levels = {
    "CL12": "Junior Developer with 1 year of experience in React and JavaScript.",
    "CL11": "Fullstack Engineer with 3 years of experience in React and Node.js.",
    "CL10": "Backend Developer with 5 years of experience in Python and Django.",
    "CL9": "Software Engineer with 7 years of experience in microservices and AWS.",
    "CL8": "Tech Lead with 10 years of experience in distributed architectures.",
    "CL7": "Engineering Manager with 15 years of experience leading agile teams."
}

# Generate reference embeddings
reference_embeddings = {level: model.encode(desc) for level, desc in reference_levels.items()}

# Candidate description to evaluate
test_description = "Senior Backend Developer with 8 years of experience in React."

# Generate query embedding
test_embedding = model.encode(test_description)

# Calculate similarities with each level
similarities = {
    level: util.cos_sim(test_embedding, emb).item()
    for level, emb in reference_embeddings.items()
}

# Get the most similar level
predicted_level = max(similarities, key=similarities.get)

# Display results
print("\nCandidate Level Evaluation:")
print(f"Description: {test_description}")
print("Similarities with each level:")
for level, score in similarities.items():
    print(f"   - {level}: {score:.4f}")

print(f"\nPredicted Level: {predicted_level}")