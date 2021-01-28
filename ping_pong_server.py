"""
Name: ping_pong_server.py

Purpose: Solution for Ping Pong.

Usage: ping_pong_server.py

Author: 24
Created: 28/01/2020
"""

import select
import socket

ANY_INTERFACE = ""
PORT = 1337

CLIENT_MESSAGE = "ping"
CLIENT_MESSAGE_TIMEOUT = 5.0

SERVER_REPLY = "pong"

MAX_CONNECTIONS = 100
POLL_TIMEOUT = 0.0

BUFFER_SIZE = 1024


def log_connection(connection_socket, message):
    """
    Logs a message for a specified connection with a socket.

    :param socket.socket connection_socket: The socket.
    :param str message: The message to log.
    """
    print(f"{connection_socket.getpeername()}: {message}")


def close_connection(connections, connection_socket):
    """
    Closes a connection from a socket and removes it from the given connection list.
    :param list connections: The list of connected sockets to remove the connection from.
    :param socket.socket connection_socket: The connection socket to close.
    :return:
    """
    connection_socket.shutdown(socket.SHUT_RDWR)
    connection_socket.close()
    connections.remove(connection_socket)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ANY_INTERFACE, PORT))
        sock.setblocking(False)
        sock.listen(MAX_CONNECTIONS)
        print("Listening.")

        clients = []

        while True:
            readable, _, _ = select.select([sock], [], [], POLL_TIMEOUT)
            if readable:
                client_socket = sock.accept()[0]
                print(f"Accepted connection from {client_socket.getpeername()} "
                      f"with File Descriptor: {client_socket.fileno()}")
                client_socket.setblocking(False)
                clients.append(client_socket)

            if not clients:
                continue

            readable_connections, _, _ = select.select(clients, [], [], POLL_TIMEOUT)
            connection_data = []
            for client_socket in clients:
                if client_socket in readable_connections:
                    try:
                        data = client_socket.recv(BUFFER_SIZE).decode()
                        connection_data.append(data)
                    except OSError as err:
                        log_connection(client_socket, f"An error has occurred: {err}")
                        close_connection(clients, client_socket)
                        readable_connections.remove(client_socket)

            for index, data in enumerate(connection_data):
                log_connection(readable_connections[index], f"Received message: {data}")
                if data != CLIENT_MESSAGE:
                    log_connection(readable_connections[index], f"Invalid message. Closing connection.")
                    close_connection(clients, readable_connections[index])
                    readable_connections.pop(index)

            if not readable_connections:
                continue

            _, writable_connections, _ = select.select([], readable_connections, [], POLL_TIMEOUT)
            for client_socket in writable_connections:
                log_connection(client_socket, f"Sending back {SERVER_REPLY}")
                try:
                    client_socket.sendall(SERVER_REPLY.encode())
                except OSError as err:
                    log_connection(client_socket, f"An error has occurred: {err}")


if __name__ == '__main__':
    main()
