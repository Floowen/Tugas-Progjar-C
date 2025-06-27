from socket import *
import socket
import threading
import logging
from datetime import datetime

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                d = b''
                while not d.endswith(b'\r\n'):
                    data = self.connection.recv(32)
                    if not data:
                        break
                    d += data

                text = d.decode('utf-8').strip()
                logging.warning(f"Received from {self.address}: {text}")

                if text == 'TIME':
                    time_string = datetime.now().strftime("%H:%M:%S")
                    response = f"JAM {time_string}\r\n"
                    self.connection.sendall(response.encode('utf-8'))
                elif text == 'QUIT':
                    logging.warning(f"Connection closed by client: {self.address}")
                    break
                else:
                    self.connection.sendall(b"Invalid command\r\n")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            self.connection.close()

class Server(threading.Thread):
    def __init__(self):
        self.the_clients = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        server_address = ('0.0.0.0', 45000)
        self.sock.bind(server_address)
        self.sock.listen(1)
        logging.warning(f"starting up on {server_address}")
        while True:
            connection, client_address = self.sock.accept()
            logging.warning(f"Connection from {client_address}")

            clt = ProcessTheClient(connection, client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    svr = Server()
    svr.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format='%(message)s')
    main()