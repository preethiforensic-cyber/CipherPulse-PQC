import math
import hashlib
import base64
import datetime
from kyber_py.kyber import Kyber512
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# ==========================================
# 1. PQC KEY EXCHANGE LOGIC (Kyber512)
# ==========================================
# NOTE on the correct kyber-py API (this is where every earlier
# version was going wrong):
#   pk, sk   = Kyber512.keygen()
#   key, c   = Kyber512.encaps(pk)     <-- shared KEY comes first, ciphertext second
#   key      = Kyber512.decaps(sk, c)  <-- secret key comes first, ciphertext second
# Kyber512 is used directly as a class (no Kyber512() instance needed).

def generate_kyber_keys():
    """Server generates Kyber Public & Secret Keys"""
    pk, sk = Kyber512.keygen()
    return pk, sk

def encapsulate_kyber(public_key):
    """Client encapsulates using Server's Public Key.
    Returns (ciphertext, shared_secret) so callers on both sides
    use the same (secret, ciphertext) naming order."""
    shared_secret, ciphertext = Kyber512.encaps(public_key)
    return ciphertext, shared_secret

def decapsulate_kyber(ciphertext, secret_key):
    """Server decapsulates using its Secret Key + the received Ciphertext"""
    shared_secret = Kyber512.decaps(secret_key, ciphertext)
    return shared_secret

def derive_fernet_key(shared_secret: bytes) -> bytes:
    """Derives a Fernet-compatible AES key using HKDF from the Kyber shared secret"""
    if not isinstance(shared_secret, (bytes, bytearray)):
        raise TypeError(f"shared_secret must be bytes, got {type(shared_secret)}")

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'pqc-chat-key-derivation',
    )
    derived_bytes = hkdf.derive(bytes(shared_secret))
    return base64.urlsafe_b64encode(derived_bytes)

# ==========================================
# 2. FORENSIC MODULE LOGIC
# ==========================================

def calculate_entropy(data_bytes: bytes) -> float:
    """Calculates Shannon Entropy (Randomness Level: 0 to 8)"""
    if not data_bytes:
        return 0.0
    length = len(data_bytes)
    freq = [0] * 256
    for b in data_bytes:
        freq[b] += 1
    entropy = 0.0
    for count in freq:
        if count:
            p_x = count / length
            entropy += -p_x * math.log2(p_x)
    return round(entropy, 4)

def calculate_sha256(data_bytes: bytes) -> str:
    """Calculates SHA-256 Hash for integrity checking"""
    return hashlib.sha256(data_bytes).hexdigest()

def generate_hex_dump(data_bytes: bytes) -> str:
    """Generates clean Hex Representation"""
    return data_bytes.hex().upper()

def log_forensics(sender: str, plaintext: str, ciphertext_bytes: bytes) -> float:
    """Forensic Log-ஐ txt கோப்பில் சேமிக்கும் ஃபங்ஷன்"""
    entropy = calculate_entropy(ciphertext_bytes)
    sha256_hash = calculate_sha256(ciphertext_bytes)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = (
        f"[{timestamp}] Sender: {sender}\n"
        f"│  Plaintext  : {plaintext}\n"
        f"│  Entropy    : {entropy}\n"
        f"└─ SHA-256    : {sha256_hash}\n"
        f"{'-'*50}\n"
    )

    with open("forensic_logs.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

    return entropy

# ==========================================
# Self-test
# ==========================================
if __name__ == "__main__":
    print("[*] Testing Kyber512 Key Exchange...")
    pk, sk = generate_kyber_keys()
    ct, ss1 = encapsulate_kyber(pk)
    ss2 = decapsulate_kyber(ct, sk)

    if ss1 == ss2:
        print("[SUCCESS] Kyber512 Shared Secret Match!")
        fernet_key = derive_fernet_key(ss1)
        print(f"Derived Fernet Key: {fernet_key.decode()}")

        print("\n[*] Testing Forensic Module...")
        sample = b"Post-Quantum Secure Chat!"
        print(f"Plaintext entropy : {calculate_entropy(sample)}")
        print(f"Ciphertext entropy: {calculate_entropy(ct)}")
        print(f"SHA-256 of sample : {calculate_sha256(sample)}")
        print(f"Hex dump (first 32 chars): {generate_hex_dump(sample)[:32]}...")

        print("\n[*] Testing Forensic Logger...")
        logged_entropy = log_forensics("TestClient", sample.decode(), ct)
        print(f"Logged entropy: {logged_entropy} (see forensic_logs.txt)")
    else:
        print("[ERROR] Key Mismatch!")