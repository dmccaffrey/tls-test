#!/usr/bin/python
import socket
import ssl
import time
import sys
from pprint import pprint

PATH="/home/redx/dev/tls-test/"
CA_CERTS_FILE = PATH + "ca/intermediate/certs/ca-chain.cert.pem"
SERVER_CERT = PATH + "ca/intermediate/certs/alpha.vmware.local.server.cert.pem"
SERVER_KEY = PATH + "ca/intermediate/private/alpha.vmware.local.key.pem"
CLIENT_CERT = PATH + "ca/intermediate/certs/bravo.vmware.local.usr.cert.pem"
CLIENT_KEY = PATH + "ca/intermediate/private/bravo.vmware.local.key.pem"

def connect(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    s_sock = ssl.wrap_socket(sock, ca_certs=CA_CERTS_FILE, certfile=CLIENT_CERT, keyfile=CLIENT_KEY, cert_reqs=ssl.CERT_REQUIRED)
    s_sock.connect((hostname, port))
    return s_sock

def listen(port):
    sock = socket.socket()
    sock.bind(('', port))
    sock.listen(5)
    return sock

def dump_info(socket):
    print("Peer Name\n" + "-" * 80)
    pprint(socket.getpeername())
    print("\nCipher\n" + "-" * 80)
    pprint(socket.cipher())
    print("\nPeer Certificate\n" + "-" * 80)
    pprint(socket.getpeercert())

def run_client():
    s_sock = connect('localhost', 2243)
    dump_info(s_sock)
    while True:
        time.sleep(1)
        s_sock.write(b"test");

def run_server():
    sock = listen(2243)
    while True:
        n_sock, addr = sock.accept()
        stream = ssl.wrap_socket(n_sock, server_side=True, ca_certs=CA_CERTS_FILE, certfile=SERVER_CERT, keyfile=SERVER_KEY, cert_reqs=ssl.CERT_REQUIRED)
        dump_info(stream)
        try:
            while True:
                print("Received: ", stream.read())
        finally:
            stream.shutdown(socket.SHUT_RDWR)
            stream.close()

if __name__ == "__main__":
    if sys.argv[1] == "client":
        run_client()
    else:
        run_server()
