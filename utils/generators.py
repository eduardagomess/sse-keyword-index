import os
import random
from faker import Faker

fake = Faker('pt_BR')
DISEASES = ["diabetes", "hipertensao", "asma", "covid", "bronquite", "cancer", "dengue", "gripe", "hepatite", "alergia"]
AGE_RANGE = range(1, 100)

def generate_phone():
    return fake.phone_number()

def generate_patient_name():
    return fake.name()

def generate_documents(n, output_folder="data/documents"):
    """
    Generate n synthetic patient documents and save them as plaintext files
    """
    os.makedirs(output_folder, exist_ok=True)
    for i in range(1, n + 1):
        name = generate_patient_name()
        disease = random.choice(DISEASES)
        age = str(random.choice(AGE_RANGE))
        neighborhood = fake.bairro()
        phone = generate_phone()

        content = (
            f"Name: {name}\n"
            f"Disease: {disease}\n"
            f"Age: {age}\n"
            f"Neighborhood: {neighborhood}\n"
            f"Phone: {phone}\n"
        )

        file_path = os.path.join(output_folder, f"doc{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
