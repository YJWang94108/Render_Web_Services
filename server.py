import socket

def Start():
    print(">> Start")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print("IP:" , local_ip)
    
