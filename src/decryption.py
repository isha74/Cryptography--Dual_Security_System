from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from pathlib import Path

KEYS_DIR = Path(__file__).resolve().parent / "keys"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def decrypt_aes_key():
    """Decrypt the AES key using RSA private key"""
    with open(KEYS_DIR / "private.pem", "rb") as f:
        private_key = RSA.import_key(f.read())

    with open(KEYS_DIR / "encrypted_aes_key.bin", "rb") as f:   # FIXED
        encrypted_aes_key = f.read()

    cipher_rsa = PKCS1_OAEP.new(private_key)
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)
    return aes_key

def decrypt_file(encrypted_file, output_file):
    """Decrypt a file using AES key"""
    aes_key = decrypt_aes_key()

    with open(encrypted_file, "rb") as f:
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print(f"✅ File decrypted and saved as: {output_file}")

if __name__ == "__main__":
    encrypted_file = OUTPUT_DIR / "0002_encrypted.bin"   # use same file from encryption.py
    decrypted_file = OUTPUT_DIR / "0002_decrypted.dcm"   # decrypted output
    decrypt_file(encrypted_file, decrypted_file)
