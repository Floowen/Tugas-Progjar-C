import socket
import threading
import logging

logging.basicConfig(level=logging.INFO) 

def client_thread(name):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('172.16.16.101', 45000)
        logging.info(f"[{name}] Connecting to {server_address}")
        sock.connect(server_address)

        sock.sendall(b"TIME\r\n")
        response = sock.recv(32).decode('utf-8')
        logging.info(f"[{name}] Received: {response.strip()}")

        sock.sendall(b"QUIT\r\n")
        sock.close()
        logging.info(f"[{name}] Disconnected")

    except Exception as e:
        logging.error(f"[{name}] Error: {e}")

def main():
    threads = []
    for i in range(10):
        t = threading.Thread(target=client_thread, args=(f"Client-{i+1}",))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()