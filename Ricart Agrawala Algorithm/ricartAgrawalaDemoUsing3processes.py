import multiprocessing
import socket
import threading
import time
import signal

PORT = 10000
NUM_OF_PROCESSES = 3
HOSTS = ['127.0.0.1', '127.0.0.1', '127.0.0.1', ]
PORTS = [(PORT + i) for i in range(NUM_OF_PROCESSES)]
ACQUIRE_MUTEX = ['A', None, 'A']
BUFFER_SIZE = 1024
RESOURCES = {
    'A': {
        'replies': 0,
    },
}
LOCK = threading.Lock()


def worker(
    pid: int,
    host: str,
    port: int,
    mutex: str,
):
    global HOSTS, PORTS, RESOURCES, LOCK
    resourcesLocal = RESOURCES.copy()

    TIMESTAMP = 0
    EVENTS = []
    QUEUE = []

    lock = threading.Lock()
    exitEvent = threading.Event()

    def printf(ts, s):
        nonlocal pid
        print(f"[Process {pid}] ", ts, s)

    def send(pid, addr, type, resource):
        nonlocal EVENTS, TIMESTAMP, lock
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        lock.acquire()
        TIMESTAMP += 1
        printf(f"TIMESTAMP={TIMESTAMP} ", f"Sending the {type} message to {addr[1]} for resource {resource}")
        msg = {
            'pid': pid,
            'type': type,
            'resource': resource,
            'timeStamp': TIMESTAMP,
        }
        EVENTS.append((msg, addr,))
        lock.release()
        s.send(str(msg).encode())
        s.close()

    def broadCast(pid, addr, type, resource, ts):
        nonlocal EVENTS, lock
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        printf(f"TIMESTAMP={ts} ", f"Sending the {type} message to {addr[1]} for resource {resource}")
        msg = {
            'pid': pid,
            'type': type,
            'resource': resource,
            'timeStamp': ts,
        }
        lock.acquire()
        EVENTS.append((msg, addr,))
        lock.release()
        s.send(str(msg).encode())
        s.close()

    def requestHandler(msg, mutex):
        nonlocal QUEUE, TIMESTAMP, pid
        externalPID = msg['pid']
        addr = (HOSTS[externalPID], PORTS[externalPID])
        printf(f"TIMESTAMP={TIMESTAMP} ", f"Received request from {addr[1]} for resource {msg['resource']} {mutex}")
        if(mutex and (mutex == msg['resource'])):
            # printf("", mutex)
            while(not(resourcesLocal[mutex].get('timeStamp'))):
                1
            # printf("Wait Over", mutex)
            if(msg['timeStamp'] < resourcesLocal[mutex]['timeStamp']):
                send(externalPID, addr, 'REPLY', msg['resource'])
            else:
                lock.acquire()
                QUEUE.append((msg, addr,))
                lock.release()
        else:
            send(pid, addr, 'REPLY', msg['resource'])
    
    def release(resource):
        nonlocal QUEUE, lock, pid, mutex
        printf(f"TIMESTAMP={TIMESTAMP} ", f"Releasing the resource {resource}")
        if(resource == mutex):
            lock.acquire()
            # printf("Queue: ", QUEUE)
            q = [i for i in QUEUE if (i[0]['resource'] == mutex)]
            QUEUE = [req for req in QUEUE if req not in q]
            mutex = None
            resourcesLocal[resource] = {
                'replies': 0,
            }
            lock.release()
            # printf(QUEUE, q)
            while(len(q)):
                msg, addr = q.pop(0)
                # printf(addr, msg)
                send(pid, addr, 'REPLY', msg['resource'])

    def replyHandler(msg, mutex):
        global LOCK
        nonlocal TIMESTAMP, resourcesLocal, lock
        externalPID = msg['pid']
        addr = (HOSTS[externalPID], PORTS[externalPID])
        printf(f"TIMESTAMP={TIMESTAMP} ", f"Received reply from {addr[1]} for resource {msg['resource']}")
        if(mutex):
            lock.acquire()
            resourcesLocal[msg['resource']]['replies'] += 1
            printf(f"TIMESTAMP={TIMESTAMP} ", f"Replies: {resourcesLocal[msg['resource']]['replies']}")
            lock.release()
            if(resourcesLocal[msg['resource']]['replies'] == NUM_OF_PROCESSES - 1):
                LOCK.acquire()
                printf(f"TIMESTAMP={TIMESTAMP} ", "Entering the Mutex")
                for i in range(1000):
                    i
                printf(f"TIMESTAMP={TIMESTAMP} ", "Exiting the Mutex")
                LOCK.release()
                release(msg['resource'])

    def listener(exitEvent:threading.Event, addr, mutex):
        nonlocal TIMESTAMP, EVENTS, QUEUE, lock
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(addr)
        s.listen(NUM_OF_PROCESSES)
        printf(f"TIMESTAMP={TIMESTAMP} ", f"Listening on port {addr[1]}")
        while not(exitEvent.isSet()):
            conn, addr = s.accept()
            raw_msg = conn.recv(BUFFER_SIZE).decode()
            # print(conn, addr, "Text:", raw_msg)
            msg = eval(raw_msg)
            lock.acquire()
            TIMESTAMP += 1
            lock.release()
            handlers[msg['type']](msg, mutex)
        else:
            conn.close()
        s.close()

    receiver = threading.Thread(target=listener, args=(exitEvent, (host, port,), mutex,))

    def exitter():
        nonlocal exitEvent, receiver
        exitEvent.set()
        receiver.join()

    handlers = {
        'REQUEST': requestHandler,
        'REPLY': replyHandler,
    }


    signal.signal(signal.SIGINT, exitter)


    receiver.start()
    time.sleep(2+pid)

    if(mutex):
        lock.acquire()
        TIMESTAMP += 1
        resourcesLocal[mutex]['timeStamp'] = TIMESTAMP
        lock.release()
        for i in range(NUM_OF_PROCESSES):
            if(i != pid):
                broadCast(
                    pid,
                    (
                        HOSTS[i],
                        PORTS[i],
                    ),
                    'REQUEST',
                    mutex,
                    resourcesLocal[mutex]['timeStamp']
                )


def createProcesses():
    processes=[]
    for i in range(NUM_OF_PROCESSES):
        processes.append(
            multiprocessing.Process(
                target=worker,
                args=(
                    i,
                    HOSTS[i],
                    PORTS[i],
                    ACQUIRE_MUTEX[i],
                ),
            )
        )

    for proc in processes:
        proc.start()

    for proc in processes:
        proc.join()


if __name__ == '__main__':
    createProcesses()