import sys, time, threading

try:
    numOfThreads = int(sys.argv[1])
except IndexError:
    print("Specify number of threads")
    sys.exit(1)

num = int(input("Enter a Number: "))

answers = [None] * numOfThreads
threads = [None] * numOfThreads
timeDifference = [None] * numOfThreads
tids = [*range(numOfThreads)]
answerLock = threading.Lock()

def multiplyOverRange(id: int, start: int, end: int):
    global answer, answerLock
    s = time.time()
    if(start > end):
        return False
    p = 1
    for num in range(start, end+1):
        p *= num
    answers[id] = p
    e = time.time()
    timeDifference[id] = (e-s) * 10 ** 6
    return True

def factorial(num: int):
    global numOfThreads, threads, tids
    if(num < 0):
        return -1
    if(num == 0 or num == 1):
        return 1
    distribution = num // numOfThreads
    if(distribution < 2 or numOfThreads == 1):
        return multiplyOverRange(1, num)
    product = 1
    rangeStart = 1
    rangeEnd = rangeStart + distribution
    for tid in tids:
        thread = threading.Thread(target=multiplyOverRange, args=(tid, rangeStart, rangeEnd))
        thread.start()
        threads[tid] = thread
        rangeStart += distribution + 1
        rangeEnd = min(rangeStart + distribution, num)
    for thread in threads:
        thread.join()
    for answer in answers:
        product *= answer
    return product

print(f"{num}!={factorial(num)}")
print(f"Time taken: {sum(timeDifference)} microseconds")