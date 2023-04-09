from env import *

# RPC
def add(num1, num2):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    # Marshaling
    data = num1.to_bytes(8, ENDIAN)
    data += num2.to_bytes(8, ENDIAN)
    data += "add".encode(STR_FORMAT)
    # Sending to OS
    s.send(data)
    # Receiving from OS
    result = s.recv(1024)
    # Unmarshaling
    status = int.from_bytes(result[:8], ENDIAN)
    answer = int.from_bytes(result[8:], ENDIAN)
    # Returning
    s.close()
    if(status != 0):
        raise Exception('RPC Call not successful')
    else:
        return answer

num1 = int(input("Enter a number:"))
num2 = int(input("Enter a number:"))

result = add(num1, num2)
print(result)