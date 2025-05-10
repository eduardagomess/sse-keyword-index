from utils.generators import generate_documents
from core.client import Client
from core.server import Server
import os
import time
import pickle
import csv

TOTAL = 100
BATCH_SIZE = 10_000
DOCUMENTS_FOLDER = "data/documents"
ENCRYPTED_FOLDER = "data/encrypted_docs"
INDEX_FILE = "data/index.pkl"
SUMMARY_FILE = "data/summary_times.csv"

def main():
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

    client = Client()
    server = Server()

    total_encrypt_time = 0
    total_index_time = 0

    for i in range(0, TOTAL, BATCH_SIZE):
        current_batch_size = min(BATCH_SIZE, TOTAL - i)
        batch_num = (i // BATCH_SIZE) + 1
        print(f"Processing batch {batch_num} (creating {current_batch_size} documents)")

        # create documents and map keywords
        generate_documents(current_batch_size, output_folder=DOCUMENTS_FOLDER)
        documents, keywords_map = client.load_documents_and_keywords(DOCUMENTS_FOLDER)

        # encrypt documents
        start_enc = time.time()
        encrypted_docs = client.encrypt_documents(documents)
        end_enc = time.time()
        total_encrypt_time += end_enc - start_enc

        # build index structures:
            # A = encrypted linked list storing nodes per keyword
            # T = lookup table storing masked pointers to the first node of each list
        start_idx = time.time()
        client.build_secure_index(keywords_map)
        end_idx = time.time()
        total_index_time += end_idx - start_idx

        # store in server
        server.store_documents(encrypted_docs)
        server.store_index(client.A, client.T)

        # clean up plaintext documents
        for f in os.listdir(DOCUMENTS_FOLDER):
            os.remove(os.path.join(DOCUMENTS_FOLDER, f))

    # save full index to disk
    with open(INDEX_FILE, "wb") as f:
        pickle.dump({"A": client.A, "T": client.T}, f)

    print("Processing completed!")
    print(f"Total encryption time: {total_encrypt_time:.2f} seconds")
    print(f"Total indexing time: {total_index_time:.2f} seconds")

    search_duration = None

    while True:
        q = input("Search word (or 'exit'): ").strip().lower()
        if q == 'exit':
            break

        trapdoor = client.generate_trapdoor(q)
        start = time.time()
        matches = server.search(trapdoor)
        duration = time.time() - start
        search_duration = duration

        if matches:
            print(f"🔍 Matching documents: {', '.join(matches)}")
            choice = input("Do you want to decrypt and view the matching documents? (y/n): ").strip().lower()
            if choice == 'y':
                for doc_id in matches:
                    decrypted = client.decrypt_document(server.documents[doc_id])
                    print(f"\n📄 Document {doc_id}:\n{decrypted}")
        else:
            print("No documents matched the search.")

        print(f"Search time: {duration:.4f} seconds")

        # Save summary of times
        with open(SUMMARY_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["encrypt_time_sec", "index_time_sec", "search_time_sec"])
            row = [f"{total_encrypt_time:.3f}", f"{total_index_time:.3f}", f"{search_duration:.3f}"]
            writer.writerow(row)

if __name__ == "__main__":
    main()
