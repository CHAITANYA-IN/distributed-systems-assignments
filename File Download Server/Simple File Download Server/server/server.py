from datetime import datetime
import sys, os
import signal
from socket import *
from _thread import *

from env_server import *


def writeLog(string: str) -> None:
    logs = open(LOGS, 'a')
    logs.write(string)
    logs.close()


def closeConnections(sig, frame):
    listeningSocket.close()
    i = 0
    while(i < len(connections)):
        conn, addr = connections.pop(i)
        conn.close()
        writeLog(f'{addr}>disconnect@{str(datetime.now())}\n')
    i += 1
    sys.exit(0)


def closeConnection(addr):
    i = 0
    while(i < len(connections)):
        if(connections[i][1] == addr):
            connections[i][0].close()
            connections.pop(i)
            print(addr, "disconnected")
            writeLog(f'{addr}>disconnect@{str(datetime.now())}\n')
        i += 1


signal.signal(signal.SIGINT, closeConnections)


def clientHandler(conn: socket, addr: tuple):
    while True:
        # Get file path
        path = conn.recv(1024)
        # Check path
        if(path == b''):
            closeConnection(addr)
            return addr
        # Adjust path
        path = path.decode()
        if(path[0] == '/'):
            path = f'.{path}'
        elif(path[0] != '.'):
            path = f'./{path}'
        print(addr, "Request for", path)
        fileName = os.path.basename(path)
        # Check file existence
        if(not(os.path.exists(path))):
            conn.send(fileStatusCodes[1] +
                      'ERROR: File not found'.encode())
            print(addr, 'ERROR: File not found')
            writeLog(
                f'{addr}>enotfound@{str(datetime.now())}#{fileName}|{path}\n')
        elif(not(os.access(path, os.F_OK))):
            conn.send(fileStatusCodes[1] + str("Is not a file").encode())
        elif(not(os.access(path, os.R_OK))):
            conn.send(fileStatusCodes[1] +
                      'Insufficient Permissions'.encode())
            writeLog(
                f'{addr}>eacces@{str(datetime.now())}#{fileName}|{path}\n')
            print(addr, 'Insufficient Permissions')
        else:
            try:
                f = open(path, 'r')
            except Exception as err:
                conn.send(fileStatusCodes[1] + str(err).encode())
            else:
                # Get file length
                fileLength = os.path.getsize(path).to_bytes(FILE_LENGTH_SIZE, 'big')
                # Read and send file
                conn.sendall(fileStatusCodes[0]+fileLength + f.read().encode())
                writeLog(f'{addr}>success@{str(datetime.now())}#{fileName}|{path}\n')
                f.close()
                # Acknowledge
                print(addr, conn.recv(1024).decode())


listeningSocket = socket(AF_INET, SOCK_STREAM)  # Socket creation - IPv4, TCP


HOST = gethostbyname(URL) # URL resolve -> IP

try:
    port = int(sys.argv[1])
except(IndexError):
    port = PORT
connections = []

listeningSocket.bind((HOST, port))
listeningSocket.listen()
print((HOST, port), "is Listening")

while True:
    conn, addr = listeningSocket.accept()
    connections.append((conn, addr))

    print(addr, "Connected")
    writeLog(f'{addr}>connect@{str(datetime.now())}\n')

    start_new_thread(clientHandler, (conn, addr, ))

closeConnections(signal.SIGINT, '')
