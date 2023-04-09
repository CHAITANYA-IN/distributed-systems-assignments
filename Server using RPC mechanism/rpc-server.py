from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

HOST = 'localhost'
PORT = 5000

# Handler functions
def checkSubString(main: str, sub: str):
    return (sub in main)

def getSubStringPosition(main: str, sub: str):
    if(checkSubString(main, sub)):
        return len(main.split(sub, 1)[0]) + 1
    return -1


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/',)

# Launch server
with SimpleXMLRPCServer((HOST, PORT), requestHandler=RequestHandler) as s:
    print(f'{HOST}: Listening at {PORT}')
    s.register_introspection_functions()
    s.register_function(checkSubString, 'isSubString')
    s.register_function(getSubStringPosition, 'getSubString')
    
    # Listening loop
    s.serve_forever()
