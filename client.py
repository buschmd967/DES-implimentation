from threading import Thread, Event
import socket
import sys


def connect(hostname, port):

    s = socket.socket()
    try:
        s.connect((hostname, port))
    except ConnectionRefusedError:
        print("Could not connect: Connection Refused")
        sys.exit()
    return s

def recvMessages(s):
    while True:
        data = s.recv(1024)
        print(data)

 
def main():
    s = connect("localhost", 4444)
    Thread(target=recvMessages, args=(s,)).start()


    message = "OPEN"
    bytes = str.encode(message)
    s.sendall(bytes)
    while(True):
        
        message = input("")

        s.sendall(message.encode())
        if(message == "CLOSE"):
            s.close()
            sys.exit()
 


    

if __name__ == "__main__":
    main()