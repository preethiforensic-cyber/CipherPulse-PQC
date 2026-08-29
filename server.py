import socket
import threading
from cryptography.fernet import Fernet
from pqc_helper import generate_kyber_keys, decapsulate_kyber, derive_fernet_key, log_forensics

HOST = '127.0.0.1'
PORT = 65432

def receive_messages(conn, cipher):
    """Client-லிருந்து வரும் செய்திகளைப் பெறுதல்"""
    while True:
        try:
            encrypted_data = conn.recv(1024)
            if not encrypted_data:
                break
            
            decrypted_msg = cipher.decrypt(encrypted_data).decode()
            entropy = log_forensics("Client", decrypted_msg, encrypted_data)
            
            print(f"\n[Client]: {decrypted_msg}")
            print(f"└─ [Forensics Logged] Entropy: {entropy}")
            print("Server: ", end="", flush=True)
            
        except Exception:
            print("\n[-] Client disconnected.")
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"[*] Server listening on {HOST}:{PORT}")
    
    conn, addr = server.accept()
    print(f"\n[+] Connected to Client: {addr}")
    
    # PQC Key Exchange
    pk, sk = generate_kyber_keys()
    conn.sendall(pk)
    ciphertext = conn.recv(2048)
    shared_secret = decapsulate_kyber(ciphertext, sk)
    
    fernet_key = derive_fernet_key(shared_secret)
    cipher = Fernet(fernet_key)
    print("[SUCCESS] Post-Quantum Channel Established!\n")

    # Receiving Thread (பின்னணியில் இயங்கும்)
    threading.Thread(target=receive_messages, args=(conn, cipher), daemon=True).start()

    # Sending Loop (Server மெசேஜ் அனுப்ப)
    while True:
        msg = input("Server: ")
        if msg.lower() == 'exit':
            break
        
        encrypted_msg = cipher.encrypt(msg.encode())
        log_forensics("Server", msg, encrypted_msg)
        conn.sendall(encrypted_msg)

    conn.close()

if __name__ == "__main__":
    start_server()