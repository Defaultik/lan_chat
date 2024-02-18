import threading, argparse, pickle, socket, sys, os
from datetime import datetime


# terminal screen clearing function in both types of systems (unix-like & win)
def clear_screen():
    if (sys.platform == "win32"):
        os.system("cls")
    else:
        os.system("clear")


def main():
    # creates an argument parser to intercept the arguments that user enters when calling a file
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", help="ip of the server socket")
    parser.add_argument("-p", "--port", help="port of the server socket (0-65535)")

    clear_screen()

    # trying to start server
    try:
        if parser.parse_args().ip is None:
            print("IP of the socket (-i) wasn't given.")
            return False

        # if didn't find an argument then start the server with port 8383
        if parser.parse_args().port is None:
            print("Port (-p) wasn't given. Default port: 8383\n")
            Client(parser.parse_args().ip, 8383).connect()
        # if the argument is found then start the server with the user port
        else:
            Client(parser.parse_args().ip, int(parser.parse_args().port)).connect()
    except socket.error as e:
        print("Socket error\n%s" % e)


class Client:
    # defines our ip, port, socket to variables
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port


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
                msg = Message("msg", datetime.now().strftime("%H:%M"), msg, "")

                self.socket.send(pickle.dumps(msg))
        except (KeyboardInterrupt, SystemExit, EOFError):
            sys.exit()


    def receive(self):
        try:
            while True:
                data = self.socket.recv(1024) # gets data from the server in utf-8 format

                if data:
                    print(pickle.loads(data))
        except ConnectionResetError:
            print("[%s] Connection to the server lost" % datetime.now().strftime("%H:%M"))


class Message:
    def __init__(self, type, time, content, nickname):
        self.type = type
        self.time = time
        self.content = content
        self.nickname = nickname


if __name__ == "__main__":
    main()