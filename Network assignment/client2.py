import socket
import os

def send_file(client_socket):
    """Send a file to the server."""
    filename = input("Enter the filename to send (e.g., sample1): ").strip()

    # Set the directory from which the client sends files (ABC folder)
    send_file_dir = "client"  # Directory where the client looks for files to send
    
    # Check if the file exists in the directory
    file_path = os.path.join(send_file_dir, filename)
    if not os.path.exists(file_path):
        print(f"Error: File '{filename}' not found in the '{send_file_dir}' folder!")
        return

    # Send 'SEND' command to the server
    client_socket.send(b'SEND')

    # Send the filename to the server
    client_socket.send(filename.encode('utf-8'))

    # Send the file size
    filesize = os.path.getsize(file_path)
    client_socket.send(str(filesize).encode('utf-8'))

    # Send the file in chunks
    with open(file_path, 'rb') as f:
        bytes_read = f.read(1024)
        while bytes_read:
            client_socket.send(bytes_read)
            bytes_read = f.read(1024)
    print(f"Sent file '{filename}' from '{send_file_dir}' to the server.")

def request_file(client_socket):
    """Request a file from the server."""
    filename = input("Enter the filename to request (e.g., sample2): ").strip()

    # Set the directory where the client will save the received files (ABC folder)
    receive_file_dir = "client"  # Directory where the client will save the received files

    # Ensure the directory exists
    if not os.path.exists(receive_file_dir):
        os.makedirs(receive_file_dir)

    # Send 'REQUEST' command to the server
    client_socket.send(b'REQUEST')

    # Send the filename to request
    client_socket.send(filename.encode('utf-8'))

    # Wait for the server's response
    response = client_socket.recv(1024)

    if response == b'EXISTS':
        # Receive the file size
        filesize = int(client_socket.recv(1024).decode('utf-8'))

        # Define the path to save the file
        save_path = os.path.join(receive_file_dir, 'received_' + filename)

        # Receive the file data in chunks
        with open(save_path, 'wb') as f:
            bytes_received = 0
            while bytes_received < filesize:
                data = client_socket.recv(1024)
                f.write(data)
                bytes_received += len(data)
        print(f"Received file '{filename}' and saved to '{receive_file_dir}' as 'received_{filename}'")
    else:
        print("File not found on server.")

def main():
    """Main function to interact with the client."""
    server_ip = "localhost"
    server_port = 5001

    # Create the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the server
    try:
        client_socket.connect((server_ip, server_port))
        print(f"Connected to server at {server_ip}:{server_port}")
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return

    while True:
        action = input("Enter 'send' to send a file, 'request' to request a file, or 'quit' to exit: ").strip().lower()

        if action == 'send':
            send_file(client_socket)

        elif action == 'request':
            request_file(client_socket)

        elif action == 'quit':
            client_socket.send(b'QUIT')
            break

        else:
            print("Invalid action. Please enter 'send', 'request', or 'quit'.")

    client_socket.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
