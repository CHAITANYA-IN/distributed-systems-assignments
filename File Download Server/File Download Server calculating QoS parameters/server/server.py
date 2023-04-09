import sys
import threading
from _thread import *
from datetime import *
from socket import *

from env_server import *
from performance import *
from utils import *

CHUNK = 5

lock = threading.Lock()
now = datetime.now
LOGS += str(now()) + '.txt'
STATS += str(now()) + '.csv'

record = {
    'requests': 0,
    'clients': 0,
    'failed': 0,
    'served': 0,
    'serving': 0,
    "servingList": {},
    'bytesSent': 0,
    'bytesReceived': 0,
    'servingTimes': [],
}
records = []
statHeaders = [
    "Average Service Rate",
    "Average Throughput",
    "Utilization",
    "Fraction of time",
    "Average Number Of Requests",
    "Response Time",
]
stats = {
    "totalRequests": 0,
    'requestsServing': 0,
    'requestsServed': 0,
    'avgServiceRate': 0,
    'avgThroughput': 0,
}
durationCount = 0


def analysis():
    global record, durationCount, records, lock
    start = now()
    while True:
        if(now() > start + timedelta(seconds=CHUNK)):
            # print(record)
            records.append(record)
            lock.acquire()
            record = {
                'requests': 0,
                'clients': 0,
                'served': 0,
                'serving': 0,
                "servingList": {},
                'bytesSent': 0,
                'failed': 0,
                'bytesReceived': 0,
                'servingTimes': [],
            }
            lock.release()
            f = open('perf.log', 'a')
            prevRecord = records[-1] if length(records) > 0 else {}
            f.write(f'{start} to {start + timedelta(seconds=CHUNK)}')
            for i in prevRecord:
                # print(i, prevRecord[i])
                f.write(f'{i}: {prevRecord[i]}\n')
            if(prevRecord["served"] > 0):
                cumServiceRate = sum([1/(i.total_seconds())
                                     for i in prevRecord['servingTimes']])
                f.write(
                    f'Cummulative Service Rate: {cumServiceRate} requests/sec\n')
                avgServiceRate = (cumServiceRate / prevRecord["served"])
                f.write(
                    f'Average Service Rate: {avgServiceRate} requests/sec\n')
                throughput = (prevRecord['served'] +
                              prevRecord['serving']) / CHUNK
                f.write(f'Average Throughput {throughput} mbps\n')
                utilization = throughput/avgServiceRate
                f.write(f'Utilization {utilization}\n')
                # avgNumOfRequests = utilization / (1-utilization)
                # f.write(f'Average Number of Requests {avgNumOfRequests}\n')
                # responseTime = avgNumOfRequests / throughput
                # f.write(f'Response Time {responseTime}\n')
                # k = 2
                # kRequests = (1-utilization)*(utilization**k)
                # f.write(f'Fraction of time having {k} requests {kRequests}\n')
                # print('-'*70)
                f.write('-'*70+'\n')
            f.close()
            durationCount += 1
            start = now() + timedelta(seconds=CHUNK)
        else:
            l = length(connections)
            record['clients'] = l if l > record['clients'] else record['clients']
            pass


def computeStats(s):
    n = s['requestsServed'] + s['requestsServing']
    µ = s['avgServiceRate']
    print("Average Service Rate:", µ)
    λ = s['avgThroughput']
    print("Average Throughput:", λ)
    U = round(λ/µ)
    print("Utilization:", U)
    pk = round((1 - U) * (U ** n), 4)
    print("Fraction of time:", pk)
    N = round(U/(1-U), 4) if U != 1 else 0
    print("Average Number Of Requests:", N)
    R = round(1/((1-U)*µ), 4) if U != 1 else 0
    print("Response Time:", R)
    stats = {
        "Average Service Rate":µ,
        "Average Throughput":λ,
        "Utilization":U,
        "Fraction of time":pk,
        "Average Number Of Requests":N,
        "Response Time":R,
    }
    return stats

def addStatsHeaders():
    f = open(STATS, 'a+')
    stdout = sys.stdout
    sys.stdout = f
    print(*statHeaders, sep=",")
    sys.stdout = stdout
    f.close()

def saveStats(s):
    stats = computeStats(dict(s))
    f = open(STATS, 'a+')
    stdout = sys.stdout
    sys.stdout = f
    for i in statHeaders:
        print(stats[i], end=",")
    print('')
    sys.stdout = stdout
    f.close()


def writeLog(string: str) -> None:
    logs = open(LOGS, 'a')
    logs.write(string)
    logs.close()


def closeConnections():
    global connections
    listeningSocket.close()
    i = 0
    while(i < length(connections)):
        conn, addr = connections[i]
        conn.close()
        writeLog(f'{addr}>disconnect@{str(now())}\n')
    connections = []
    i += 1


def closeConnection(addr):
    i = 0
    while(i < length(connections)):
        if(connections[i][1] == addr):
            connections[i][0].close()
            connections.pop(i)
            print(addr, "disconnected")
            writeLog(f'{addr}>disconnect@{str(now())}\n')
        i += 1


def clientHandler(conn: socket, addr: tuple):
    while True:
        # Get file path
        path = conn.recv(1024)
        startServiceTime = now()
        lock.acquire()
        stats['requestsServing'] += 1
        record['requests'] += 1
        record['serving'] += 1
        record['servingList'][addr] = True
        record['bytesReceived'] += length(path)
        lock.release()
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
        # Check file existence
        try:
            fileName = split(path, '/')[-1]
            f = open(path, 'r')
        except(FileNotFoundError):
            data = conn.send(fileStatusCodes[1] +
                             'ERROR: File not found'.encode())
            lock.acquire()
            record['bytesSent'] += data
            record['failed'] += 1
            lock.release()
            print(addr, 'ERROR: File not found')
            writeLog(
                f'{addr}>enotfound@{str(now())}#{fileName}|{path}\n')
        except(PermissionError):
            data = conn.send(fileStatusCodes[1] +
                             'Insufficient Permissions'.encode())
            lock.acquire()
            record['bytesSent'] += data
            record['failed'] += 1
            lock.release()
            writeLog(
                f'{addr}>eacces@{str(now())}#{fileName}|{path}\n')
            print(addr, 'Insufficient Permissions')
        except Exception as err:
            data = conn.send(fileStatusCodes[1] + str(err).encode())
            lock.acquire()
            record['bytesSent'] += data
            record['failed'] += 1
            lock.release()
        else:
            # Get file length
            f.seek(0, 2)
            fileLength = f.tell().to_bytes(FILE_LENGTH_SIZE, 'big')
            # Read and send file
            f.seek(0, 0)
            data = fileStatusCodes[0]+fileLength + f.read().encode()
            conn.sendall(data)
            endServiceTime = now()
            lock.acquire()
            # Normal Averaging
            serviceTime = endServiceTime - startServiceTime
            servedSeconds = serviceTime.total_seconds()
            sRS = stats['requestsServed']
            stats['avgServiceRate'] = round((sRS * \
                stats['avgServiceRate'] + round(1 / servedSeconds)) / (sRS + 1), 4)
            stats['requestsServing'] -= 1
            stats['requestsServed'] += 1
            stats['totalRequests'] += 1
            stats['avgThroughput'] = round((sRS * stats['avgThroughput'] + \
                round(stats['requestsServed'] * stats['avgServiceRate'])) / stats['requestsServed'], 4)
            # Stats for CHUNK time
            record['bytesSent'] += length(data)
            record['served'] += 1
            if(record['servingList'][addr]):
                record['serving'] -= 1
                del record['servingList'][addr]
            record['servingTimes'].append(serviceTime)
            lock.release()
            saveStats(stats)
            writeLog(
                f'{addr}>success@{str(now())}#{fileName}|{path}\n')
            f.close()
            # Acknowledge
            print('All bytes sent complete')
            print(addr, conn.recv(1024).decode())


listeningSocket = socket(AF_INET, SOCK_STREAM)

HOST = gethostbyname(URL)

try:
    port = int(sys.argv[1])
except(IndexError):
    port = PORT
connections = []
numberOfClients = 0

listeningSocket.bind((HOST, port))
listeningSocket.listen()
serverStartTime = now()
print((HOST, port), "is Listening")

addStatsHeaders()
start_new_thread(analysis, ())

try:
    while True:
        conn, addr = listeningSocket.accept()
        numberOfClients += 1
        connections.append((conn, addr))

        print(addr, "Connected")
        writeLog(f'{addr}>connect@{str(now())}\n')

        threadIdentifier = start_new_thread(clientHandler, (conn, addr, ))

except:
    saveStats(stats)
    closeConnections()
    serverEndTime = now()
