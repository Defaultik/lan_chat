import threading, argparse, pickle, socket, sys, os
from datetime import datetime


# terminal screen clearing function in both types of systems (unix-like & win)
def clear_screen():
    if (sys.platform == "win32"):
        os.system("cls")
    else:
        os.system("clear")


def nickname_creation():
    nickname = input("Enter your nickname: ")
    return nickname


def main():
    # creates an argument parser to intercept the arguments that user enters when calling a file
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--ip", required=True, help="ip of the server socket")
    parser.add_argument("-p", "--port", type=int, help="port of the server socket (0-65535)")

    if not parser.parse_args().ip:
        parser.error("IP (-i) of the socket wasn't given")

    nickname = nickname_creation()
    clear_screen()

    try:
        if not parser.parse_args().port:
            print("Port (-p) of the socket wasn't given. Default port: 8383\n")
            Client(parser.parse_args().ip, 8383, nickname).connect()
        else:
            Client(parser.parse_args().ip, parser.parse_args.port, nickname).connect()
    except socket.error as e:
        print("Socket Error\n%s" % e)


class Client:
    # defines our ip, port, socket to variables
    def __init__(self, host, port, nickname):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.nickname = nickname


    def connect(self):
        print("[%s] Trying to connect to the server..." % datetime.now().strftime("%H:%M"))

        try:
            self.socket.connect((self.host, self.port))
            print("[%s] Connection with the server establishment!\n" % datetime.now().strftime("%H:%M"))
            
            threading.Thread(target=self.receive).start() # starts a loop to receive messages in a new thread
            threading.Thread(target=self.send).start() # starts a loop to send messages in a new thread
        except socket.error as e:
            print("Connecting error: %s" % e)
        except (KeyboardInterrupt, SystemExit):
            print("[%s] You disconnected from the server!" % datetime.now().strftime("%H:%M"))
            self.socket.close()

    
    def send(self):
        try:
            while True:
                msg = input()
                msg = Message("msg", datetime.now().strftime("%H:%M"), msg, self.nickname)

                self.socket.send(pickle.dumps(msg))
        except (KeyboardInterrupt, SystemExit, EOFError):
            return


    def receive(self):
        try:
            while True:
                data = self.socket.recv(1024) # gets data from the server in utf-8 format

                if data:
                    print(pickle.loads(data))
        except (ConnectionResetError, ConnectionAbortedError):
            print("[%s] Connection to the server lost" % datetime.now().strftime("%H:%M"))


class Message:
    def __init__(self, type, time, content, nickname):
        self.type = type
        self.time = time
        self.content = content
        self.nickname = nickname


if __name__ == "__main__":
    main()