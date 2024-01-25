import socket

def Start():
    print(">> Start", flush=True)
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"IP: {str(local_ip)}", flush=True)
    
