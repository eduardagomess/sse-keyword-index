import json
from typing import Dict, List, Tuple
from core.crypto import SKE_decrypt


class Server:
    def __init__(self):
        self.A = {}           # encrypted nodes (linked list)
        self.T = {}           # lookup table
        self.documents = {}   # encrypted documents

    def store_index(self, A: Dict[int, bytes], T: Dict[int, bytes]):
        """
        Stores the encrypted index structures A and T.
        """
        self.A = A
        self.T = T

    def store_documents(self, encrypted_docs: Dict[str, bytes]):
        """
        Stores encrypted documents sent by the client.
        """
        self.documents = encrypted_docs

    def search(self, trapdoor: Tuple[int, bytes]) -> List[str]:
        """
        Uses the trapdoor t to search the encrypted index and returns the list of matching document IDs.
        """
        index_pos, mask = trapdoor  # γ, η = (π_{K3}(w), f_{K2}(w))

        # if there's no entry at the computed index, return empty
        if index_pos not in self.T:
            return []

        t_entry = self.T[index_pos]

        # ensure sizes match before applying XOR
        if len(mask) != len(t_entry):
            raise ValueError(f"Mask length {len(mask)} does not match entry length {len(t_entry)}")

        # recover ⟨addr, K⟩ by unmasking the entry: θ ⊕ η
        entry_plain_bytes = []
        for a, b in zip(t_entry, mask):
            entry_plain_bytes.append(a ^ b)
        entry_plain = bytes(entry_plain_bytes)

        addr = int.from_bytes(entry_plain[:4], 'big')  # α: starting address in A
        key = entry_plain[4:20] # K: decryption key for first node

        assert len(key) == 16, f"Recovered key length is {len(key)}, should be 16 bytes for AES"

        results = []

        # traverse the encrypted linked list starting from addr
        while True:
            encrypted_node = self.A.get(addr)
            if not encrypted_node:
                break  # no node found at this address — stop
            try:
                # decrypt the current node using the key from the previous step
                plaintext = SKE_decrypt(key, encrypted_node)
                decrypted = json.loads(plaintext.decode())
            except Exception as e:
                print("Failed to decrypt node")
                raise e

            # collect the document ID from the current node
            results.append(decrypted["id"])

            # if the current node is the last one in the list, stop
            if decrypted["ptr"] == "NULL":
                break

            # otherwise, prepare for the next node and update addr to point to the next node in the list
            addr = int(decrypted["ptr"], 16)

            # get the key to decrypt the next node
            key = bytes.fromhex(decrypted["k"])
            assert len(key) == 16, f"Next key is {len(key)} bytes — expected 16"
        return results