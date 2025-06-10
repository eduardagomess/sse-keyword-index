# ---------------------------------------------------------------
# This script was used to generate the search time values for the
# keyword-based index, which are later compared against the results 
# of the document-based index (Algorithm 2). It measures the average 
# search time for a fixed keyword using the secure inverted index scheme described by Curtmola et al.
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

def run_search_and_measure(keyword="hepatite"):
    print(f"Running search test for keyword '{keyword}'...")

    client = Client()
    server = Server()

    documents, keywords_map = client.load_documents_and_keywords(DOCUMENTS_FOLDER)

    encrypted_documents = client.encrypt_documents(documents)
    server.documents = encrypted_documents

    client.build_secure_index(keywords_map)
    server.A = client.A
    server.T = client.T

    trapdoor = client.generate_trapdoor(keyword)

    durations = []
    for _ in range(10):
        start = time.perf_counter()
        _ = server.search(trapdoor)
        durations.append(time.perf_counter() - start)

    avg_search_time = sum(durations) / len(durations)
    return 10, avg_search_time


if __name__ == "__main__":
    results = [run_search_and_measure("hepatite")]

    os.makedirs("charts", exist_ok=True)
    with open(CSV_OUTPUT, "a", newline="") as f:
        writer = csv.writer(f)
        if os.stat(CSV_OUTPUT).st_size == 0:
            writer.writerow(["total_documents", "avg_search_time_sec"])
        writer.writerows(results)

    print(f"\nSearch results saved to: {CSV_OUTPUT}")