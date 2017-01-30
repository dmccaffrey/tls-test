#!/usr/bin/python
import socket
import ssl
import time
import sys
import fcntl
import os
import struct
import subprocess
from pprint import pprint

PATH="/home/redx/tls-test/"
CA_CERTS_FILE = PATH + "ca/intermediate/certs/ca-chain.cert.pem"
SERVER_CERT = PATH + "ca/intermediate/certs/alpha.vmware.local.server.cert.pem"
SERVER_KEY = PATH + "ca/intermediate/private/alpha.vmware.local.key.pem"
CLIENT_CERT = PATH + "ca/intermediate/certs/bravo.vmware.local.usr.cert.pem"
CLIENT_KEY = PATH + "ca/intermediate/private/bravo.vmware.local.key.pem"

def create_tun(name, ip):
    TUNSETIFF = 0x400454ca
    TUNSETOWNER = TUNSETIFF + 2
    IFF_TUN = 0x0001
    IFF_TAP = 0x0002
    IFF_NO_PI = 0x1000
    tun = open('/dev/net/tun', 'r+b')
    ifr = struct.pack('16sH', name, IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    fcntl.ioctl(tun, TUNSETOWNER, 1000)
    subprocess.check_call('ip addr change dev {} {}'.format(name, ip),
                          shell=True)
    subprocess.check_call('ip link set dev {} up'.format(name),
                          shell=True)
    return tun


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
    tun = create_tun("client0", "10.0.0.1/24")
    s_sock = connect('localhost', 2243)
    dump_info(s_sock)
    while True:
        packet = os.read(tun.fileno(), 4096)
        print("got paket")
        s_sock.write(packet)

def run_server():
    tun = create_tun("server0", "10.0.0.2/24")
    sock = listen(2243)
    while True:
        n_sock, addr = sock.accept()
        stream = ssl.wrap_socket(n_sock, server_side=True, ca_certs=CA_CERTS_FILE, certfile=SERVER_CERT, keyfile=SERVER_KEY, cert_reqs=ssl.CERT_REQUIRED)
        dump_info(stream)
        try:
            while True:
                packet = stream.read()
                print("got paket")
                os.write(tun.fileno(), packet)
        finally:
            stream.shutdown(socket.SHUT_RDWR)
            stream.close()

if __name__ == "__main__":
    type = sys.argv[1]
    if type == "client":
        run_client()
    elif type == "server":
        run_server()
