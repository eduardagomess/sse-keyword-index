from utils.generators import generate_documents
from core.client import Client
from core.server import Server
import os
import time
import csv
import statistics

TOTAL = 1000
BATCH_SIZE = 10_000
DOCUMENTS_FOLDER = "data/documents"
ENCRYPTED_FOLDER = "data/encrypted_docs"
SUMMARY_FILE = "data/summary_times.csv"

def main():
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

    client = Client()
    server = Server()

    print(f"Generating {TOTAL} documents...")
    start_gen = time.time()
    generate_documents(TOTAL, output_folder=DOCUMENTS_FOLDER)
    end_gen = time.time()
    generation_time = end_gen - start_gen

    print("Loading all documents...")
    documents, keywords_map = client.load_documents_and_keywords(DOCUMENTS_FOLDER)
    all_doc_ids = list(documents.keys())

    total_index_time = 0

    for i in range(0, TOTAL, BATCH_SIZE):
        current_batch_size = min(BATCH_SIZE, TOTAL - i)
        batch_num = (i // BATCH_SIZE) + 1
        print(f"Processing batch {batch_num} with {current_batch_size} documents")

        batch_doc_ids = all_doc_ids[i:i + current_batch_size]
        batch_documents = {doc_id: documents[doc_id] for doc_id in batch_doc_ids}
        batch_keywords = {doc_id: keywords_map[doc_id] for doc_id in batch_doc_ids}

        # Encrypt documents
        encrypted_docs = client.encrypt_documents(batch_documents)

        # Build secure index
        start_idx = time.time()
        client.build_secure_index(batch_keywords)
        end_idx = time.time()
        total_index_time += end_idx - start_idx

        # Store in server
        server.store_documents(encrypted_docs)
        server.store_index(client.A, client.T)

    print("Processing completed!")
    print(f"Total document generation time: {generation_time:.2f} seconds")
    print(f"Total indexing time: {total_index_time:.2f} seconds")

    while True:
        q = input("Search word (or 'exit'): ").strip().lower()
        if q == 'exit':
            break

        trapdoor = client.generate_trapdoor(q)
        

        print("Measuring average search time over 50 runs...")
        durations = []
        matches = None

        for _ in range(50):
            start = time.perf_counter()
            result = server.search(trapdoor)
            durations.append(time.perf_counter() - start)
            matches = result  # same for all runs

        search_duration = statistics.mean(durations)
        print(f"Average search time: {search_duration:.6f} seconds")

        if matches:
            print(f"Matching documents: {', '.join(matches)}")
            choice = input("Do you want to decrypt and view the matching documents? (y/n): ").strip().lower()
            if choice == 'y':
                for doc_id in matches:
                    decrypted = client.decrypt_document(server.documents[doc_id])
                    print(f"Document {doc_id}:\n{decrypted}")
        else:
            print("No documents matched the search.")

        # Save summary of times
        with open(SUMMARY_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["generation_time_sec", "index_time_sec", "search_time_sec"])
            row = [f"{generation_time:.3f}", f"{total_index_time:.3f}", f"{search_duration:.3f}"]
            writer.writerow(row)

if __name__ == "__main__":
    main()