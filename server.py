import socket
from datetime import datetime
import select

HEADER_LENGHT = 10
IP = "127.0.0.1"
PORT = 1234

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
print("Server started")

server_list = [server_socket]
user_list = []

clients = {}

def get_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string

def recv_msg(client_socket):
    try:
        # Receive message
        msg_header = client_socket.recv(HEADER_LENGHT)
        # If we received no data
        if not len(msg_header):
            return False
        msg_len = int(msg_header.decode("utf-8").strip())
        return {"header": msg_header, "data": client_socket.recv(msg_len)}
    
    except Exception as e:
        print(f"\n[{get_time()}] {e}")
        pass

while True:
    # Wait for a new connection
    read_socket, _, exception_socket = select.select(server_list, [], server_list)
    # Iterate over the connected clients
    for notified_socket in read_socket:
        # If the socket is the server socket
        if notified_socket == server_socket:
            # Accept the new connection
            client_socket, client_address = server_socket.accept()
            # Receive data from new client
            user = recv_msg(client_socket)

            if user is False:
                continue

            # Add the new client to the list of connected clients
            server_list.append(client_socket)
            user_list.append(user['data'])
            clients[client_socket] = user
            print(f"[{get_time()}] Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}")
        
        # Else if the socket is a client socket
        else:
            # Receive the message
            msg = recv_msg(notified_socket)
            # If the client is disconnected
            if msg is False:
                # Remove the client from the list of connected clients
                print(f"[{datetime.now()}] Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                server_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            try:
                print(f"[{get_time()}] {user['data'].decode('utf-8')}: {msg['data'].decode('utf-8')}")
            except Exception as e:
                print(f"\n[{get_time()}] {e}")

            # Iterate over the list of connected clients
            for client_socket in clients:
                # If the client is not the sender
                if client_socket != notified_socket:
                    try:
                        client_socket.send(user["header"] + user["data"] + msg["header"] + msg["data"])
                    except Exception:
                        client_socket.close()
                        server_list.remove(client_socket)
                        del clients[client_socket]
                        break

    for notified_socket in exception_socket:
        server_list.remove(notified_socket)
        del clients[notified_socket]
