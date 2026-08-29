import socket
from cryptography.fernet import Fernet

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5000))

# Receive Shared Key from Server
SHARED_KEY = client.recv(1024)
cipher = Fernet(SHARED_KEY)

print("=" * 50)
print("🔑 Received Encrypted Session Key from Server:")
print(SHARED_KEY.decode())
print("=" * 50)
print("✅ Secure Quantum-Resistant Channel Established!\n")

while True:
    msg = input("You (Client): ")
    encrypted_msg = cipher.encrypt(msg.encode())
    client.send(encrypted_msg)
    
    if msg.lower() == 'exit':
        break
        
    encrypted_response = client.recv(2048)
    if not encrypted_response:
        break
        
    decrypted_response = cipher.decrypt(encrypted_response).decode()
    if decrypted_response.lower() == 'exit':
        print("Server disconnected.")
        break
        
    print(f"🔒 [RAW RECEIVED CIPHERTEXT]: {encrypted_response.decode()}")
    print(f"🔓 [DECRYPTED MESSAGE]: {decrypted_response}\n")

client.close()