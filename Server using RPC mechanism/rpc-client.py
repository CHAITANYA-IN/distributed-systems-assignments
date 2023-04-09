import xmlrpc.client

PROTOCOL = 'http'
HOST = 'localhost'
PORT = 5000

def commandParser(command: str) -> list:
    func, params = command.split('(', 1)
    params = params.split(',')
    params[-1] = params[-1].split(')')[0]
    return func, params

server = xmlrpc.client.ServerProxy(f'{PROTOCOL}://{HOST}:{PORT}/')
callHandler = {
    'isSubString': server.isSubString,
    'getSubString': server.getSubString,
}

try:
    while True:
        print('> ', end="")
        try:
            command = input()
            if(command[:4] == "exit" or command[:4] == 'quit'):
                exit(0)
            elif(command[:4] == "help"):
                print(*server.system.listMethods(), sep=", ")
                continue
            func, params = commandParser(command)
            print(callHandler[func](*[eval(i) for i in params]))
        except Exception as err:
            print('SyntaxError:', err)
            continue
except KeyboardInterrupt:
    exit(0)
