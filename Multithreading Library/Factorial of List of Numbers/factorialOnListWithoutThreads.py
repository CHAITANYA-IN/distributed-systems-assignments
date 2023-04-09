import threading, sys, time

data = [100, 200, 300, 400, 500]
LEN = len(data)
results = [None] * LEN

def operationOverRange(data, operation, start, end):
    for i in range(start, end):
        results[i] = operation(data[i])

def factorial(num: int):
    if(num == 0 or num == 1):
        return 1
    product = 1
    for num in range(1, num+1):
        product *= num
    return product

start = time.time()
operationOverRange(data, factorial, 0, LEN)
end = time.time()


print("I:", *data, sep="  ")
print("O:", *results, sep="  ")
print(f"Time taken: {(end - start)} seconds")
