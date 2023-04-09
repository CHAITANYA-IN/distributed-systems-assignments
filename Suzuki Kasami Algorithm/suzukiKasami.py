import random, sys, threading, time, datetime
from collections import deque
from mpi4py import MPI

now = datetime.datetime.now
comm = MPI.COMM_WORLD
tid = comm.Get_rank()
N = comm.Get_size()

criticalSectionLock = threading.Lock()
tokenLock = threading.Lock()
RNLock = threading.Lock()
releaseLock = threading.Lock()
requestLock = threading.Lock()
sendLock = threading.Lock()

Q = deque()
hasToken = 0
inCriticalSection = 0
waitingForToken = 0

RN = []
LN = []
for i in range(0, N):
    LN.append(0)
    RN.append(0)

# Process 0 gets the token initially
if(tid == 0):
    print(f"{now().strftime('%M:%S')}|[Process {tid}]: Startup Token")
    sys.stdout.flush()
    hasToken = 1
RN[0] = 1


def receiveRequest():
    global LN
    global RN
    global Q
    global inCriticalSection
    global waitingForToken
    global hasToken, tid
    while True:
        message = comm.recv(source=MPI.ANY_SOURCE)
        if message[0] == 'RN':
            with RNLock:
                requester_id = message[1]
                cs_value = message[2]
                RN[requester_id] = max([cs_value, RN[requester_id]])
                if cs_value < RN[requester_id]:
                    print(f"{now().strftime('%M:%S')}|[Process {tid}]: Request from Process {requester_id} expired")
                    sys.stdout.flush()

                if (hasToken == 1) and (inCriticalSection == 0) and (RN[requester_id] == (LN[requester_id] + 1)):
                    hasToken = 0
                    sendToken(requester_id)

        elif message[0] == 'token':
            with tokenLock:
                print(f"{now().strftime('%M:%S')}|[Process {tid}]: Got token")
                sys.stdout.flush()
                hasToken = 1
                waitingForToken = 0
                LN = message[1]
                Q = message[2]
                criticalSection()


def sendRequest(message):
    for i in range(N):
        if tid != i:
            to_send = ['RN', tid, message]
            comm.send(to_send, dest=i)


def sendToken(recipent):
    global Q
    with sendLock:
        print(f"{now().strftime('%M:%S')}|[Process {tid}]: Sending token to Process {recipent}")
        sys.stdout.flush()
        global inCriticalSection
        to_send = ['token', LN, Q]
        comm.send(to_send, dest=recipent)


def requestForCriticalSection():
    global RN
    global inCriticalSection
    global waitingForToken
    global hasToken
    with requestLock:
        if hasToken == 0:
            RN[tid] += 1
            print(f"{now().strftime('%M:%S')}|[Process {tid}]: Request for token ({RN[tid]})")
            sys.stdout.flush()
            waitingForToken = 1
            sendRequest(RN[tid])


def release_cs():
    global inCriticalSection
    global LN
    global RN
    global Q
    global hasToken
    with releaseLock:
        LN[tid] = max(LN) + 1
        for k in range(N):
            if k not in Q:
                if RN[k] == (LN[k] + 1):
                    Q.append(k)
                    print(f"{now().strftime('%M:%S')}|[Process {tid}]: Adding {k} to Queue\n\tQueue after adding: {Q}\n\tLN={LN}\n\tRN={RN}")
                    sys.stdout.flush()
        if len(Q) != 0:
            hasToken = 0
            sendToken(Q.popleft())


def criticalSection():
    global inCriticalSection
    global hasToken
    with criticalSectionLock:
        if hasToken == 1:
            inCriticalSection = 1
            print(f"{now().strftime('%M:%S')}|[Process {tid}]: Entering Critical Section ({RN[tid]})")
            sys.stdout.flush()
            time.sleep(random.uniform(2, 5))
            print(f"{now().strftime('%M:%S')}|[Process {tid}]: Exiting Critical Section ({RN[tid]})")
            sys.stdout.flush()
            inCriticalSection = 0
            release_cs()


try:
    listener = threading.Thread(target=receiveRequest)
    listener.start()
except:
    print("ERROR: Threads not spawning")
    sys.stdout.flush()

while True:
    if hasToken == 0:
        time.sleep(random.uniform(1, 3))
        requestForCriticalSection()
    elif inCriticalSection == 0:
        criticalSection()
    while waitingForToken:
        time.sleep(0.5)