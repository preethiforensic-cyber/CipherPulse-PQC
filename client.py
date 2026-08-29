import socket
import threading
from cryptography.fernet import Fernet
from pqc_helper import encapsulate_kyber, derive_fernet_key, log_forensics

HOST = '127.0.0.1'
PORT = 65432

def receive_messages(client, cipher):
    """Server-லிருந்து வரும் செய்திகளைப் பெறுதல்"""
    while True:
        try:
            encrypted_data = client.recv(1024)
            if not encrypted_data:
                break
            
            decrypted_msg = cipher.decrypt(encrypted_data).decode()
            entropy = log_forensics("Server", decrypted_msg, encrypted_data)
            
            print(f"\n[Server]: {decrypted_msg}")
            print(f"└─ [Forensics Logged] Entropy: {entropy}")
            print("You: ", end="", flush=True)
            
        except Exception:
            print("\n[-] Connection lost.")
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print("[*] Connected to Server.")

    # PQC Key Exchange
    server_pk = client.recv(2048)
    ciphertext, shared_secret = encapsulate_kyber(server_pk)
    client.sendall(ciphertext)

    fernet_key = derive_fernet_key(shared_secret)
    cipher = Fernet(fernet_key)
    print("[SUCCESS] Post-Quantum Encrypted Chat Ready!\n")

    # Receiving Thread (பின்னணியில் இயங்கும்)
    threading.Thread(target=receive_messages, args=(client, cipher), daemon=True).start()

    # Sending Loop (Client மெசேஜ் அனுப்ப)
    while True:
        msg = input("You: ")
        if msg.lower() == 'exit':
            break
        
        encrypted_msg = cipher.encrypt(msg.encode())
        log_forensics("Client", msg, encrypted_msg)
        client.sendall(encrypted_msg)

    client.close()

if __name__ == "__main__":
    start_client()