import sys
from socket import *
from datetime import datetime

from logs import *
from env_client import *
from utils import *

LOGS += str(datetime.now())

def writeLog(string: str) -> None:
    logs = open(LOGS, 'a')
    logs.write(string)
    logs.close()


def insertTimestamp(path):
    fileName = split(path, '/')[-1]
    fileName, fileExtension = split(fileName, '.')
    return f"{fileName}-{str(datetime.now())}.{fileExtension}"


def closeConnection():
    clientSocket.close()
    sys.exit(0)


def help():
    print("""Type,
> file <path to file> # To Download the file
> quit # To close the connection
""")


def extractStatusCode(data):
    return int.from_bytes(data[:1], byteorder='big')


def extractFileLength(data):
    size = FILE_LENGTH_SIZE
    return (
        int.from_bytes(data[:size], byteorder='big'),
        data[size:].decode()
    )


clientSocket = socket(AF_INET, SOCK_STREAM)
HOST = gethostbyname(URL)

try:
    port = int(sys.argv[1])
except(IndexError):
    port = PORT
clientSocket.connect((HOST, port))
LOGS += '-'+str(clientSocket.getsockname()[1]) + '.txt'
logs = open(LOGS, 'a')
logs.close()
help()
try:
    while True:
        # Take the action
        command = input('> ').strip()
        if(command[:4] == 'quit' or command[:4] == 'exit'):
            closeConnection()
        elif(command == ''):
            continue
        else:
            if(command[:5] != 'file '):
                help()
                continue
            path = command[5:].strip()

        if(path[:2] == '..' or path[:2] == './'):
            pass
        elif(path[:1] == '/'):
            path = '.'+path
        else:
            path = './'+path
        print(LOGS)
        previousAccessDetails = checkPreviousAccess(LOGS, path, 0)
        print('Here')
        if(previousAccessDetails):
            agoString, timestamp = timeAgo(previousAccessDetails)
            print(f"File Previously Accessed at {timestamp}, {agoString}")
            again = input('Do you want to access it again?(y/n):')
            if(again[0] == 'Y' or again[0] == 'y'):
                overwrite = input('Overwrite the file?(y/n):')
                if(overwrite[0] == 'Y' or overwrite[0] == 'y'):
                    fileName = path.split('/')[-1]
                else:
                    fileName = insertTimestamp(path)
            else:
                continue
        else:
            fileName = path.split('/')[-1]
        print(f'Downloading {fileName}')
        # Send the path
        clientSocket.send(path.encode())

        # Get file access status, file length and initial contents
        data = clientSocket.recv(1024)
        code = extractStatusCode(data)
        writeLog(
            f'{code}@{str(datetime.now())}#{fileName}|{path}\n')
        data = data[1:]
        if(code == 1):
            print(data.decode())
            continue
        if(code == 2):
            continue
        if(code != 0):
            continue
        fileLength, data = extractFileLength(data)
        # Open a file with same name
        f = open(DOWNLOADS+fileName, 'w')

        f.write(data)
        receivedLength = length(data)
        # Get all contents of the file
        print(f"Received {receivedLength}")
        while(receivedLength < fileLength):
            data = clientSocket.recv(1024).decode()
            f.write(data)
            receivedLength += length(data)
            print(f"Received {receivedLength}")
        f.close()

        # Send ACK
        clientSocket.send('Received Successfully'.encode())
except:
    closeConnection()
