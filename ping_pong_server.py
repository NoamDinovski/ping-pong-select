"""
Name: ping_pong_server.py

Purpose: Solution for Ping Pong.

Usage: ping_pong_server.py

Author: 24
Created: 28/01/2020
"""

import select
import socket
import sys

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

def select_for_read(sockets, timeout):
    length = len(sockets)
    reads = []
    while length > 0:
        reads_temp, _, _ = select.select(sockets[max(0, length - MAX_FDS):length], [], [], timeout)
        reads += reads_temp
        length -= MAX_FDS
    return reads


def poll_for_read(poll_object, timeout):
    poll_object.poll()


def select_for_write(sockets, timeout):
    length = len(sockets)
    writes = []
    while length > 0:
        _, writes_temp, _ = select.select([], sockets[max(0, length - MAX_FDS):length], [], timeout)
        writes += writes_temp
        length -= MAX_FDS
    return writes


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ANY_INTERFACE, PORT))
        sock.setblocking(False)
        sock.listen(MAX_CONNECTIONS)
        print("Listening.")

        clients = []

        use_poll = is_poll_object_supported()

        if use_poll:
            poll = select.poll()

        while True:
            readable = select_for_read([sock], POLL_TIMEOUT)
            if readable:
                client_socket = sock.accept()[0]
                print(f"Accepted connection from {client_socket.getpeername()} "
                      f"with File Descriptor: {client_socket.fileno()}")
                client_socket.setblocking(False)
                clients.append(client_socket)

            if not clients:
                continue

            readable_connections = select_for_read(clients, POLL_TIMEOUT)
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

            connections_to_pop = []

            for index, data in enumerate(connection_data):
                log_connection(readable_connections[index], f"Received message: {data}")
                if data != CLIENT_MESSAGE:
                    log_connection(readable_connections[index], f"Invalid message. Closing connection.")
                    close_connection(clients, readable_connections[index])
                    connections_to_pop.append(readable_connections[index])

            readable_connections = [conn for conn in readable_connections if conn not in connections_to_pop]

            if not readable_connections:
                continue

            writable_connections = select_for_write(readable_connections, POLL_TIMEOUT)
            for client_socket in writable_connections:
                log_connection(client_socket, f"Sending back {SERVER_REPLY}")
                try:
                    client_socket.sendall(SERVER_REPLY.encode())
                except OSError as err:
                    log_connection(client_socket, f"An error has occurred: {err}")
                    close_connection(clients, client_socket)


if __name__ == '__main__':
    main()
