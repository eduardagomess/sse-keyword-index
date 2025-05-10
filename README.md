# 🔐 Keyword-Based Searchable Encryption System

This project implements a **document-based searchable encryption scheme**, inspired by the construction in:

**Searchable Symmetric Encryption: Improved Definitions and Efficient Constructions**  
*Reza Curtmola (NJIT), Juan Garay (AT&T Labs – Research), Seny Kamara (Microsoft Research), and Rafail Ostrovsky (UCLA)*

The implemented SSE-1 model enables **secure search over encrypted documents** using symmetric key encryption (AES-CBC) and **pseudorandom functions (PRFs)**.

## Quick Setup

If you're running on a VM or fresh environment, you can auto-setup everything by running:

```bash
bash setup_vm.sh
```
This script will:

- Create a Python virtual environment

- Install all dependencies (requirements.txt)

- Create necessary folders (data/)

- Set up your project to run immediately

## Run the system

```bash
python main.py
```

This will:

- Generate synthetic plaintext documents

- Encrypt the documents using AES

- Build an encrypted inverted index (Array A + Table T)

- Allow keyword-based search via trapdoor generation

## Example Search Output

```bash
Search word (or 'exit'): diabetes
Matching documents: doc3, doc12, doc57
Search time: 0.0021 seconds
```

## Running Tests

```bash
PYTHONPATH=. pytest tests/
```

This runs:

- test_crypto.py: tests core cryptographic functions: key generation, PRFs, determinism, and input sensitivity.

- test_index.py: tests whether the lookup table entry (T) is correctly masked and unmasked using the keyword-derived mask.

- test_integration.py: tests the full workflow: document encryption, index construction, trapdoor generation, and correct/incorrect search results.

## Technologies Used

- PyCryptodome — AES symmetric encryption (AES-CBC)

- hashlib / HMAC-SHA256 — Pseudorandom Functions (PRF)

- Python 3.10+

- Faker — Synthetic data generation (diseases, patients, etc.)

- pytest — Testing framewor


## 📚 Reference

Curtmola, R., Garay, J. A., Kamara, S., & Ostrovsky, R. (2006).
Searchable symmetric encryption: Improved definitions and efficient constructions.
https://eprint.iacr.org/2006/210.pdf
