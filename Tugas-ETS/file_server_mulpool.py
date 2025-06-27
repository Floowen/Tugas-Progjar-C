import threading
import logging
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from socket import *
import socket

from file_protocol import  FileProtocol
fp = FileProtocol()

def ProcessTheClient(connection):
    buffer= b""
    try:
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
        return True
    except Exception as e:
        logging.warning(f"Error processing client: {e}")
        try:
            connection.close()
        except:
            pass
        return False

class Server(threading.Thread):
    success_count = 0
    fail_count = 0
    counter_lock = threading.Lock()

    def __init__(self,ipaddress='0.0.0.0',port=8889, max_workers=50):
        self.ipinfo=(ipaddress,port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(100)
        try:
            while True:
                self.connection, self.client_address = self.my_socket.accept()
                logging.warning(f"connection from {self.client_address}")
                self.executor.submit(self.process_and_count, self.connection)
        except Exception as e:
            logging.warning(f"server stopped: {e}")
        finally:
            print(f"Success: {Server.success_count}, Failed: {Server.fail_count}")

    def process_and_count(self, connection):
        result = ProcessTheClient(connection)
        with Server.counter_lock:
            if result:
                Server.success_count += 1
            else:
                Server.fail_count += 1

def main():
    svr = Server()
    svr.start()
    svr.join()

if __name__ == "__main__":
    main()