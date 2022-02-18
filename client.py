from inspect import cleandoc
import sys
import socket
import errno
from datetime import datetime
import threading

def send_message():
    while True:
        message = input()
        if len(message) > 0:
            message = message.encode("utf-8")
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(message_header + message)

def receive_message():
    while True:
        try:
            # Receive our "header" containing the length of the username
            username_header = client_socket.recv(HEADER_LENGTH)
            # If we received no data, client is disconnected
            if not len(username_header):
                print("Connection closed by the server")
                client_socket.close()

            username_length = int(username_header.decode("utf-8").strip())
            # Receive the username
            username = client_socket.recv(username_length).decode("utf-8")

            # Receive the message
            message_header = client_socket.recv(HEADER_LENGTH)
            message_lenght = int(message_header.decode("utf-8").strip())
            message = client_socket.recv(message_lenght).decode("utf-8")
            # Print the received message with username
            print(f"{username} > {message}")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error', str(e))
                client_socket.close()
        except Exception as e:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print(f"\n[{dt_string}] {e}")
            client_socket.close()

def join_room():
    username = input("Enter your username: ")
    un_encoded = username.encode('utf-8')
    username_header = f"{len(un_encoded):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + un_encoded)
    print("You joined the chat!")

    t = threading.Thread(target=receive_message)
    t1 = threading.Thread(target=send_message)
    t.start()
    t1.start()

if __name__ == '__main__':
    menu = cleandoc("""
    1. Join room
    2. Create room
    3. Exit\n""")
    choice = input(menu)
    if choice == '1':
        # Set up the socket
        HEADER_LENGTH = 10
        IP = "127.0.0.1"
        PORT = 1234
        # Create a socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        client_socket.setblocking(False)
        join_room()

    elif choice == '2':
        print()
    elif choice == '3':
        sys.exit()