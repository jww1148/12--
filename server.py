# server.py
import socket
import argparse
import os

FLAGS = _ = None
DEBUG = False
MTU = 1500
FILE_DIR = "C:/Users/jww11/Desktop/사진"

def load_file_info():
    files = {}
    for fname in os.listdir(FILE_DIR):
        path = os.path.join(FILE_DIR, fname)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            files[fname] = {'path': path, 'size': size}
    return files

def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {FLAGS.address}:{FLAGS.port}...')

    file_info = load_file_info()

    while True:
        data, client = sock.recvfrom(2**16)
        message = data.decode('utf-8')
        print(f'Received: {message} from {client}')

        if message.startswith("INFO "):
            filename = message[5:].strip()
            if filename in file_info:
                size_str = str(file_info[filename]['size'])
                sock.sendto(size_str.encode('utf-8'), client)
            else:
                sock.sendto("404 Not Found".encode('utf-8'), client)

        elif message.startswith("DOWNLOAD "):
            filename = message[9:].strip()
            if filename not in file_info:
                sock.sendto("404 Not Found".encode('utf-8'), client)
                continue
            path = file_info[filename]['path']
            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(MTU)
                    if not chunk:
                        break
                    sock.sendto(chunk, client)
            print(f'Finished sending {filename} to {client}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Print debug messages')
    parser.add_argument('--address', type=str, default='0.0.0.0', help='Bind address')
    parser.add_argument('--port', type=int, default=3034, help='Port to listen on')
    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
