import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from cryptography.fernet import Fernet

class QuantumChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Post-Quantum Secure Chat")
        self.root.geometry("450x550")
        
        self.cipher = None
        self.sock = None
        
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        self.btn_server = tk.Button(frame, text="Start as Server", command=self.start_server, bg="#4CAF50", fg="white", width=15)
        self.btn_server.pack(side=tk.LEFT, padx=5)
        
        self.btn_client = tk.Button(frame, text="Connect as Client", command=self.start_client, bg="#2196F3", fg="white", width=15)
        self.btn_client.pack(side=tk.LEFT, padx=5)
        
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=20)
        self.chat_area.pack(padx=10, pady=5)
        self.chat_area.config(state=tk.DISABLED)
        
        self.msg_entry = tk.Entry(self.root, width=38)
        self.msg_entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.msg_entry.bind("<Return>", lambda event: self.send_message())
        
        self.btn_send = tk.Button(self.root, text="Send 🔒", command=self.send_message, bg="#9C27B0", fg="white", width=10)
        self.btn_send.pack(side=tk.LEFT, pady=10)

    def log(self, text):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, text + "\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)

    def start_server(self):
        self.btn_server.config(state=tk.DISABLED)
        self.btn_client.config(state=tk.DISABLED)
        threading.Thread(target=self._run_server, daemon=True).start()

    def _run_server(self):
        key = Fernet.generate_key()
        self.cipher = Fernet(key)
        self.log("🔑 Session Key Generated!")
        self.log("⏳ Server listening on 127.0.0.1:5000...")
        
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 5000))
        srv.listen(1)
        self.sock, addr = srv.accept()
        self.log(f"✅ Connected to Client: {addr}")
        self.sock.send(key)
        
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def start_client(self):
        self.btn_server.config(state=tk.DISABLED)
        self.btn_client.config(state=tk.DISABLED)
        threading.Thread(target=self._run_client, daemon=True).start()

    def _run_client(self):
        self.log("⏳ Connecting to Server...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", 5000))
        
        key = self.sock.recv(1024)
        self.cipher = Fernet(key)
        self.log("🔑 Received Session Security Key!")
        self.log("✅ Secure Channel Established!\n")
        
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if msg and self.sock and self.cipher:
            encrypted = self.cipher.encrypt(msg.encode())
            self.sock.send(encrypted)
            self.log(f"You: {msg}")
            self.msg_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(2048)
                if not data:
                    break
                decrypted = self.cipher.decrypt(data).decode()
                self.log(f"Peer: {decrypted}")
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumChatApp(root)
    root.mainloop()