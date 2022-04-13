import socket
from threading import Thread
from queue import Queue


def startup():
    s = socket.socket()

    ip = "127.0.0.1"
    port = 4445

    s.bind((ip, port))

    return s

def recvLoop(client, messageQueue: Queue, disconnectedClients: Queue):
    
    # Initial connection + username
    data = client.recv(1024)
    print("got connection")
    print(data)
    if(data.decode()[0:4]=='OPEN'):
            print("found open")        
            username = data.decode()[5:]
            print("gout username")
            client.send(b'HELLO')
            message = f"{username} has joined"
            messageQueue.put(message.encode())
    else:
        return

    
    while(True):
        data = client.recv(1024)

        if(data==b'CLOSE'):
            client.send(b'CLOSE')
            message = f"{username} has left"
            messageQueue.put(message.encode())
            disconnectedClients.put(client)
            break
        else:
            message = username + ": " + data.decode()
            messageQueue.put(message.encode())

def sendLoop(newClients: Queue, messages: Queue, disconnectedClients: Queue):
    connectedClients = []
    while True:
        while not disconnectedClients.empty():
            oldClient = disconnectedClients.get()
            connectedClients.remove(oldClient)
            disconnectedClients.task_done()
        while not newClients.empty():
            newClient = newClients.get()
            connectedClients.append(newClient)
            newClients.task_done()
        while not messages.empty():
            message = messages.get()
            print(message)
            for client in connectedClients:
                client.send(message)
            messages.task_done()


def main():
    s = startup()
    s.listen()

    messages = Queue()
    newClients = Queue()
    disconnectedClients = Queue()
    
    Thread(target=sendLoop, args=(newClients, messages,disconnectedClients, )).start()
    while(True):
        (client, clientAddress) = s.accept()
        newClients.put(client)
        Thread(target=recvLoop, args=(client,messages, disconnectedClients)).start()
        

    

if __name__ == "__main__":
    main()