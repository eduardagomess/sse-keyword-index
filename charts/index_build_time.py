import os
import sys
import shutil
import time
import matplotlib.pyplot as plt

# Ajustar o path para importar os módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.client import Client
from utils.generators import generate_documents_with_keywords_per_doc

DOCUMENTS_FOLDER = "data/documents"

def run_index_time_vs_keyword_pairs(n_docs: int, keywords_per_doc_list: list) -> list:
    results = []

    for kw_per_doc in keywords_per_doc_list:
        print(f"Running test with {n_docs} docs and {kw_per_doc} keywords per doc...")

        # Limpar pasta
        shutil.rmtree(DOCUMENTS_FOLDER, ignore_errors=True)
        os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)

        # Gerar documentos com N palavras-chave por documento
        generate_documents_with_keywords_per_doc(
            n=n_docs,
            keywords_per_doc=kw_per_doc,
            output_folder=DOCUMENTS_FOLDER
        )

        # Inicializar client
        client = Client()

        # Carregar documentos
        _, keywords_map = client.load_documents_and_keywords(DOCUMENTS_FOLDER)

        total_pairs = sum(len(kw_list) for kw_list in keywords_map.values())

        # Medir tempo de criação do índice
        start = time.perf_counter()
        client.build_secure_index(keywords_map)
        duration = time.perf_counter() - start

        print(f"  ↳ Index build time: {duration:.6f}s for {total_pairs} (w,id) pairs")
        results.append((total_pairs, duration))

    return results


if __name__ == "__main__":
    NUM_DOCS = 10000
    KEYWORDS_PER_DOC = [1, 5, 10, 20, 50, 100]

    results = run_index_time_vs_keyword_pairs(NUM_DOCS, KEYWORDS_PER_DOC)

    # Plotar gráfico
    pairs, times = zip(*results)

    plt.figure(figsize=(10, 6))
    plt.plot(pairs, times, marker='o')
    plt.title("Tempo de Construção do Índice vs Número de pares (w, id)")
    plt.xlabel("Número de pares (w, id)")
    plt.ylabel("Tempo de construção do índice (segundos)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
