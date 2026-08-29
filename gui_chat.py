import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from cryptography.fernet import Fernet
from pqc_helper import generate_kyber_keys, encapsulate_kyber, decapsulate_kyber, derive_fernet_key, log_forensics


class PQCChatApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Post-Quantum Secure Chat & Forensics")
        self.root.geometry("600x500")  # FIX: was "600\u00d7500" (× instead of x) -> Tkinter needs "WIDTHxHEIGHT"

        self.conn = None
        self.client_socket = None
        self.cipher = None
        self.is_server = False

        # --- UI Layout ---
        # 1. Mode Selection Frame
        self.mode_frame = tk.LabelFrame(root, text="Select Mode", padx=10, pady=10)
        self.mode_frame.pack(fill="x", padx=10, pady=10)

        self.btn_server = tk.Button(self.mode_frame, text="Start as Server", bg="lightblue", command=self.setup_server)
        self.btn_server.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_client = tk.Button(self.mode_frame, text="Connect as Client", bg="lightgreen", command=self.setup_client)
        self.btn_client.pack(side="right", expand=True, fill="x", padx=5)

        # 2. Chat Log Area
        self.chat_display = scrolledtext.ScrolledText(root, state='disabled', wrap='word', bg="#f4f4f4")
        self.chat_display.pack(expand=True, fill='both', padx=10, pady=5)

        # 3. Message Input Frame
        self.input_frame = tk.Frame(root, padx=10, pady=10)
        self.input_frame.pack(fill="x", padx=10)

        self.msg_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.msg_entry.pack(side="left", expand=True, fill='x', padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = tk.Button(self.input_frame, text="Send", bg="green", fg="white",
                                   font=("Arial", 10, "bold"), command=self.send_message)
        self.send_btn.pack(side="right")

        # Disable input initially until connected
        self.toggle_input(False)

        # FIX: close sockets cleanly when window is closed, so port doesn't stay stuck in use
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_input(self, state):
        """Enable or disable typing based on connection state"""
        st = 'normal' if state else 'disabled'
        self.msg_entry.config(state=st)
        self.send_btn.config(state=st)

    def append_chat(self, sender, message, entropy=None):
        """Append messages to UI chat box"""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"[{sender}]: {message}\n")
        if entropy:
            self.chat_display.insert(tk.END, f" \u2514\u2500 [Forensics] Entropy: {entropy}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def setup_server(self):
        """Initialize Server Mode in a background thread"""
        self.is_server = True
        self.btn_server.config(state='disabled')
        self.btn_client.config(state='disabled')
        self.append_chat("System", "Starting server, waiting for client...")

        threading.Thread(target=self.run_server_socket, daemon=True).start()

    def run_server_socket(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # FIX: allow quick restart of the app without "Address already in use" errors
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('127.0.0.1', 65432))
            server.listen(1)
            self.conn, addr = server.accept()
            self.root.after(0, self.append_chat, "System", f"Connected with Client: {addr}")

            # PQC Key Exchange
            pk, sk = generate_kyber_keys()
            self.conn.sendall(pk)
            ciphertext = self.conn.recv(4096)  # FIX: bumped buffer size, some Kyber variants exceed 2048 bytes
            shared_secret = decapsulate_kyber(ciphertext, sk)

            fernet_key = derive_fernet_key(shared_secret)
            self.cipher = Fernet(fernet_key)

            self.root.after(0, self.append_chat, "System", "PQC Secure Handshake Successful!")
            self.root.after(0, self.toggle_input, True)

            # Start listening for incoming messages
            self.receive_loop(self.conn)
        except Exception as e:
            # FIX: messagebox from a background thread can hang/crash Tkinter; hop back to main thread
            self.root.after(0, messagebox.showerror, "Server Error", str(e))
        finally:
            server.close()

    def setup_client(self):
        """Initialize Client Mode"""
        self.is_server = False
        self.btn_server.config(state='disabled')
        self.btn_client.config(state='disabled')

        threading.Thread(target=self.run_client_socket, daemon=True).start()

    def run_client_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(('127.0.0.1', 65432))
            self.root.after(0, self.append_chat, "System", "Connected to Server.")

            # PQC Key Exchange
            server_pk = self.client_socket.recv(4096)  # FIX: bumped buffer size to match server
            ciphertext, shared_secret = encapsulate_kyber(server_pk)
            self.client_socket.sendall(ciphertext)

            fernet_key = derive_fernet_key(shared_secret)
            self.cipher = Fernet(fernet_key)

            self.root.after(0, self.append_chat, "System", "PQC Secure Handshake Successful!")
            self.root.after(0, self.toggle_input, True)

            # Start listening for incoming messages
            self.receive_loop(self.client_socket)
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Client Error", str(e))

    def receive_loop(self, active_socket):
        """Continuous loop to receive encrypted messages"""
        while True:
            try:
                encrypted_data = active_socket.recv(1024)
                if not encrypted_data:
                    break

                decrypted_msg = self.cipher.decrypt(encrypted_data).decode()
                sender_name = "Client" if self.is_server else "Server"
                entropy = log_forensics(sender_name, decrypted_msg, encrypted_data)

                # Update UI safely from the background thread
                self.root.after(0, self.append_chat, sender_name, decrypted_msg, entropy)
            except Exception:
                break

    def send_message(self):
        """Encrypt and send message through active connection"""
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        # FIX: guard against sending before the handshake/cipher is ready
        if self.cipher is None:
            messagebox.showwarning("Not Connected", "Wait for the secure handshake to finish before sending.")
            return

        try:
            encrypted_msg = self.cipher.encrypt(msg.encode())
            sender_name = "Server" if self.is_server else "Client"
            entropy = log_forensics(sender_name, msg, encrypted_msg)

            if self.is_server and self.conn:
                self.conn.sendall(encrypted_msg)
            elif not self.is_server and self.client_socket:
                self.client_socket.sendall(encrypted_msg)
            else:
                messagebox.showwarning("Not Connected", "No active connection to send through.")
                return

            self.append_chat("You", msg, entropy)
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Send Error", str(e))

    def on_close(self):
        """FIX: clean shutdown so sockets/threads don't linger after closing the window"""
        try:
            if self.conn:
                self.conn.close()
            if self.client_socket:
                self.client_socket.close()
        finally:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PQCChatApp(root)
    root.mainloop()