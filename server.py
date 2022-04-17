from multiprocessing import Event
import socket
from threading import Thread
from queue import Queue
from typing import Tuple
import sys
from time import sleep

import des
import elgamal as elg


def startup(port=1234):
    s = socket.socket()

    ip = "127.0.0.1"

    s.bind((ip, port))

    return s

def recvLoop(client, messageQueue: Queue, newClients: Queue, disconnectedClients: Queue, keys: Tuple[int, int, int, int]):
    
    # Initial connection
    g, a, p, b = keys
    publicKeys = f"{g} {a} {p}"
    key = ""
    data = client.recv(64)
    if(data.decode()=='OPEN'): 
            # Send public elgamal keys
            client.send(publicKeys.encode())

            # Recieve DES key
            data = client.recv(1024)
            message = data.decode()
            values = message.split(" ")
            c = (int(values[0]), int(values[1]))
            key = elg.decryptMessage(c, p, b)
            client.send(b'OK')
            # Get username
            username = des.getDesMessage(client, key)
            username = username.replace("\x00", "").replace("\n", "")
            # username = username

            newClients.put((client, key))

            message = f"{username} has joined"
            messageQueue.put(message)
    else:
        return

    closed = False
    while(not closed):
        message = des.getDesMessage(client, key).replace("\n", "")
        if message == "":
            pass
        elif(message=="CLOSE"):

            message = f"{username} has left"
            messageQueue.put(message)
            disconnectedClients.put((client, key))
            closed = True
            return
        else:

            message = username + ": " + message
            messageQueue.put(message)

def sendLoop(newClients: Queue, messages: Queue, disconnectedClients: Queue, quit: Event):
    connectedClients = []
    while True:
        if(quit.is_set()):
            for client, key in connectedClients:
                des.sendDESMessage(client, "CLOSE", key)
                client.close()
            return
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
            for client, key in connectedClients:
                des.sendDESMessage(client, message, key)
            messages.task_done()

def consoleControl(quit: Event):
    x = input("")
    if(x == "CLOSE"):
        print("QUITTING")
        quit.set()
        sleep(.5)
        sys.exit()

def newConnectionLoop(s: socket, messages: Queue, newClients: Queue, disconnectedClients: Queue, publicKeys, quitEvent: Event):
    while(True):
        (client, clientAddress) = s.accept()
        # newClients.put(client)
        Thread(target=recvLoop, args=(client,messages, newClients, disconnectedClients, publicKeys)).start()
        if(quitEvent.is_set()):
            break

def main():
    port = 1234
    if(len(sys.argv) > 1):
        port = sys.argv[1]
        if(not port.isnumeric):
            print("invaid port specified")
            return
        else:
            port = int(port)
    s = startup(port)
    s.listen()
    k = input("Enter k-bit elgamal key length (at least 32): ")
    k = int(k)

    p, g, b, a = elg.getKeys(k)
    print("Done. Listening for clients")
    publicKeys = (g, a, p, b)

    messages = Queue()
    newClients = Queue()
    disconnectedClients = Queue()
    quitEvent = Event()

    t1 = Thread(target=consoleControl, args=(quitEvent,))
    t2 = Thread(target=sendLoop, args=(newClients, messages, disconnectedClients, quitEvent))
    t3 = Thread(target=newConnectionLoop, args=(s, messages, newClients, disconnectedClients, publicKeys, quitEvent))

    t3.daemon = True

    t1.start()
    t2.start()
    t3.start()


    while True:
        if(quitEvent.is_set()):
            t1.join()
            t2.join()
            break
        

    

if __name__ == "__main__":
    main()