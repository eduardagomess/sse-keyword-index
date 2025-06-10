# ---------------------------------------------------------------
# This script was used to measure the index creation time for the
# keyword-based index (Algorithm 1), which will later be compared 
# with the index creation time of the document-based index (Algorithm 2).
# It simulates the construction of a secure inverted index as 
# described by Curtmola et al.
# ---------------------------------------------------------------

import os
import time
import csv
import sys
sys.path.append(".")

from core.client import Client
from core.server import Server

# Update the path below to point to the folder where the documents were generated
DOCUMENTS_FOLDER = ""
ENCRYPTED_FOLDER = "data/encrypted_docs"
CSV_OUTPUT = "charts/search_time_result.csv"

def run_index():
        # Inicializar client
        client = Client()

        # Carregar documentos
        _, keywords_map = client.load_documents_and_keywords(DOCUMENTS_FOLDER)
        print(keywords_map)

        # Medir tempo de criação do índice
        start = time.perf_counter()
        client.build_secure_index(keywords_map)
        duration = time.perf_counter() - start
        # change the total documents for consistency with the search time
        return 10, duration
    
if __name__ == "__main__":
    results = [run_index()]

    os.makedirs("charts", exist_ok=True)
    with open(CSV_OUTPUT, "a", newline="") as f:
        writer = csv.writer(f)
        if os.stat(CSV_OUTPUT).st_size == 0:
            writer.writerow(["total_documents", "avg_search_time_sec"])
        writer.writerows(results)

    print(f"\nSearch results saved to: {CSV_OUTPUT}")