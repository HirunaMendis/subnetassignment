
import socket
import os
import threading

# Server settings
SERVER_HOST = 'localhost'
SERVER_PORT = 5001

# Directory where the server will save files (DEF folder)
SERVER_FILE_DIR = "server"  # Directory where the server looks for files to send

# Ensure the server directory exists
if not os.path.exists(SERVER_FILE_DIR):
    os.makedirs(SERVER_FILE_DIR)

def handle_client(client_socket, client_address):
    """Handle file requests from the client."""
    print(f"New connection from {client_address}")

    while True:
        # Receive the command
        command = client_socket.recv(1024).decode('utf-8')

        if command == 'SEND':
            filename = client_socket.recv(1024).decode('utf-8')
            filesize = int(client_socket.recv(1024).decode('utf-8'))

            # Define the file path for saving the received file (in DEF folder)
            file_path = os.path.join(SERVER_FILE_DIR, filename)

            # Ensure the folder exists
            if not os.path.exists(SERVER_FILE_DIR):
                os.makedirs(SERVER_FILE_DIR)

            # Receive the file data in chunks and save it
            with open(file_path, 'wb') as f:
                bytes_received = 0
                while bytes_received < filesize:
                    data = client_socket.recv(1024)
                    f.write(data)
                    bytes_received += len(data)
            print(f"Received file '{filename}' and saved to '{SERVER_FILE_DIR}'")

        elif command == 'REQUEST':
            filename = client_socket.recv(1024).decode('utf-8')

            # Server will always send the file from the DEF folder
            file_path = os.path.join(SERVER_FILE_DIR, filename)

            if os.path.exists(file_path):
                # Send the file size to the client
                filesize = os.path.getsize(file_path)
                client_socket.send(b'EXISTS')
                client_socket.send(str(filesize).encode('utf-8'))

                # Send the file in chunks
                with open(file_path, 'rb') as f:
                    bytes_read = f.read(1024)
                    while bytes_read:
                        client_socket.send(bytes_read)
                        bytes_read = f.read(1024)
                print(f"Sent file '{filename}' to client.")
            else:
                client_socket.send(b'NOT_EXISTS')
                print(f"File '{filename}' not found in {SERVER_FILE_DIR}")

        elif command == 'QUIT':
            print(f"Client {client_address} disconnected.")
            break

    client_socket.close()

def start_server():
    """Start the server and handle client connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
