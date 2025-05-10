import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def pad(data):
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def SKE_encrypt(key: bytes, plaintext: bytes) -> bytes:
    """
    Performs symmetric encryption using AES in CBC mode (SKE2 encryption step)
    """
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext))
    return cipher.iv + ct_bytes

def SKE_decrypt(key: bytes, ciphertext: bytes) -> bytes:
    """
    Performs symmetric decryption using AES in CBC mode (SKE2 decryption step).
    """
    iv = ciphertext[:16]
    ct = ciphertext[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct))

def PRF(key: bytes, data: str) -> int:
    """
    PRF: pseudo-random function based on SHA-256. This is used in the SSE scheme 
    to generate addresses or indices in the arrays A and T.
    """
    return int(hashlib.sha256(key + data.encode()).hexdigest(), 16)

def PRF_bytes(key: bytes, data: str, length: int = 16) -> bytes:
    """
    Key-derivation function that produces a pseudo-random byte string of fixed length. This is used to generate 
    keys, masks, or pointers in the SSE index.
    """
    
    return hashlib.pbkdf2_hmac(
    'sha256',         # hash algorithm
    data.encode(),    # input string encoded as bytes
    key,              # secret key used as salt
    1000,             # number of times the hash function is applied during key derivation
    dklen=length      # desired output length in bytes
    )
