import socket
from threading import Thread
from queue import Queue


def startup():
    s = socket.socket()

    ip = "127.0.0.1"
    port = 4444

    s.bind((ip, port))

    return s

def recvLoop(client, messageQueue):
    print("Accepted")
    while(True):
        data = client.recv(1024)


        if(data==b'OPEN'):        

            client.send(b'HELLO')
            print("New Connection")

        elif(data==b'CLOSE'):
            client.send(b'CLOSE')
            print("Connection Closed")
            break
        else:
            messageQueue.put(data)

def sendLoop(newClients: Queue, messages: Queue):
    connectedClients = []
    while True:
        while not newClients.empty():
            newClient = newClients.get()
            connectedClients.append(newClient)
            newClients.task_done()
        while not messages.empty():
            message = messages.get()
            for client in connectedClients:
                client.send(message)
            messages.task_done()


def main():
    s = startup()
    s.listen()
    messages = Queue()
    newClients = Queue()
    
    Thread(target=sendLoop, args=(newClients, messages,)).start()
    while(True):
        (client, clientAddress) = s.accept()
        newClients.put(client)
        Thread(target=recvLoop, args=(client,messages)).start()
        

    

if __name__ == "__main__":
    main()