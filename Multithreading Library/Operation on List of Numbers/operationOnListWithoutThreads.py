import threading, sys, time

data = [123389115, 231846842842, 814985834538542, 8142345234852, 1131821345877, 257171235381723389115, 231846842842, 814985834538542, 8142345234852, 1131821345877, 2571712353817,]
LEN = len(data)
results = [None] * LEN

def operationOverRange(data, operation, start, end):
    for i in range(start, end):
        results[i] = operation(data[i])

def sumOfCubes(num):
    sum = 0
    num_str = str(num)
    for ch in num_str:
        sum += int(ch) ** 3
    return sum

start = time.time()
operationOverRange(data, sumOfCubes, 0, LEN)
end = time.time()


print("I:", *data, sep="  ")
print("O:", *results, sep="  ")
print(f"Time taken: {(end - start) * 10 ** 6} microseconds")
