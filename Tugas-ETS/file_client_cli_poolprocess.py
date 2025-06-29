import os
import socket
import json
import base64
import logging

server_address=('0.0.0.0',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        command_str = command_str + "\r\n\r\n"
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(65536)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False


def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filename=""):
    if not os.path.exists(filename):
        logging.warning("File does not exist")
        return False
    with open(filename, "rb") as fp:
        file_content = fp.read()
    encoded_content = base64.b64encode(file_content).decode()
    command_str = f"UPLOAD {filename} {encoded_content}"
    hasil = send_command(command_str)
    if hasil and hasil.get('status') == 'OK':
        print(hasil['data'])
        return True
    else:
        print(hasil['data'])
        return False

def remote_delete(filename=""):
    command_str=f"DELETE {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print(hasil['data'])
        return True
    else:
        print(hasil['data'])
        return False

def worker(worker_id, server_address, download_file, upload_file, upload_size):
    import os
    try:
        # Download
        download_success = remote_get(download_file)
        download_size = os.path.getsize(download_file) if download_success and os.path.exists(download_file) else 0
        # Upload
        upload_success = remote_upload(upload_file)
        # Worker is successful only if both succeed
        all_success = download_success and upload_success
        total_bytes = download_size + (upload_size if upload_success else 0)
        return {
            'worker_id': worker_id,
            'success': all_success,
            'bytes': total_bytes
        }
    except Exception as e:
        return {
            'worker_id': worker_id,
            'success': False,
            'bytes': 0,
            'error': str(e)
        }

if __name__=='__main__':
    import concurrent.futures
    import time

    server_address=('172.16.16.101',8889)

    NUM_WORKERS = 50  # Number of concurrent workers
    DOWNLOAD_FILE = '10mb_file'
    UPLOAD_FILE = '10mb_file'

    upload_size = os.path.getsize(UPLOAD_FILE) if os.path.exists(UPLOAD_FILE) else 0

    start_all = time.perf_counter()
    worker_success = 0
    worker_fail = 0
    total_bytes = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [
            executor.submit(worker, i+1, server_address, DOWNLOAD_FILE, UPLOAD_FILE, upload_size)
            for i in range(NUM_WORKERS)
        ]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res['success']:
                worker_success += 1
                total_bytes += res['bytes']
            else:
                worker_fail += 1
                if 'error' in res:
                    print(f"Worker {res['worker_id']} failed with error: {res['error']}")

    end_all = time.perf_counter()
    total_time = end_all - start_all
    throughput = total_bytes / total_time if total_time > 0 else 0

    print(f"\nStress Test Summary:")
    print(f"Total workers: {NUM_WORKERS}")
    print(f"Workers succeeded: {worker_success}")
    print(f"Workers failed: {worker_fail}")
    print(f"Total bytes transferred: {total_bytes} bytes")
    print(f"Total time: {total_time:.4f} seconds")
    print(f"Throughput: {throughput:.2f} bytes/sec")
