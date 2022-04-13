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
        try:
            data = s.recv(1024)
            print(data.decode())
        except Exception as e:
            print("Socket closed. Goodbye")
            return

 
def main(username="guest"):
    s = connect("localhost", 4445)
    

    message = "OPEN:" + username
    bytes = str.encode(message)
    s.sendall(bytes)
    print("Sent open")


    Thread(target=recvMessages, args=(s,)).start()

    while(True):
        
        message = input("")

        s.sendall(message.encode())
        if(message == "CLOSE"):
            s.close()
            sys.exit()
 


    

if __name__ == "__main__":
    main()