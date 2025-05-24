import json
import logging
import shlex

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""



class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
       
    def proses_string(self, string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")
        try:
            parts = string_datamasuk.strip().split(' ', 2)
            c_request = parts[0].strip().lower()
            if len(parts) == 1:
                params = []
            elif len(parts) == 2:
                params = [parts[1]]
            else:
                params = [parts[1], parts[2]]
            logging.warning(f"memproses request: {c_request}")
            logging.warning(f"Params: {params}")
            cl = getattr(self.file, c_request)(params)
            return json.dumps(cl)
        except Exception as e:
            logging.warning(f"Exception: {e}")
            return json.dumps(dict(status='ERROR', data='request tidak dikenali'))


if __name__=='__main__':
    msg = 'spare15'
    #contoh pemakaian
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string('UPLOAD testfile.txt "goodmorning"'))
