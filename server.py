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
    
    DEFINE['HOST'] = str(local_ip)
    log(f"HOST: {DEFINE['HOST']}")
    
    mainServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mainServer.settimeout(DEFINE['Timeout'])
    mainServer.bind((DEFINE['HOST'], 23456))
    mainServer.listen()
    log(">> Server lsitening ...")
    connect, addresss = mainServer.accept()
    log(f">> [ACCEPT]: {addresss}")
    connect.send(str("nice!").encode('utf-8'))
    mainServer.close()
    
