import socket
import time
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 12345        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024) # Receive up to 1024 bytes
            print(f"Received: {data.decode()}") # Decode bytes to string
            time.sleep(2)
            conn.sendall(data) # Send back the received data (echo)