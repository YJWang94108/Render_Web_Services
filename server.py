import socket
import threading
import random
import time
print(">> Set DEFINE")
DEFINE = {
    'HOST': '127.0.0.1',
    'PORT': None,
    'Connection': None,
    'Timeout': 60*5,
    'LaunchState': 0,
    'TextLength': 1024*4
}
clients = []
ChatRoom = []
mutex = threading.Lock()

def GeneratePortNumber():
    random.seed(time.time())
    return random.randint(30000, 65536)

def ShowInfo():
    global DEFINE
    print('==== [ INFO ] ====')
    print('HOST: ', DEFINE['HOST'])
    print('PORT: ', DEFINE['PORT'])
    print('==================')

def launch(server):
    global DEFINE
    server.bind((DEFINE['HOST'], DEFINE['PORT']))
    ShowInfo()
    server.listen()
    print('>> Server is listening ...')
    DEFINE['LaunchState'] = 1
    return server

def GetClientIndex(conn):
    global clients
    for i, c in enumerate(clients):
        if c[1]==conn:
            return i
    return -1

def Broadcast(msg):
    global clients
    print('[send] => '+str(msg))
    for _, client in clients:
        client.send(str(msg).encode('utf-8'))

def DisconnectAll():
    global clients
    for _, client in clients:
        client.close()
    clients = []

def handle(conn):
    global DEFINE, clients
    counter = 0
    while True:
        try:
            msg = conn.recv(DEFINE['TextLength']).decode('utf-8')
            if msg=='EXIT':
                break
            if msg=='':
                counter += 1
                break
            Broadcast(msg)
        except:
            return
    getIndex = GetClientIndex(conn)
    if getIndex!=-1:
        nickname = clients[getIndex][0]
        Broadcast(f'[SYSTEM]{nickname} left the chat!')
        clients[getIndex][1].close()
        del clients[getIndex]       

def inputFromKeyboard(server):
    global DEFINE
    while True:
        try:
            text = input("")
            if str(text)=='shutdown':
                DEFINE['LaunchState'] = 0
                break
            print('>> input: '+text)
        except KeyboardInterrupt:
            DEFINE['LaunchState'] = 0
            break
        except:
            DEFINE['LaunchState'] = 0
            break
    server.close()
    print('>> Keyboard closed')

def Room(server):
    cmd = threading.Thread(target=inputFromKeyboard, args=(server,))
    cmd.start()
    while True:
        if DEFINE['LaunchState']==0: break
        try:
            connect, addresss = server.accept()
            print(f'>> Connected by {str(addresss)}')
        except:
            Broadcast('>> Server is closing ...')
            print('>> Server is closing ...')
            DisconnectAll()
            break

        nickname = connect.recv(DEFINE['TextLength']).decode('utf-8')

        clients.append([nickname, connect])
        print(f'Nickname of the client name is {str(nickname)}')
        
        Broadcast(f'[SYSTEM]{nickname} joins the chat')
        
        openThread = threading.Thread(target=handle, args=(connect,))
        openThread.start()
    print('>> The server closed')

def MainServer(Server):
    global ChatRoom, mutex
    while True:
        try:
            connect, addresss = Server.accept()
            print('[ACCEPT]: ', addresss)
            mutex.acquire()
            if len(ChatRoom)==0:
                print('>> Launching the chat room ...')
                DEFINE['PORT'] = GeneratePortNumber()
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server = launch(server)
                ChatRoom.append({DEFINE['PORT']:[server, 0]})
                openRoom = threading.Thread(target=Room, args=(server,))
                openRoom.start()
        
            if len(ChatRoom)>0:
                connect.send(str(DEFINE['PORT']).encode('utf-8'))
                ChatRoom[0][DEFINE['PORT']][1] += 1
                connect.close()
                if ChatRoom[0][DEFINE['PORT']][1]>=2:
                    Server.close()
                    break
            mutex.release()
        except:
            print('>> Close server ...')
            break


def Start():
    print(">> Start")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    DEFINE['HOST'] = str(local_ip)
    print('HOST: ', DEFINE['HOST'])
    mainServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mainServer.settimeout(DEFINE['Timeout'])
    mainServer.bind((DEFINE['HOST'], 23456))
    mainServer.listen()
    openServer = threading.Thread(target=MainServer, args=(mainServer,))
    openServer.start()
    openServer.join()
    print('>> Get two users!')
