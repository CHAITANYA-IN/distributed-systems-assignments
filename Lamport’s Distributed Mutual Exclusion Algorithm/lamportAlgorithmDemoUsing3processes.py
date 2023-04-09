import multiprocessing, traceback

w1_messagesToSend = [
    (1023, 2, 1),
    (1023, 3, 1),
    (1234, 2, 1),
    (1456, 3, 1),
    (2367, 2, 1),
]
w2_messagesToSend = [
    (2231, 1, 2),
    (9237, 3, 2),
    (1231, 1, 2),
    (3490, 1, 2),
]
w3_messagesToSend = [
    (3489, 1, 3),
    (1934, 2, 3),
    (2567, 2, 3),
    (9823, 1, 3),
]

w1_messagesToReply = {
    1231:
        (9823, 3, 1),
}

w2_messagesToReply = {
    1023:
        (1212, 1, 2),
    1234:
        (1111, 1, 2),
    1934:
        (2233, 3, 2),
}

w3_messagesToReply = {
    1023:
        (1999, 1, 3),
    9237:
        (2341, 2, 3),
}

Q = multiprocessing.Queue()

def worker(Q: multiprocessing.Queue, PID: str, messages: list[tuple], replyTo: dict):
    import threading, time
    import random
    
    exitEvent = threading.Event()
    lock = threading.Lock()
    EVENTS = []
    currentTimeStamp = 0

    def peek(Q: multiprocessing.Queue, pos: int=0):
        pos = pos if pos < Q.qsize() else -1
        l = []
        while(Q.qsize()):
            l.append(Q.get())
        ele = l[pos] if len(l) else None
        try:
            while(True):
                Q.put(l.pop(0))
        except IndexError:
            pass
        return ele

    def sendMessage(Q: multiprocessing.Queue):
        nonlocal EVENTS, currentTimeStamp
        for i in messages:
            lock.acquire()
            currentTimeStamp += 1
            event = (i, currentTimeStamp)
            Q.put(event)
            EVENTS.append(event)
            print(f"[SENT] Process {PID}:", f"TimeStamp:{currentTimeStamp}", EVENTS[-1] if len(EVENTS) else None, sep="\t")
            lock.release()
            time.sleep(random.randint(1, 3))
        time.sleep(10)
        exitEvent.set()

    def receiveMessage(Q: multiprocessing.Queue, replyTo: dict):
        nonlocal EVENTS, currentTimeStamp
        while True:
            try:
                if(exitEvent.is_set()):
                    break
                if(Q.empty() is False):
                    msg = peek(Q)
                    if(msg and msg[0][1] == PID):
                        msg = Q.get()
                        lock.acquire()
                        if(currentTimeStamp < msg[1]):
                            currentTimeStamp = msg[1]
                        currentTimeStamp += 1
                        EVENTS.append((msg[0], currentTimeStamp))
                        print(f"[RECV] Process {PID}:", f"TimeStamp:{currentTimeStamp}", EVENTS[-1] if len(EVENTS) else None, sep="\t")
                        if(replyTo.get(msg[0][0])):
                            currentTimeStamp += 1
                            Q.put((replyTo[msg[0][0]], currentTimeStamp))
                            EVENTS.append((replyTo[msg[0][0]], currentTimeStamp))
                            print(f"[SENT] Process {PID}:", f"TimeStamp:{currentTimeStamp}", EVENTS[-1] if len(EVENTS) else None, sep="\t")
                        lock.release()
            except KeyboardInterrupt:
                print("Terminating")
                break
            except Exception as err:
                print(traceback.format_exc())
                print(PID, EVENTS, msg)
                print(err)

    sender = threading.Thread(target=sendMessage, args=(Q, ))
    receiver = threading.Thread(target=receiveMessage, args=(Q, replyTo))

    sender.start()
    receiver.start()

    sender.join()
    receiver.join()

def createProcesses():
    global Q
    p1 = multiprocessing.Process(target=worker, args=(Q, 1, w1_messagesToSend, w1_messagesToReply))
    p2 = multiprocessing.Process(target=worker, args=(Q, 2, w2_messagesToSend, w2_messagesToReply))
    p3 = multiprocessing.Process(target=worker, args=(Q, 3, w3_messagesToSend, w3_messagesToReply))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

if __name__ == '__main__':
    createProcesses()
