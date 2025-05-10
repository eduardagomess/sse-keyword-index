from core.client import Client
from core.crypto import PRF

def test_all_keys_have_correct_length():
    """
    All cryptographic keys (K1, K2, K3, K4) must be exactly 16 bytes for AES compatibility.
    """
    client = Client()
    assert len(client.K1) == 16
    assert len(client.K2) == 16
    assert len(client.K3) == 16
    assert len(client.K4) == 16

def test_prf_deterministic():
    """
    The same input to the PRF must always produce the same output (determinism).
    """
    key = b"this_is_a_key123"
    msg = "test"
    out1 = PRF(key, msg)
    out2 = PRF(key, msg)
    assert out1 == out2

def test_prf_changes_on_input():
    """
    A small change in input should result in a different PRF output (sensitivity).
    """
    key = b"this_is_a_key123"
    out1 = PRF(key, "abc")
    out2 = PRF(key, "abd")
    assert out1 != out2
