import threading, sys, time, math

try:
    numOfThreads = int(sys.argv[1])
except:
    print("Missing Argument: Number of Threads")
    sys.exit(1)
threads = []

data = [100, 200, 300 ,100, 400 ,500,100, 200, 300 ,100, 400 ,500,100, 200, 300 ,100, 400 ,500,]
LEN = len(data)
results = [None] * LEN

rangeStart = 0
difference = int(math.ceil(LEN // numOfThreads))
rangeEnd = rangeStart + difference

timeDifference = []

def operationOverRange(data, operation, start, end):
    s = time.time()
    for i in range(start, end):
        results[i] = operation(data[i])
    e = time.time()
    timeDifference.append((e - s) * 10 ** 6)

def factorial(num: int):
    if(num < 0):
        return None
    if(num == 0 or num == 1):
        return 1
    product = 1
    for num in range(1, num+1):
        product *= num
    return product

if(numOfThreads == 1 or difference < 1):
    operationOverRange(data, factorial, rangeStart, LEN)
else:
    for i in range(numOfThreads):
        threads.append(threading.Thread(target=operationOverRange, args=(data.copy(), factorial, rangeStart, rangeEnd, )))
        threads[-1].start()
        rangeStart += difference
        rangeEnd = min([rangeStart+difference, LEN])

for thread in threads:
    thread.join()


print("I:", *data, sep="  ")
print("O:", *results, sep="  ")
print(f"Time taken: {sum(timeDifference)} microseconds")