import json
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

#  Cargar el modelo EXISTENTE que queremos afinar
model_path = "models/all-mpnet-base-v2"
model = SentenceTransformer(model_path)

#  Cargar los datos de entrenamiento desde JSON
file_path = "app/utils/training/CL/level.json"
with open(file_path, "r", encoding="utf-8") as file:
    training_data = json.load(file)

#  Mapear niveles a valores numéricos
level_mapping = {
    "CL12": 0, "CL11": 1, "CL10": 2, "CL9": 3, "CL8": 4, "CL7": 5
}

#  Crear ejemplos de entrenamiento con pares de textos
train_examples = []
for i, data in enumerate(training_data):
    for j, other in enumerate(training_data):
        if i != j:  # Evita comparar un texto consigo mismo
            level_1 = level_mapping[data["level"]]  # Convertir level a número
            level_2 = level_mapping[other["level"]]  # Convertir level a número
            
            #  Si los niveles están cerca, asignamos una similitud mayor
            similarity_score = 1.0 if abs(level_1 - level_2) <= 1 else 0.0
            
            train_examples.append(
                InputExample(texts=[data["description"], other["description"]], label=float(similarity_score))
            )

#  Verificar que los ejemplos se generen correctamente
print(" Ejemplo de train_examples después de la corrección:")
for example in train_examples[:10]:  # Solo mostrar los primeros 10 ejemplos
    print(f"Texts: {example.texts}, Label: {example.label}")

#  Crear DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)

#  Definir la función de pérdida (CosineSimilarityLoss)
train_loss = losses.CosineSimilarityLoss(model)

#  Configurar el número de épocas y `warmup_steps`
num_epochs = 5
warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)

#  Ejecutar el fine-tuning
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=num_epochs,
    warmup_steps=warmup_steps
)

#  Guardar el modelo ajustado en la misma carpeta
model.save(model_path)
print(" Modelo `all-mpnet-base-v2` afinado y guardado exitosamente en models/all-mpnet-base-v2")