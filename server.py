import socket

DEFINE = {
    'HOST': '0.0.0.0',
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
    log(f"HOSTNAME: {hostname}")
    local_ip = socket.gethostbyname(hostname)
    
    log(f"HOST: {local_ip}")
    
    mainServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mainServer.settimeout(DEFINE['Timeout'])
    mainServer.bind((DEFINE['HOST'], 23456))
    mainServer.listen()
    log(">> Server lsitening ...")
    try:
        connect, addresss = mainServer.accept()
        log(f">> [ACCEPT]: {addresss}")
        connect.send(str("nice!").encode('utf-8'))
    except:
        print('>> Server is closing ...')
    mainServer.close()
    
