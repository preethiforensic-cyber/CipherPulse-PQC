# CipherPulse-PQC

Post-Quantum Cryptography (PQC) inspired encrypted messaging app with socket programming, real-time payload encoding, and multi-threaded GUI
# Post-Quantum Secure Chat

A simple Python chat application built step by step as a Cyber Security / Cyber Forensics mini project. It shows how messages can be encrypted before sending, so that no one in the middle can read them.

This README explains the project in the exact order it was built, with screenshots from each step.


# What This Project Does

- Two users (Server and Client) connect to each other using Python sockets.
- Every message is encrypted using the cryptography library (Fernet — AES + HMAC) before it is sent.
- If someone changes even one byte of the encrypted message, it will fail to decrypt.
- The final version has a simple GUI (built with Tkinter) so both sides can chat like a normal chat app, but everything going through the network is ciphertext, not plain text.


#  Tech Used

 Part           |   Tool 

 Language       | Python 3 
 Encryption     | cryptography library (Fernet) 
Networking      | Python socket 
 GUI            | tkinter  
 Threading      | threading (so GUI doesn't freeze while chatting) 
 Environment    | venv 


#  Step-by-Step Build Process

1. Create the project  (Created a folder named PostQuantumSecureChat on the Desktop, and opened it in the terminal.)

2. Set up the virtual environment

3.Enabled script execution and activated the virtual environment in PowerShell:

powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1


Once (venv) appeared at the start of the line, the environment was active.

 PowerShell showing the execution policy command and successful (venv) activation.

Install the cryptography library

# powershell
pip install cryptography


 Terminal showing cryptography, cffi, and pycparser downloading and installing successfully.

 Create and test basic encryption (test.py)

Created test.py in Notepad first (Notepad asked to create a new file since it didn't exist yet):

 Notepad dialog: "Cannot find test.py. Do you want to create a new file?"

The file used Fernet to generate a key, encrypt a message, and decrypt it back:

# python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

message = b"Post-Quantum Secure Chat Testing!"
encrypted = cipher.encrypt(message)
decrypted = cipher.decrypt(encrypted)

print("Key:", key.decode())
print("Encrypted:", encrypted.decode())
print("Decrypted Message:", decrypted.decode())


# Ran it with python test.py:

 Output showing the generated key, the encrypted text, and the correctly decrypted message: "Post-Quantum Secure Chat Testing!"

This confirmed encryption and decryption were working correctly.

### Step 5 — Build a basic (unencrypted) chat first — server.py and client.py

Before adding encryption to the chat itself, a plain socket-based server and client were built to confirm the connection works.

Created server.py:

 Notepad dialog creating server.py.

python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 5000))
server.listen(1)

print(" Server is waiting for connection...")
conn, addr = server.accept()
print(f" Connected by: {addr}")

while True:
    data = conn.recv(1024).decode()
    if not data or data.lower() == 'exit':
        print("Client disconnected.")
        break
    print(f" Client says: {data}")

    msg = input("Server response: ")
    conn.send(msg.encode())
    if msg.lower() == 'exit':
        break

conn.close()


 server.py code open in the editor.

Created client.py:

 Notepad dialog creating client.py.

python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5000))

print(" Connected to Server! (Type 'exit' to quit)")

while True:
    msg = input("You (Client): ")
    client.send(msg.encode())
    if msg.lower() == 'exit':
        break

    response = client.recv(1024).decode()
    if not response or response.lower() == 'exit':
        print("Server disconnected.")
        break
    print(f" Server says: {response}")

client.close()


 client.py code open in the editor.

At this stage, the two machines could talk to each other, but the messages were sent as plain, unencrypted text.

### Step 6 — Upgrade to encrypted chat — secure_server.py and secure_client.py

Next, encryption was added on top of the same socket logic. The server generates a shared Fernet key and sends it to the client right after connecting; every message after that is encrypted with that key.

Created secure_server.py:

 Notepad dialog creating secure_server.py.

python
import socket
from cryptography.fernet import Fernet

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


# Created secure_client.py:

 Notepad dialog creating secure_client.py (with earlier terminal output from the test.py run and pip install still visible in the background).

python
import socket
from cryptography.fernet import Fernet

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5000))

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


Running secure_server.py in one terminal and secure_client.py in another showed the raw ciphertext being received on each side, and the correctly decrypted message printed right below it — confirming the whole chat was now encrypted end to end at the transport level.

 Build the GUI version — gui_chat.py

To make it usable like a real chat app, the same encrypted logic was wrapped in a Tkinter GUI with Start as Server and Connect as Client buttons, a chat log, and a message box.

First attempt — the window opened but the chat area was blank and not yet wired up correctly:

 Early version of the GUI window, opened but not functioning yet.

After fixing the script and running it properly:

 Two GUI windows side by side. Left window (Server) shows "Session Key Generated! Server listening... Connected to Client". Right window (Client) shows "Connecting to Server... Received Session Security Key! Secure Channel Established!".

Finally, sending an actual message between the two windows worked correctly:

 Both GUI windows showing the message hellow sent from one side and received (Peer: hellow) on the other, with You: hellow shown locally on the sender's side.

Step 8 — Final project structure

Final folder view showing all files created during the project:


PostQuantumSecureChat/
│
├── venv/
├── client.py
├── gui_chat.py
├── secure_client.py
├── secure_server.py
├── server.py
└── test.py




 How to Run It

bash
1. Set up environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install cryptography

2. Run the GUI version
python gui_chat.py


Click Start as Server on one window, and Connect as Client on another. Once you see "Secure Channel Established!", start chatting.



 What This Project Proves

- Messages are encrypted before they leave the sender, and decrypted only after arriving — a middle-man only ever sees ciphertext.
- Fernet encryption also verifies message integrity, so a tampered message would fail to decrypt instead of showing corrupted text.
- The project was built in stages: plain socket chat → encrypted socket chat → encrypted GUI chat, so each layer could be tested before adding the next.
What's Next

- Replace the direct key hand-off with a real post-quantum key exchange (ML-KEM), so the key itself is never sent directly over the network.
- Add an encrypted file vault.
- Add password-based login with Argon2id.
- Add a forensic comparison module (entropy, hash, hex view of plaintext vs. ciphertext.
