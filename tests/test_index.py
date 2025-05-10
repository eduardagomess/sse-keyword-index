from core.client import Client
from core.crypto import PRF_bytes

def test_lookup_table_entry_masking_and_unmasking():
    """
    Verifies that (addr || K) ⊕ f_K2(w) can be reversed using the same mask.
    """
    client = Client()
    keyword = "diabetes"
    address = 42
    key = client.K4
    entry_plain = address.to_bytes(4, 'big') + key
    mask = PRF_bytes(client.K2, keyword, length=20)
    masked_entry = bytes([a ^ b for a, b in zip(entry_plain, mask)])
    unmasked_entry = bytes([a ^ b for a, b in zip(masked_entry, mask)])
    assert unmasked_entry == entry_plain
