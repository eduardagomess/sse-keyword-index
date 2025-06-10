import os
import json
from typing import Dict, List, Tuple
from core.crypto import PRF, PRF_bytes, SKE_encrypt, SKE_decrypt
from Crypto.Random import get_random_bytes

INDEX_TABLE_SIZE = 500_009
ENCRYPTED_FOLDER = "data/encrypted_docs"

def generate_symmetric_key(k: int = 16) -> bytes:
    """
    SKE2.Gen(1^k): generation of a symmetric key of k bytes for document encryption
    """
    return get_random_bytes(k) # secure random key generation

class Client:
    def __init__(self):             
        self.K1 = get_random_bytes(16)  # used to generate secure pointers for linked list in array A
        self.K2 = get_random_bytes(16)  # used to mask entries in the lookup table T
        self.K3 = get_random_bytes(16)  # used to compute secure indices for lookup in T
        self.K4 = generate_symmetric_key() # symmetric key used to encrypt/decrypt the documents

        self.A = {} # encrypted linked list nodes (array A)
        self.T = {} # lookup table
        self.counter = 1 # counter used to generate unique addresses in A

    def load_documents_and_keywords(self, folder="data/documents") -> Tuple[Dict[str, str], Dict[str, List[str]]]:
        """
        Loads the content of plaintext documents and extracts associated keywords. This corresponds to the δ(D) phase 
        in the SSE setup, where keywords are extracted from each document.
        """

        documents = {}       # stores the raw content of each document
        keywords_map = {}    # stores extracted keywords per document

        for filename in os.listdir(folder): 
            if filename.endswith(".txt"): 
                path = os.path.join(folder, filename)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()  # read full content of the document
                    documents[filename] = content  # store it in the documents dict

                    for line in content.splitlines():
                        if line.lower().startswith("disease:"):
                            value = line.split(":", 1)[1].strip()
                            diseases = [d.strip().lower() for d in value.split(",")]
                            keywords_map.setdefault(filename, []).extend(diseases)
        
        # documents: {'doc1.txt': content, ...}
        # keywords_map: {'doc1.txt': ['cancer'], 'doc2.txt': ['diabetes']}
        return documents, keywords_map

    def encrypt_documents(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """
        Encrypts all plaintext documents using the symmetric key K4

        - Input: a dictionary mapping document IDs to their plaintext content.
        - Output: a dictionary mapping the same document IDs to their encrypted content (as bytes).
        """

        os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
        encrypted_documents = {}

        for doc_id, content in documents.items():
            plaintext_bytes = content.encode()
            encrypted = SKE_encrypt(self.K4, plaintext_bytes)
            encrypted_documents[doc_id] = encrypted

            # Remove .txt before saving .enc
            base_name = os.path.splitext(doc_id)[0]
            file_path = os.path.join(ENCRYPTED_FOLDER, f"{base_name}.enc")
            with open(file_path, "wb") as f:
                f.write(encrypted)

        return encrypted_documents
    
    def build_secure_index(self, keywords_map: Dict[str, List[str]]):
        """
        Builds the secure inverted index (A and T) based on the extracted keywords
        """

        # this block inverts the original mapping from:
        # document_id → list of keywords to keyword → list of document_ids
        # example: "cancer": ["doc1.txt", "doc3.txt"]
        keyword_map = {}
        for doc_id, keywords in keywords_map.items():
            for keyword in keywords:
                keyword_map.setdefault(keyword, []).append(doc_id)

        # for each keyword, build an encrypted linked list
        for keyword, doc_ids in keyword_map.items():
            first_key = get_random_bytes(16)  # key used to encrypt the first node of the linked list (K_(i,0))
            ki_prev = first_key  # initialize the chain with this key
            addr_first = None  # will store the address of the first node (to be saved in T)
            
            for i, doc_id in enumerate(doc_ids):
                ki = get_random_bytes(16)  # generate K_{i,j}: to be included in the current node and used to decrypt the next one

                # generate a unique pseudo-random address for the current node
                while True:
                    addr = PRF(self.K1, str(self.counter)) % INDEX_TABLE_SIZE
                    if addr not in self.A:
                        break
                    self.counter += 1  # skip to next counter if address already used

                if i < len(doc_ids) - 1:  # if it is not the last document
                    # generate a unique next node address
                    temp_counter = self.counter + 1
                    while True:
                        next_addr = PRF(self.K1, str(temp_counter)) % INDEX_TABLE_SIZE
                        if next_addr not in self.A:
                            break
                        temp_counter += 1
                    next_ptr = next_addr.to_bytes(4, 'big')  # pseudo-random pointer to the next node
                    key_next = ki  # key to decrypt the next node
                    ptr_hex = next_ptr.hex()
                else:
                    key_next = b'0' * 16   # dummy key (0^k) since there is no next node to decrypt
                    ptr_hex = "NULL"       # marks the end of the linked list

                node = {
                    "id": doc_id,           # id(Di,j )
                    "k": key_next.hex(),    # key to decrypt the next node (K_{i,j}) in hex format
                    "ptr": ptr_hex          # pointer to the next node
                }

                # encrypt the current node using the previous key (K_{i,j-1}) and store it in A
                encrypted_node = SKE_encrypt(ki_prev, json.dumps(node).encode())
                self.A[addr] = encrypted_node  # store encrypted node at pseudo-random address

                if addr_first is None:
                    addr_first = addr  # store address of first node for table T

                # prepare for next node
                ki_prev = ki
                self.counter += 1

            # convert the first node's address to 4 bytes
            address_bytes = addr_first.to_bytes(4, 'big')

            # concatenate the address and the key of the first node → ⟨addr, K⟩
            entry_plain = address_bytes + first_key

            # generate a pseudo-random mask f_{K2}(w) to protect the lookup entry
            # must use 20 bytes: the ⟨addr, K⟩ structure is 4 bytes (address) + 16 bytes (key), so the mask must match this size to apply XOR correctly
            mask = PRF_bytes(self.K2, keyword, length=20)

            # apply XOR byte-by-byte
            masked_entry = bytes(a ^ b for a, b in zip(entry_plain, mask))

            # compute the index π_{K3}(w) for this keyword in table T
            index = PRF(self.K3, keyword) % INDEX_TABLE_SIZE

            # store the masked entry in T at the secure index
            self.T[index] = masked_entry


    def generate_trapdoor(self, keyword: str) -> Tuple[int, bytes]:
        """
        Generates a secure trapdoor for a given keyword w. This trapdoor allows the server to recover the address and decryption 
        key for the first node in A associated with the queried keyword, without learning the keyword itself.
        """
        
        index = PRF(self.K3, keyword) % INDEX_TABLE_SIZE # compute π_{K3}(w): secure index in the T table for the given keyword
        mask = PRF_bytes(self.K2, keyword, length=20) # compute f_{K2}(w): mask used to unmask the T[π_{K3}(w)] entry

        return index, mask # return the trapdoor t = (index, mask) used for secure search

    def decrypt_document(self, ciphertext: bytes) -> str:
        """ 
        Decrypt a document using the symmetric key K4
        """
        return SKE_decrypt(self.K4, ciphertext).decode()
