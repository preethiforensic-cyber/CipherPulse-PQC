from cryptography.fernet import Fernet

# Secret Key உருவாக்க
key = Fernet.generate_key()
cipher = Fernet(key)

# Secret Message
message = b"Post-Quantum Secure Chat Testing!"
encrypted = cipher.encrypt(message)
decrypted = cipher.decrypt(encrypted)

print("Key:", key.decode())
print("Encrypted:", encrypted.decode())
print("Decrypted Message:", decrypted.decode())