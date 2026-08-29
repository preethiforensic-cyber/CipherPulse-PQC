import socket
from cryptography.fernet import Fernet

# 1. Post-Quantum / Hybrid Symmetric Key Generation
SHARED_KEY = Fernet.generate_key()
cipher = Fernet(SHARED_KEY)

print("=" * 50)
print("🔑 Generated Shared Security Key for Session:")
print(SHARED_KEY.decode())
print("=" * 50)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 5000))
server.listen(1)

print("\n🔒 Quantum-Safe Server waiting for connection...")
conn, addr = server.accept()
print(f"✅ Connected by: {addr}")

# Send Shared Key to Client for Session Handshake
conn.send(SHARED_KEY)

while True:
    encrypted_data = conn.recv(2048)
    if not encrypted_data:
        break
    
    decrypted_msg = cipher.decrypt(encrypted_data).decode()
    if decrypted_msg.lower() == 'exit':
        print("Client disconnected.")
        break
        
    print(f"\n🔒 [RAW RECEIVED CIPHERTEXT]: {encrypted_data.decode()}")
    print(f"🔓 [DECRYPTED MESSAGE]: {decrypted_msg}")
    
    reply = input("\nServer Response: ")
    encrypted_reply = cipher.encrypt(reply.encode())
    conn.send(encrypted_reply)
    if reply.lower() == 'exit':
        break

conn.close()