from flask import Flask, request, jsonify
import socket
import threading

app = Flask(__name__)

# Maintain a list of connected clients
connected_clients = set()

def handle_client(client_socket):
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if not data:
            break
        message = data.decode('utf-8')
        print(f"Received from client: {message}")

        # Send a response back to the client
        response = "Server received: " + message
        client_socket.send(response.encode('utf-8'))

    # Remove the client from the connected_clients set when the connection is closed
    connected_clients.remove(client_socket)
    client_socket.close()

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message', '')
    
    # Send the message to all connected clients
    for client_socket in connected_clients:
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message to client: {str(e)}")

    return jsonify({'status': 'success'})

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    print("Server listening on port 5000")

    while True:
        client_socket, addr = server.accept()
        connected_clients.add(client_socket)

        # Start a new thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()