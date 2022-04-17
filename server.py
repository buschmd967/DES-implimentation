import socket
from threading import Thread
from queue import Queue
from typing import Tuple

import des
import elgamal as elg


def startup():
    s = socket.socket()

    ip = "127.0.0.1"
    port = 2230

    s.bind((ip, port))

    return s

def getDesMessage(client, key):
    # print("getting message")
    try:
        data = int(client.recv(1024).decode())
        message = des.decrypt([data], key)
    except ValueError:
        return ""
    while(message[-1] != "\n"):
        try:
            data = int(client.recv(64).decode())
            message += des.decrypt([data], key)
        except ValueError:
            message += "\n"
    # print(message)
    message = message.replace("\x00", "")
    return message


def recvLoop(client, messageQueue: Queue, disconnectedClients: Queue, keys: Tuple[int, int, int, int]):
    
    # Initial connection
    g, a, p, b = keys
    publicKeys = f"{g} {a} {p}"
    key = ""
    data = client.recv(64)
    print("got connection")
    print(data)
    if(data.decode()=='OPEN'): 
            # Send public elgamal keys
            client.send(publicKeys.encode())

            # Recieve DES key
            data = client.recv(1024)
            message = data.decode()
            values = message.split(" ")
            c = (int(values[0]), int(values[1]))
            key = elg.decryptMessage(c, p, b)
            print("got key")
            client.send(b'OK')
            # Get username
            username = getDesMessage(client, key)
            username = username.replace("\x00", "").replace("\n", "")
            print(f"username type: {type(username)} and {username=}")
            # username = username
            message = f"{username} has joined"
            messageQueue.put(message.encode())
    else:
        return

    closed = False
    while(not closed):
        message = getDesMessage(client, key).replace("\n", "")
        if message == "":
            pass
        elif(message=="CLOSE"):
            print(f"Got message: '{message}'")

            print("Closing connection")
            message = f"{username} has left"
            messageQueue.put(message.encode())
            disconnectedClients.put(client)
            closed = True
            return
        else:
            print(f"'{message.encode()}' != 'CLOSE'")
            print(f"Got message: '{message}'")

            message = username + ": " + message
            print(message)
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
            # print(message)
            for client in connectedClients:
                client.send(message)
            messages.task_done()


def main():
    s = startup()
    s.listen()
    k = input("Enter k-bit elgamal key length (at least 32): ")
    k = int(k)

    p, g, b, a = elg.getKeys(k)
    print("Done. Listening for clients")
    publicKeys = (g, a, p, b)

    messages = Queue()
    newClients = Queue()
    disconnectedClients = Queue()
    
    Thread(target=sendLoop, args=(newClients, messages,disconnectedClients, )).start()
    while(True):
        (client, clientAddress) = s.accept()
        newClients.put(client)
        Thread(target=recvLoop, args=(client,messages, disconnectedClients, publicKeys)).start()
        

    

if __name__ == "__main__":
    main()