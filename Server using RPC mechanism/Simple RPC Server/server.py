from socket import *

from env import *

def add(a, b):
    c = None
    c = a+b
    return c

s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
conn, addr = s.accept()

data = conn.recv(1024)

# Unmarshaling
num1 = int.from_bytes(data[:8], ENDIAN)
num2 = int.from_bytes(data[8:16], ENDIAN)
operation = data[16:].decode(STR_FORMAT)
# Invocation
if(operation == "add"):
    # Execution
    answer = add(num1, num2)
    # Marshaling
    if(answer):
        result = int.to_bytes(0, 8, ENDIAN)
        result += answer.to_bytes(8, ENDIAN)
    else:
        result = int.to_bytes(1, 8, ENDIAN)
# Returning
conn.send(result)
conn.close()
s.close()
