import json
import random

# Listas de valores ficticios para enmascarar los datos
roles =[
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Software Engineer",
    "Software Architect",
    "Mobile Developer",
    "Data Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Analyst",
    "Database Administrator",
    "Big Data Specialist",
    "DevOps Engineer",
    "Systems Administrator",
    "Network Administrator",
    "Cybersecurity Specialist",
    "Security Engineer",
    "Penetration Tester (Pentester)",
    "Security Analyst",
    "Security Architect",
    "Cloud Computing Specialist",
    "Cloud Solutions Architect",
    "Cloud Infrastructure Administrator",
    "Automation Engineer",
    "Integration Engineer",
    "API Developer",
    "QA Tester",
    "Automated Testing Engineer",
    "Technology Manager",
    "Scrum Master",
    "Product Owner",
    "IT Project Manager",
    "IT Business Analyst",
    "UX/UI Specialist",
    "User Experience Designer",
    "Game Developer",
    "Augmented Reality Engineer",
    "Virtual Reality Engineer",
    "Blockchain Engineer",
    "Smart Contracts Developer",
    "Server Administrator",
    "Virtualization Specialist",
    "Linux Administrator",
    "Windows Server Administrator",
    "Technical Support Engineer",
    "ITIL Specialist",
    "Technology Consultant",
    "Infrastructure Architect",
    "No-Code/Low-Code Developer",
    "Internet of Things (IoT) Specialist"
]

animals = [
    "Abeja",
    "Abejorro",
    "Águila",
    "Alce",
    "Almeja",
    "Anaconda",
    "Anguila",
    "Antílope",
    "Araña",
    "Ardilla",
    "Avestruz",
    "Avispa",
    "Babosa",
    "Ballena",
    "Bisonte",
    "Boa",
    "Búfalo",
    "Burro",
    "Caballo",
    "Cabra",
    "Caimán",
    "Calamar",
    "Camaleón",
    "Camello",
    "Canario",
    "Cangrejo",
    "Canguro",
    "Caracol",
    "Castor",
    "Cebra",
    "Cernícalo",
    "Cerdo",
    "Ciervo",
    "Cigüeña",
    "Cisne",
    "Cobra",
    "Cochinilla",
    "Cocodrilo",
    "Colibrí",
    "Comadreja",
    "Conejo",
    "Coral",
    "Cormorán",
    "Coyote",
    "Cucaracha",
    "Delfín",
    "Dromedario",
    "Elefante",
    "Erizo",
    "Escarabajo",
    "Escorpión",
    "Estrella de mar",
    "Flamenco",
    "Foca",
    "Gacela",
    "Gallina",
    "Gallo",
    "Gamba",
    "Gato",
    "Gaviota",
    "Gorila",
    "Grillo",
    "Guacamayo",
    "Guepardo",
    "Halcón",
    "Hamster",
    "Hiena",
    "Hipopótamo",
    "Hormiga",
    "Hurón",
    "Iguana",
    "Jabalí",
    "Jaguar",
    "Jirafa",
    "Koala",
    "Lagarto",
    "Langosta",
    "Lechuza",
    "Lémur",
    "León",
    "Leopardo",
    "Lobo",
    "Loro",
    "Luciérnaga",
    "Mamut",
    "Manatí",
    "Mapache",
    "Medusa",
    "Mofeta",
    "Mono",
    "Morsa",
    "Mosca",
    "Mosquito",
    "Murciélago",
    "Nutria",
    "Orangután",
    "Orca",
    "Oruga",
    "Oso",
    "Ostra",
    "Paloma",
    "Pantera",
    "Pato",
    "Pavo",
    "Perezoso",
    "Perro",
    "Pez payaso",
    "Pingüino"
]

animal_types = [
    "Mamífero",
    "Reptil",
    "Ave",
    "Pez",
    "Anfibio",
    "Insecto",
    "Arácnido",
    "Crustáceo",
    "Molusco",
    "Equinodermo",
    "Cnidario",
    "Gusano",
    "Miriápodo",
    "Marsupial",
    "Rumiantes",
    "Roedor",
    "Carnívoro",
    "Herbívoro",
    "Omnívoro",
    "Acuático"
]

actors = [
    "Tom Hanks",
    "Meryl Streep",
    "Leonardo DiCaprio",
    "Scarlett Johansson",
    "Brad Pitt",
    "Angelina Jolie",
    "Denzel Washington",
    "Robert De Niro",
    "Al Pacino",
    "Natalie Portman",
    "Morgan Freeman",
    "Cate Blanchett",
    "Johnny Depp",
    "Viola Davis",
    "Christian Bale",
    "Nicole Kidman",
    "Joaquin Phoenix",
    "Charlize Theron",
    "Hugh Jackman",
    "Emma Stone",
    "Samuel L. Jackson",
    "Julia Roberts",
    "Ryan Gosling",
    "Anne Hathaway",
    "Matt Damon",
    "Jennifer Lawrence",
    "Keanu Reeves",
    "Sandra Bullock",
    "Jake Gyllenhaal",
    "Emily Blunt",
    "Robert Downey Jr.",
    "Amy Adams",
    "Javier Bardem",
    "Salma Hayek",
    "Idris Elba",
    "Marion Cotillard",
    "Chris Hemsworth",
    "Tilda Swinton",
    "Adam Driver",
    "Jessica Chastain",
    "Benedict Cumberbatch",
    "Halle Berry",
    "Michael Fassbender",
    "Brie Larson",
    "Daniel Day-Lewis",
    "Timothée Chalamet",
    "Kate Winslet",
    "Eddie Redmayne",
    "Chris Evans",
    "Tom Hardy"
]

def truncate_description(description, length=50):
    """
    Trunca la descripción a la cantidad de caracteres especificada.
    Si el texto es mayor a 'length', lo recorta y añade '...' al final.
    """
    if isinstance(description, str) and len(description) > length:
        return description[:length] + "..."
    return description

def mask_data(data):
    """
    Reemplaza los valores de los campos `project`, `industry` y `contact` con valores aleatorios de listas ficticias.
    """
    for item in data:
        item["project"] = random.choice(animals)  # Reemplazar con un animal
        item["industry"] = random.choice(animal_types)  # Reemplazar con un tipo de animal
        item["contact"] = random.choice(actors)  # Reemplazar con un actor famoso
        item["roleName"] = random.choice(roles)  # Reemplazar con un actor famoso

                # Truncar la descripción a 50 caracteres
        if "description" in item:
            item["description"] = truncate_description(item["description"], 50)
    
    return data

def process_json(input_file, output_file):
    """
    Carga un JSON desde una ubicación específica, enmascara los datos y guarda el JSON modificado en otra ubicación.
    
    :param input_file: Ruta del archivo JSON de entrada.
    :param output_file: Ruta del archivo JSON de salida con los datos enmascarados.
    """
    try:
        # Cargar el archivo JSON de la ubicación especificada
        with open(input_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Aplicar la enmascaración de datos
        masked_data = mask_data(json_data)

        # Guardar el JSON enmascarado en la ubicación especificada
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(masked_data, f, indent=4, ensure_ascii=False)

        print(f"Masked JSON saved successfully at: {output_file}")

    except Exception as e:
        print(f"Error processing JSON file: {e}")

# Ruta de los archivos (cambia las rutas según tu sistema)
input_json_path = "/Users/julio.c.gomez.valdez/Documents/Demanda/demand_output.json"   # Ruta del archivo JSON de entrada
output_json_path = "/Users/julio.c.gomez.valdez/Documents/Demanda/masked_data.json" # Ruta del archivo JSON de salida

# Ejecutar el proceso
process_json(input_json_path, output_json_path)
