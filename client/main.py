import socket
import sys

SERVER_HOST = 'localhost'
SERVER_PORT = 9090


def run():
    sock = socket.socket()
    try:
        print(F'Establishing connection with {SERVER_HOST}:{SERVER_PORT}...', end='')
        sys.stdout.flush()
        sock.connect((SERVER_HOST, SERVER_PORT))
        print(' done!')

        sock.send(b'KEK\r\n')

        data = sock.recv(1024)
    except ConnectionRefusedError:
        print(' connection refused :(')
    finally:
        sock.close()

    pass


if __name__ == '__main__':
    run()
