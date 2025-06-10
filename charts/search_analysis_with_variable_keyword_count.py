import os
import sys
import shutil
import time
import csv
import matplotlib.pyplot as plt

# Ajustar manualmente se necessário no seu ambiente
sys.path.append(".")

from core.client import Client
from core.server import Server
from utils.generators import generate_documents_fixed_keyword

DOCUMENTS_FOLDER = "data/documents"
ENCRYPTED_FOLDER = "data/encrypted_docs"

def run_keyword_variation_test(n_docs: int, keyword_counts: list) -> list:
    results = []

    for count in keyword_counts:
        print(f"Running test with {count} documents containing 'hepatite'...")

        # Limpar diretórios
        shutil.rmtree(DOCUMENTS_FOLDER, ignore_errors=True)
        shutil.rmtree(ENCRYPTED_FOLDER, ignore_errors=True)
        os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
        os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

        # Gerar documentos com quantidade fixa da keyword
        generate_documents_fixed_keyword(n_docs, keyword="hepatite", keyword_count=count, output_folder=DOCUMENTS_FOLDER)
        print(f"  ↳ Generated {count} documents containing 'hepatite'")

        # Inicializar client e server
        print("Initializing client and server...")
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
        print("  ↳ Secure index built")

        # Gerar trapdoor para "hepatite"
        trapdoor = client.generate_trapdoor("hepatite")
        print("  ↳ Trapdoor generated for 'hepatite'")

        # Medir tempo médio de busca
        durations = []
        for _ in range(10):
            start = time.perf_counter()
            _ = server.search(trapdoor)
            durations.append(time.perf_counter() - start)

        avg_search_time = sum(durations) / len(durations)
        print(f"  ↳ Avg search time: {avg_search_time:.6f}s | Docs with 'hepatite': {count}")
        results.append((count, avg_search_time))

    return results

if __name__ == "__main__":
    # Parâmetros do experimento
    TOTAL_DOCS = 10000
    KEYWORD_COUNTS = [1000, 3000, 5000, 8000]

    # Executar teste
    results = run_keyword_variation_test(TOTAL_DOCS, KEYWORD_COUNTS)

    # Salvar CSV
    os.makedirs("charts", exist_ok=True)
    with open("charts/search_time_vs_keyword_count.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["docs_with_hepatite", "search_time_sec"])
        writer.writerows(results)

    # Plotar gráfico
    counts, times = zip(*results)
    plt.figure(figsize=(10, 6))
    plt.plot(counts, times, marker='o')
    plt.title("Tempo de busca vs Número de documentos contendo 'hepatite'")
    plt.xlabel("Número de documentos contendo 'hepatite'")
    plt.ylabel("Tempo de busca medio (seconds)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
