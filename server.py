import socket

DEFINE = {
    'HOST': '127.0.0.1',
    'PORT': None,
    'Connection': None,
    'Timeout': 30,
    'LaunchState': 0,
    'TextLength': 1024*4
}

def log(msg:str):
    print(f"[PYTHON]: {msg}", flush=True)

def Start():
    global DEFINE

    log(">> Start")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    log(f"IP: {str(local_ip)}")
    print('>>', DEFINE['Timeout'])
    
