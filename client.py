from threading import Thread, Event
import socket
import sys

import elgamal as elg
import des

def connect(hostname, port):

    s = socket.socket()
    try:
        s.connect((hostname, port))
    except ConnectionRefusedError:
        print("Could not connect: Connection Refused")
        sys.exit()
    return s



def recvMessages(s, key):
    while True:
        try:
            message = des.getDesMessage(s, key)
            print(message.replace("\n", ""))
        except Exception as e:
            print("Socket closed. Goodbye")
            print(e)
            return


    

def initialConnection(s: socket, username: str):
    deskey = input("Specify DES key: ").replace("\n", "")[:4]

    message = "OPEN"
    bytes = str.encode(message)
    s.sendall(bytes)
    print("Sent open")

    # getting elgamal keys
    data = s.recv(1024).decode()
    keys = data.split(" ")
    keys = (int(keys[0]), int(keys[1]), int(keys[2]))
    g, a, p = keys
    c = elg.encryptMessage(deskey, a, g, p)
    message = f"{c[0]} {c[1]}".encode()

    s.sendall(message)
    print("sent key, awaiting ack")
    data = s.recv(1024)
    print("sending username")
    des.sendDESMessage(s, username, deskey)

    return deskey


def main():
    username = "guest"
    port = 2257
    print(sys.argv)
    if(len(sys.argv) < 2):
        print("Please specify hostname and port")
        sys.exit()
    elif(len(sys.argv) >= 2):
        hostname = sys.argv[1]
        if(len(hostname.split(":")) == 2):
            x = hostname.split(":")
            hostname = x[0]
            port = int(x[1])
        if(len(sys.argv) == 3):
            username = sys.argv[2]

    s = connect(hostname, port)
    key = initialConnection(s, username)
   


    Thread(target=recvMessages, args=(s,key)).start()

    while(True):
        
        message = input("")

        des.sendDESMessage(s, message, key)
        if(message == "CLOSE"):
            s.close()
            sys.exit()
 


    

if __name__ == "__main__":
    main()