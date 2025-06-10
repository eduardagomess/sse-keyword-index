import os
import sys
import shutil
import time
import csv
import matplotlib.pyplot as plt

# Ajustar o path para importar os módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.client import Client
from core.server import Server
from utils.generators import generate_documents_fixed_keyword

DOCUMENTS_FOLDER = "data/documents"
ENCRYPTED_FOLDER = "data/encrypted_docs"

def run_test(n_docs: int) -> tuple:
    print(f"Running test with {n_docs} documents...")

    # Limpar diretórios
    shutil.rmtree(DOCUMENTS_FOLDER, ignore_errors=True)
    shutil.rmtree(ENCRYPTED_FOLDER, ignore_errors=True)
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

    # Gerar documentos
    generate_documents_fixed_keyword(n_docs, keyword="hepatite", keyword_count=50, output_folder=DOCUMENTS_FOLDER)


    # Inicializar client e server
    client = Client()
    server = Server()

    # Carregar e extrair doenças
    documents, keywords_map = client.load_documents_and_keywords(folder=DOCUMENTS_FOLDER)

    # Criptografar documentos
    encrypted_documents = client.encrypt_documents(documents)
    server.documents = encrypted_documents

    # Construir índice
    client.build_secure_index(keywords_map)
    server.A = client.A
    server.T = client.T

    # Gerar trapdoor para "hepatite"
    trapdoor = client.generate_trapdoor("hepatite")

    # Número de documentos que contêm "hepatite"
    docs_with_hepatite = sum("hepatite" in kws for kws in keywords_map.values())

    # Medir tempo médio de busca
    durations = []
    for _ in range(10):
        start = time.perf_counter()
        _ = server.search(trapdoor)
        durations.append(time.perf_counter() - start)

    avg_search_time = sum(durations) / len(durations)
    print(f"  ↳ Avg search time: {avg_search_time:.6f}s | Docs with 'hepatite': {docs_with_hepatite}")
    return n_docs, docs_with_hepatite, avg_search_time


# Executar testes com diferentes quantidades de documentos
results = []
for size in [100, 500, 1000, 2000, 5000, 10000]:
    results.append(run_test(size))

# Salvar CSV
with open("charts/search_time_vs_docs.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["num_documents", "docs_with_hepatite", "search_time_sec"])
    writer.writerows(results)

# Plotar gráfico
num_docs, docs_with_hepatite, times = zip(*results)

plt.figure(figsize=(10, 6))
plt.plot(num_docs, times, marker='o')
plt.title("Search time vs Number of documents")
plt.xlabel("Number of documents")
plt.ylabel("Average search time (seconds)")
plt.xticks(num_docs, [f"{x//1000}k" if x >= 1000 else str(x) for x in num_docs])
plt.grid(True)
plt.tight_layout()
plt.show()
