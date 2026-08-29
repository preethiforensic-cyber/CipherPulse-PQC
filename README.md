# CipherPulse-PQC

Post-Quantum Cryptography (PQC) inspired encrypted messaging app with socket programming, real-time payload encoding, and multi-threaded GUI
#  Post-Quantum Secure Chat & Forensics Tool

A Python-based encrypted chat application built as a Cyber Security / Digital Forensics mini project. It demonstrates a *post-quantum key exchange (Kyber512 / ML-KEM)* combined with *AES encryption (Fernet), plus a built-in **forensic logging module* that records entropy and hash values for every message sent.



##  Table of Contents

- [ Overview](#-overview)
- [ Tech Stack](#-tech-stack)
- [ Step-by-Step Build Process](#-step-by-step-build-process)
- [ Project Structure](#-project-structure)
- [ Setup & Installation](#-setup--installation)
- [ How to Run](#️-how-to-run)
- [ What This Project Proves](#️-what-this-project-proves)
- [ Threat Model & Known Limitations](#️-threat-model--known-limitations)
- [ Future Work](#-future-work)
- [ Author](#-author)



##  Overview

Two peers — a *Server* and a *Client* — connect over a TCP socket and exchange messages that are:

1. Protected by a *quantum-resistant key exchange* (Kyber512), so the shared secret itself is never sent in plaintext over the network.
2. Encrypted with *Fernet (AES + HMAC)* using a key derived from that shared secret via *HKDF-SHA256*.
3. Logged for *forensic analysis* — every message's ciphertext is run through Shannon entropy and SHA-256 hashing, with a timestamped audit trail written to forensic_logs.txt.

The project ships in two interchangeable forms:
- *CLI version* — server.py + client.py (terminal based)
- *GUI version* — gui_chat.py (Tkinter window, single file, mode selectable as Server or Client)

Both versions share the same cryptographic and forensic core in pqc_helper.py.

> * In short:* Server & Client agree on a secret key using quantum-safe math (Kyber512) → that secret becomes an AES key (Fernet) → every message is encrypted with it → every message is also fingerprinted (entropy + SHA-256) and saved to a forensic log file.


##  Tech Stack

 Part                      |  Tool
 Language                  | Python 3 
 Post-Quantum KEM          | Kyber512 (kyber-py) 
 Symmetric Encryption      | cryptography library (Fernet — AES + HMAC) 
 Key Derivation            | HKDF-SHA256 
 Networking                | Python socket 
 GUI                       | tkinter 
 Concurrency               | threading (keeps GUI/CLI responsive while chatting) 
 Forensics                 | Shannon Entropy + SHA-256 (custom module) 
 Environment               | venv 



##  Step-by-Step Build Process

This project was not written in one shot — it grew in stages, with each layer tested before the next was added. Below is the exact build order, including the dead ends that came up along the way (kept here because they're useful for the viva — they explain why the final code looks the way it does).

### Step 1 — Project folder & virtual environment
Created a PostQuantumSecureChat folder and set up an isolated Python environment:
powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python -m venv venv
.\venv\Scripts\Activate.ps1


### Step 2 — Prove basic encryption works (test.py)
Before touching networking, a standalone script confirmed Fernet encryption/decryption worked:
python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
message = b"Post-Quantum Secure Chat Testing!"
encrypted = cipher.encrypt(message)
decrypted = cipher.decrypt(encrypted)

Output confirmed the message round-tripped correctly.

### Step 3 — Plain (unencrypted) chat first — server.py + client.py
A bare socket server and client were built first, just to confirm two processes could talk to each other over 127.0.0.1:5000. At this stage messages were sent as *plain text* — no security at all — purely to validate the networking layer in isolation.

### Step 4 — Add encryption on top — secure_server.py + secure_client.py
The same socket logic was upgraded: the server generates one Fernet.generate_key() for the session and *sends it directly to the client* right after connecting. Every message after that is encrypted with that shared key. This proved encryption worked over the wire, but it had an obvious weakness — the key itself travels in the clear, so anyone snooping the connection at that exact moment could grab it.

### Step 5 — Wrap it in a GUI — first QuantumChatApp (Tkinter)
The same "server generates a Fernet key and sends it raw" logic was wrapped in a Tkinter window with *Start as Server* / *Connect as Client* buttons, a scrolling chat log, and a message box — so both sides could chat like a real app instead of a terminal.

### Step 6 — Naming the project
A few project names were considered before settling on the final one:
- AegisQuantum-Chat
- CipherPulse-PQC
- *Post-Quantum Secure Chat & Forensics Tool*  (final)

### Step 7 — Replace the raw key hand-off with real PQC (Kyber512)
This was the biggest and most iterative step. Sending the Fernet key directly (Step 4/5) is not post-quantum-safe — the goal was to replace it with a proper *Kyber512 key encapsulation mechanism (KEM), so only a *public key and a KEM ciphertext ever cross the network, never the secret itself.


Final, correct flow (documented directly in pqc_helper.py as a comment so it's never lost again):
python
pk, sk   = Kyber512.keygen()
key, c   = Kyber512.encaps(pk)     # shared KEY comes first, ciphertext second
key      = Kyber512.decaps(sk, c)  # secret key comes first, ciphertext second


### Step 8 — Rebuild pqc_helper.py as the shared crypto + forensics core
Once the Kyber API was confirmed working, pqc_helper.py became the single source of truth, exposing:
- generate_kyber_keys(), encapsulate_kyber(), decapsulate_kyber() — the PQC handshake
- derive_fernet_key() — HKDF-SHA256 turns the Kyber shared secret into a Fernet-compatible AES key
- calculate_entropy(), calculate_sha256(), generate_hex_dump() — the forensic primitives
- log_forensics() — ties the above together into one timestamped log entry per message

### Step 9 — Rebuild the CLI Server/Client on top of pqc_helper
server.py and client.py were rewritten to import from pqc_helper instead of doing raw Fernet key hand-off:
1. Server generates a Kyber keypair and sends the *public key* only.
2. Client encapsulates a shared secret against that public key and sends back the *ciphertext* only.
3. Server decapsulates to arrive at the same shared secret.
4. Both derive the same Fernet key via HKDF and chat normally from there — with log_forensics() called on every message sent and received.

### Step 10 — Forensic logging goes live
log_forensics(sender, plaintext, ciphertext_bytes) was wired into the receive loop and the send loop on both CLI and GUI versions, so every message — incoming or outgoing — is automatically entropy-checked, hashed, and appended to forensic_logs.txt with a timestamp.

### Step 11 — Rebuild the GUI on PQC — pqc_gui_chat.py
The Tkinter GUI from Step 5 was rewritten to use the new pqc_helper handshake and forensic logging instead of the old raw-key hand-off, with the entropy value now shown inline under each received message bubble.

### Step 12 — Debugging the GUI build
A few real bugs came up once the GUI was rebuilt, found and fixed with PowerShell:
- __init__ typo: an early version had def __init__(self): instead of def __init__(self, root):, so the window never received its parent. Found with:
  powershell
  Select-String -Path pqc_gui_chat.py -Pattern "def __init__"
  
  and fixed with:
  powershell
  (Get-Content pqc_gui_chat.py) -replace 'def __init__\(self\):', 'def __init__(self, root):' | Set-Content pqc_gui_chat.py
  
- Geometry string bug*: self.root.geometry("600×500") used the multiplication sign × instead of a plain x — Tkinter needs "WIDTHxHEIGHT" literally, so this was corrected to "600x500".

### Step 13 — Final hardening pass
A last round of fixes made the app stable enough for a live demo:
- SO_REUSEADDR added to the server socket so restarting the app doesn't hit "Address already in use".
- Receive buffer bumped from 2048 → 4096 bytes, since some Kyber public keys/ciphertexts exceeded the old limit.
- messagebox calls moved onto the main thread via root.after(0, ...), since popping a dialog from a background thread can freeze or crash Tkinter.
- A guard added in send_message() so the app can't try to encrypt/send before the handshake has finished (self.cipher is None check).
- on_close() handler added via root.protocol("WM_DELETE_WINDOW", ...) so both sockets close cleanly when the window is closed, instead of leaving the port stuck.

### Step 14 — Forensic module logic, standalone
log_forensics() was finalized to always write entries in this format:

[2026-08-29 14:32:10] Sender: Client
│  Plaintext  : Hello, secure world!
│  Entropy    : 7.8524
└─ SHA-256    : 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
--------------------------------------------------

The GUI version also displays the entropy value inline under each received message for a live forensic view.



##  Project Structure


PostQuantumSecureChat/
│
├── venv/
├── pqc_helper.py     # Kyber512 key exchange + Fernet key derivation + forensic module
├── gui_chat.py        # Tkinter GUI — Server/Client mode in one app
├── client.py          # CLI client
├── server.py           # CLI server
├── forensic_logs.txt   # Auto-generated forensic audit trail
└── requirements.txt




##  Setup & Installation

bash
# 1. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1      # PowerShell (Windows)

# If script execution is blocked on Windows, run once:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Install dependencies
pip install cryptography kyber-py




##  How to Run

### GUI Version (recommended)
bash
python gui_chat.py

Open two instances of the app. Click *Start as Server* on one, *Connect as Client* on the other. Once you see "PQC Secure Handshake Successful!", start chatting — every message is end-to-end encrypted and forensically logged in the background.

### CLI Version
bash
# Terminal 1
python server.py

# Terminal 2
python client.py




##  What This Project Proves

- A shared encryption key can be established over an insecure channel *without ever transmitting the key itself*, using a post-quantum key encapsulation mechanism.
- Messages are encrypted before they leave the sender and decrypted only after arriving — a network eavesdropper only ever sees ciphertext.
- Fernet's built-in authentication means a tampered message fails to decrypt rather than producing corrupted plaintext.
- Every transmitted message can be forensically fingerprinted (entropy + hash) and logged for chain-of-custody style analysis — connecting the cryptography work directly to a digital forensics use case.



##  Threat Model & Known Limitations

- *Harvest-now, decrypt-later*: this project's core motivation — data encrypted with classical-only key exchange today could be decrypted retroactively once large-scale quantum computers exist. Kyber512 mitigates this for the key exchange step.
- *No authentication yet: the current handshake does not verify *who holds the public key, so it is still vulnerable to an active man-in-the-middle who can intercept the initial exchange. A future version should add digital signatures (e.g., Dilithium/ML-DSA) to authenticate each side.
- *No forward secrecy across sessions*: a new Kyber keypair is generated per session, but there is no ratcheting within a session.
- This is an educational/mini-project implementation, not intended for production security use.


##  Future Work

- Add authentication via post-quantum digital signatures (ML-DSA / Dilithium) to prevent MITM on the handshake.
- Hybrid key exchange combining classical ECDH (X25519) with Kyber, derived jointly via HKDF (TLS 1.3-style migration approach).
- Upgrade symmetric layer to AES-256-GCM or ChaCha20-Poly1305 directly on the derived key.
- Per-session ephemeral keys with forward secrecy (simplified double-ratchet style).
- Encrypted file transfer / vault feature.
- Password-based login with Argon2id.
- Side-by-side hex dump viewer for plaintext vs. ciphertext in the GUI.

##  Author

Built by Preethi as a hands-on Cyber Security + Digital Forensics learning project, combining post-quantum cryptography with forensic log analysis.
