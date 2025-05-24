from socket import *
import socket
import threading
import logging
import time
import sys
from concurrent.futures import ThreadPoolExecutor


from file_protocol import  FileProtocol
fp = FileProtocol()


def ProcessTheClient(connection):
    buffer= b""
    while True:
        data = connection.recv(65536)
        if data:
            buffer += data
            if b"\r\n\r\n" in buffer:
                break
        else:
            break
    if buffer:
        d = buffer.decode()
        hasil = fp.proses_string(d)
        hasil = hasil + "\r\n\r\n"
        connection.sendall(hasil.encode())
    connection.close()

class Server(threading.Thread):
    def __init__(self,ipaddress='0.0.0.0',port=8889, max_workers=5):
        self.ipinfo=(ipaddress,port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(100)
        with ThreadPoolExecutor() as executor:
            try:
                while True:
                    self.connection, self.client_address = self.my_socket.accept()
                    logging.warning(f"connection from {self.client_address}")
                    self.executor.submit(ProcessTheClient, self.connection)
            except Exception as e:
                logging.warning(f"server stopped: {e}")

def main():
    svr = Server()
    svr.start()
    svr.join()


if __name__ == "__main__":
    main()

