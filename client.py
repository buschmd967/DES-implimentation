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

 
def main():
    username = "guest"
    port = 1234
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