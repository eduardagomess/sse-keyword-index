from core.client import Client
from core.server import Server

def test_encrypt_then_decrypt_documents_consistency():
    """
    After encrypting and decrypting, the original document content must be recovered.
    """
    client = Client()
    text = "Disease: asthma\nPatient: Alice"
    encrypted = client.encrypt_documents({"doc1": text})
    decrypted = client.decrypt_document(encrypted["doc1"])
    assert decrypted == text

def test_search_finds_word_in_document():
    """
    Searching for a word that exists in the document must return its ID.
    """
    client = Client()
    server = Server()
    docs = {"doc1": "Disease: cancer"}
    keywords_map = {"doc1": ["cancer"]}

    encrypted = client.encrypt_documents(docs)
    client.build_secure_index(keywords_map)
    server.store_index(client.A, client.T)
    server.store_documents(encrypted)

    trapdoor = client.generate_trapdoor("cancer")
    results = server.search(trapdoor)
    assert "doc1" in results

def test_search_returns_multiple_matches():
    """
    If the same keyword appears in multiple docs, all IDs must be returned.
    """
    client = Client()
    server = Server()
    docs = {
        "doc1": "Disease: cancer",
        "doc2": "Disease: cancer"
    }
    keywords_map = {
        "doc1": ["cancer"],
        "doc2": ["cancer"]
    }

    encrypted = client.encrypt_documents(docs)
    client.build_secure_index(keywords_map)
    server.store_index(client.A, client.T)
    server.store_documents(encrypted)

    trapdoor = client.generate_trapdoor("cancer")
    results = server.search(trapdoor)
    assert set(results) == {"doc1", "doc2"}

def test_index_rejects_unknown_word():
    """
    Searching for a non-existent keyword should return an empty list.
    """
    client = Client()
    server = Server()
    docs = {"doc1": "Disease: flu"}
    keywords_map = {"doc1": ["flu"]}

    encrypted = client.encrypt_documents(docs)
    client.build_secure_index(keywords_map)
    server.store_index(client.A, client.T)
    server.store_documents(encrypted)

    trapdoor = client.generate_trapdoor("cancer")
    results = server.search(trapdoor)
    assert results == []
