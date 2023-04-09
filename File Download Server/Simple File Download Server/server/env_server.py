fileStatusCodes = {
    0: int(0).to_bytes(1, 'big'),  # Success
    1: int(1).to_bytes(1, 'big'),  # Error
    2: int(2).to_bytes(1, 'big'),  # Warning
}

FORMAT = 'utf-8'
URL = "localhost"
LOGS = './logs/server-logs.txt'
PORT = 9000
FILE_LENGTH_SIZE = 8