from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from pathlib import Path
import os

KEYS_DIR = Path(__file__).resolve().parent / "keys"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def encrypt_file(file_path):
    # 1. Load RSA public key
    public_key_path = KEYS_DIR / "public.pem"
    with open(public_key_path, "rb") as f:
        public_key = RSA.import_key(f.read())
    cipher_rsa = PKCS1_OAEP.new(public_key)

    # 2. Generate AES key
    aes_key = get_random_bytes(32)  # 256-bit key
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)

    # 3. Read file data
    with open(file_path, "rb") as f:
        file_data = f.read()

    # 4. Encrypt file data
    ciphertext, tag = cipher_aes.encrypt_and_digest(file_data)

    # 5. Save encrypted file
    encrypted_file_path = OUTPUT_DIR / (Path(file_path).stem + "_encrypted.bin")
    with open(encrypted_file_path, "wb") as f:
        [f.write(x) for x in (cipher_aes.nonce, tag, ciphertext)]

    # 6. Encrypt AES key with RSA and save
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)
    encrypted_key_path = KEYS_DIR / "encrypted_aes_key.bin"
    with open(encrypted_key_path, "wb") as f:
        f.write(encrypted_aes_key)

    print(f"✅ File encrypted: {encrypted_file_path}")
    print(f"🔑 AES key encrypted and saved at: {encrypted_key_path}")

if __name__ == "__main__":
    file_to_encrypt = input("Enter file path to encrypt: ")
    encrypt_file(file_to_encrypt)
