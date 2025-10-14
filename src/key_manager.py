from Crypto.PublicKey import RSA
from pathlib import Path

KEYS_DIR = Path(__file__).resolve().parent / "keys"
KEYS_DIR.mkdir(parents=True, exist_ok=True)

def generate_rsa_keys():
    private_key = RSA.generate(2048)
    private_path = KEYS_DIR / "private.pem"
    public_path = KEYS_DIR / "public.pem"

    with open(private_path, "wb") as f:
        f.write(private_key.export_key("PEM"))

    with open(public_path, "wb") as f:
        f.write(private_key.publickey().export_key("PEM"))

    print(f"RSA Keys generated:\n- {private_path}\n- {public_path}")

if __name__ == "__main__":
    generate_rsa_keys()
