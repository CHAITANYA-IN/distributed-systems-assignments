import datetime
import signal
import socket

from env import *

CORRECTION = 0

def closeConnection(sig, frame):
    slave.send(b'-1')
    slave.close()

slave = socket.socket()

signal.signal(signal.SIGINT, closeConnection)

slave.connect((HOST, PORT))

while True:
    payload = slave.recv(BUFFERSIZE).decode(FORMAT)
    messageType = payload[0]
    message = payload[1:]
    if(messageType == '0'):
        serverTime = datetime.datetime.fromisoformat(message)
        difference = (datetime.datetime.now() + datetime.timedelta(seconds=CORRECTION) - serverTime).total_seconds()
        slave.send(str(int(difference)).encode(FORMAT))
    elif(messageType == '1'):
        CORRECTION += int(message)
        print(f"Client: Corrected Time {datetime.datetime.now() + datetime.timedelta(seconds=CORRECTION)}")

closeConnection(signal.SIGINT, '')