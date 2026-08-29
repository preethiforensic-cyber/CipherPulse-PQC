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