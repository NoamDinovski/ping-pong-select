"""
Name: ping_pong_server.py

Purpose: Solution for Ping Pong.

Usage: ping_pong_server.py

Author: 24
Created: 28/01/2020
"""

import select
import socket

import poller

ANY_INTERFACE = ""
PORT = 1337

CLIENT_MESSAGE = "ping"
CLIENT_MESSAGE_TIMEOUT = 5.0

SERVER_REPLY = "pong"

MAX_CONNECTIONS = 100
POLL_TIMEOUT = 0.0

BUFFER_SIZE = 1024

MAX_FDS = 512


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


def is_poll_object_supported():
    return getattr(select, "poll", None) is not None


def get_poller():
    if is_poll_object_supported():
        return poller.PollPoller()
    return poller.SelectPoller(MAX_FDS)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ANY_INTERFACE, PORT))
        sock.setblocking(False)
        sock.listen(MAX_CONNECTIONS)
        print("Listening.")

        clients = []

        current_poller = get_poller()

        while True:
            current_poller.register([sock])
            readable = current_poller.poll_for_reading(POLL_TIMEOUT)
            current_poller.unregister([sock])
            if readable:
                client_socket = sock.accept()[0]
                print(f"Accepted connection from {client_socket.getpeername()} "
                      f"with File Descriptor: {client_socket.fileno()}")
                client_socket.setblocking(False)
                clients.append(client_socket)

            if not clients:
                continue

            current_poller.register(clients)
            readable_connections = current_poller.poll_for_reading(POLL_TIMEOUT)
            current_poller.unregister(clients)
            connection_data = []
            for connection in readable_connections:
                try:
                    data = connection.recv(BUFFER_SIZE).decode().strip()
                    connection_data.append(data)
                except OSError as err:
                    log_connection(client_socket, f"An error has occurred: {err}")
                    close_connection(clients, connection)
                    readable_connections.remove(connection)

            if not readable_connections:
                continue

            invalid_message_connections = []

            for index, data in enumerate(connection_data):
                log_connection(readable_connections[index], f"Received message: {data}")
                if data != CLIENT_MESSAGE:
                    log_connection(readable_connections[index], f"Invalid message. Closing connection.")
                    close_connection(clients, readable_connections[index])
                    invalid_message_connections.append(readable_connections[index])

            for connection in invalid_message_connections:
                readable_connections.remove(connection)

            current_poller.register(readable_connections)
            writable_connections = current_poller.poll_for_writing(POLL_TIMEOUT)
            current_poller.unregister(readable_connections)
            for client_socket in writable_connections:
                log_connection(client_socket, f"Sending back {SERVER_REPLY}")
                try:
                    client_socket.sendall(SERVER_REPLY.encode())
                except OSError as err:
                    log_connection(client_socket, f"An error has occurred: {err}")
                    close_connection(clients, client_socket)


if __name__ == '__main__':
    main()
