import sys, datetime

num = int(input("Enter a Number: "))

def factorial(num: int):
    if(num < 0):
        return -1
    if(num == 0 or num == 1):
        return 1
    product = 1
    for num in range(1, num+1):
        product *= num
    return product

start = datetime.datetime.now()
print(f"{num}!={factorial(num)}")
end = datetime.datetime.now()
print(f"Time taken: {(end-start).total_seconds() * 10 ** 6} microseconds")