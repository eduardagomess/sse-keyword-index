import os
import random
from faker import Faker
from typing import List


fake = Faker('pt_BR')
DISEASES = [
    "diabetes", "hipertensao", "asma", "covid", "bronquite", "cancer",
    "dengue", "gripe", "hepatite", "alergia"]
AGE_RANGE = range(1, 100)

DISEASE_PROPORTIONS = {
    "bronquite": 0.08,
    "gripe": 0.02,
    "hepatite": 0.40,
    "cancer": 0.10,
    "covid": 0.10,
    "dengue": 0.10,
    "hipertensao": 0.10,
    "diabetes": 0.05,
    "asma": 0.02,
    "alergia": 0.01
}

def generate_phone():
    return fake.phone_number()

def generate_patient_name():
    return fake.name()

def generate_documents(n, output_folder="data/documents", max_diseases_per_patient=5, fixed_disease="hepatite", fixed_proportion=0.4):
    os.makedirs(output_folder, exist_ok=True)
    total_diseases_needed = n * max_diseases_per_patient

    # Step 1: Allocate fixed disease
    num_fixed = round(total_diseases_needed * fixed_proportion)
    disease_pool = [fixed_disease] * num_fixed

    # Step 2: Normalize remaining proportions
    remaining_diseases = {k: v for k, v in DISEASE_PROPORTIONS.items() if k != fixed_disease}
    total_remaining = sum(remaining_diseases.values())
    normalized_remaining = {k: v / total_remaining for k, v in remaining_diseases.items()}

    # Step 3: Allocate other diseases proportionally
    num_remaining = total_diseases_needed - num_fixed
    for disease, weight in normalized_remaining.items():
        count = round(num_remaining * weight)
        disease_pool.extend([disease] * count)

    # Adjust for exact length
    while len(disease_pool) < total_diseases_needed:
        disease_pool.append(random.choice(list(normalized_remaining.keys())))
    disease_pool = disease_pool[:total_diseases_needed]
    random.shuffle(disease_pool)

    for i in range(1, n + 1):
        name = generate_patient_name()
        age = str(random.choice(AGE_RANGE))
        neighborhood = fake.bairro()
        phone = generate_phone()

        # Select diseases for the patient
        num_diseases = random.randint(1, max_diseases_per_patient)
        diseases = set()
        while len(diseases) < num_diseases and disease_pool:
            diseases.add(disease_pool.pop())

        content = (
            f"Name: {name}\n"
            f"Disease: {', '.join(diseases)}\n"
            f"Age: {age}\n"
            f"Neighborhood: {neighborhood}\n"
            f"Phone: {phone}\n"
        )

        file_path = os.path.join(output_folder, f"doc{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

def generate_documents_fixed_keyword(n: int, output_folder="data/documents", keyword="hepatite", keyword_count=50, max_diseases_per_patient=5):
    """
    Generates `n` documents, ensuring that exactly `keyword_count` of them contain the specified `keyword`.
    """
    os.makedirs(output_folder, exist_ok=True)

    other_diseases = [d for d in DISEASE_PROPORTIONS if d != keyword]
    keyword_indices = set(random.sample(range(n), min(keyword_count, n)))

    for i in range(n):
        name = generate_patient_name()
        age = str(random.choice(AGE_RANGE))
        neighborhood = fake.bairro()
        phone = generate_phone()

        diseases: List[str] = []

        # Force the keyword to appear in `keyword_count` documents
        if i in keyword_indices:
            diseases.append(keyword)

        # Fill in the remaining diseases
        while len(diseases) < max_diseases_per_patient:
            # If exhausted, reshuffle the disease pool
            disease_pool = random.sample(other_diseases, len(other_diseases))
            for disease in disease_pool:
                if disease not in diseases and disease != keyword:
                    diseases.append(disease)
                    if len(diseases) == max_diseases_per_patient:
                        break

        content = (
            f"Name: {name}\n"
            f"Disease: {', '.join(diseases)}\n"
            f"Age: {age}\n"
            f"Neighborhood: {neighborhood}\n"
            f"Phone: {phone}\n"
        )

        file_path = os.path.join(output_folder, f"doc{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return keyword_indices 

def generate_documents_with_keywords_per_doc(n: int, keywords_per_doc: int, output_folder: str = "data/documents"):
    """
    Generates `n` documents, each containing exactly `keywords_per_doc` keywords (diseases).
    """
    DISEASES = [
        "diabetes", "hipertensao", "asma", "covid", "bronquite", "cancer",
        "dengue", "gripe", "hepatite", "alergia",
        "doenca11", "doenca12", "doenca13", "doenca14", "doenca15",
        "doenca16", "doenca17", "doenca18", "doenca19", "doenca20",
        "doenca21", "doenca22", "doenca23", "doenca24", "doenca25",
        "doenca26", "doenca27", "doenca28", "doenca29", "doenca30",
        "doenca31", "doenca32", "doenca33", "doenca34", "doenca35",
        "doenca36", "doenca37", "doenca38", "doenca39", "doenca40",
        "doenca41", "doenca42", "doenca43", "doenca44", "doenca45",
        "doenca46", "doenca47", "doenca48", "doenca49", "doenca50",
        "doenca51", "doenca52", "doenca53", "doenca54", "doenca55",
        "doenca56", "doenca57", "doenca58", "doenca59", "doenca60",
        "doenca61", "doenca62", "doenca63", "doenca64", "doenca65",
        "doenca66", "doenca67", "doenca68", "doenca69", "doenca70",
        "doenca71", "doenca72", "doenca73", "doenca74", "doenca75",
        "doenca76", "doenca77", "doenca78", "doenca79", "doenca80",
        "doenca81", "doenca82", "doenca83", "doenca84", "doenca85",
        "doenca86", "doenca87", "doenca88", "doenca89", "doenca90",
        "doenca91", "doenca92", "doenca93", "doenca94", "doenca95",
        "doenca96", "doenca97", "doenca98", "doenca99", "doenca100"
    ]


    DISEASE_PROPORTIONS = {d: 1/len(DISEASES) for d in DISEASES}

    os.makedirs(output_folder, exist_ok=True)

    all_diseases = list(DISEASE_PROPORTIONS.keys())
    if keywords_per_doc > len(all_diseases):
        raise ValueError("keywords_per_doc exceeds number of available diseases")

    for i in range(n):
        name = generate_patient_name()
        age = str(random.choice(AGE_RANGE))
        neighborhood = fake.bairro()
        phone = generate_phone()

        diseases = random.sample(all_diseases, keywords_per_doc)

        content = (
            f"Name: {name}\n"
            f"Disease: {', '.join(diseases)}\n"
            f"Age: {age}\n"
            f"Neighborhood: {neighborhood}\n"
            f"Phone: {phone}\n"
        )

        file_path = os.path.join(output_folder, f"doc{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)