import json
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Load the EXISTING model we want to fine-tune
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

# Load training data from JSON
file_path = "app/utils/training/CL/level.json"
with open(file_path, "r", encoding="utf-8") as file:
    training_data = json.load(file)

# Map levels to numeric values
level_mapping = {
    "CL12": 0, "CL11": 1, "CL10": 2, "CL9": 3, "CL8": 4, "CL7": 5
}

# Create training examples with pairs of texts
train_examples = []
for i, data in enumerate(training_data):
    for j, other in enumerate(training_data):
        if i != j:  # Avoid comparing a text with itself
            level_1 = level_mapping[data["level"]]  # Convert level to number
            level_2 = level_mapping[other["level"]]  # Convert level to number
            
            # If the levels are close, assign a higher similarity
            similarity_score = 1.0 if abs(level_1 - level_2) <= 1 else 0.0
            
            train_examples.append(
                InputExample(texts=[data["description"], other["description"]], label=float(similarity_score))
            )

# Verify that the examples are generated correctly
print("Example of train_examples after correction:")
for example in train_examples[:10]:  # Only show the first 10 examples
    print(f"Texts: {example.texts}, Label: {example.label}")

# Create DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)

# Define the loss function (CosineSimilarityLoss)
train_loss = losses.CosineSimilarityLoss(model)

# Set the number of epochs and `warmup_steps`
num_epochs = 5
warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)

# Run the fine-tuning
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=num_epochs,
    warmup_steps=warmup_steps
)

# Save the fine-tuned model in the same folder
model.save(model_path)
print("Fine-tuned `all-mpnet-base-v2` model successfully saved in models/all-mpnet-base-v2")