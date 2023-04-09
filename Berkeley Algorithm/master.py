import datetime, time
import threading, signal
import socket

from env import *

CLIENTS = {}
CORRECTION = 0

def acceptConnections():
    while True:
        conn, addr = master.accept()
        CLIENTS[addr] = {
            SOCKET: conn,
        }

def sendTime():
    global CORRECTION
    while True:
        for addr in CLIENTS:
            CLIENTS[addr][SOCKET].send(b'0'+str(datetime.datetime.now()+datetime.timedelta(seconds=CORRECTION)).encode(FORMAT))
        time.sleep(GAP)

def receiveTime():
    global CORRECTION
    while True:
        if(len(CLIENTS) > 0):
            currentClients = CLIENTS.copy()
            addresses = currentClients.keys()
            for addr in addresses:
                currentClients[addr][DIFFERENCE] = int(currentClients[addr][SOCKET].recv(BUFFERSIZE).decode(FORMAT))
            averageDifference = int(sum([currentClients[addr][DIFFERENCE] for addr in currentClients]) / len(currentClients))
            for addr in addresses:
                currentClients[addr][SOCKET].send(b'1'+str(averageDifference-currentClients[addr][DIFFERENCE]).encode(FORMAT))
                CORRECTION += averageDifference
            print(f"Server: Corrected Time - {datetime.datetime.now()+datetime.timedelta(seconds=CORRECTION)}")

def closeConnection(addr):
    CLIENTS[addr][SOCKET].close()

def closeConnections(sig, frame):
    for addr in CLIENTS:
        CLIENTS[addr][SOCKET].close()
    master.close()
    accept_connections.exit()
    send_time.exit()
    receive_time.exit()
    exit(0)

# threading.Thread(target=clockHandler)
master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

signal.signal(signal.SIGINT, closeConnections)

master.bind((HOST, PORT))

master.listen(5)
print(f"Server listening at {PORT}")

accept_connections = threading.Thread(target=acceptConnections)
send_time = threading.Thread(target=sendTime)
receive_time = threading.Thread(target=receiveTime)

accept_connections.start()
send_time.start()
receive_time.start()

# accept_connections.join()
# send_time.join()
# receive_time.join()

# closeConnections()