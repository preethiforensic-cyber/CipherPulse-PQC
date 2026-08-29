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