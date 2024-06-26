import threading, argparse, pickle, socket, sys, os
from datetime import datetime


clients = []
clients_lock = threading.Lock()


# terminal screen clearing function in both types of systems (unix-like & win)
def clear_screen():
    if (sys.platform == "win32"):
        os.system("cls")
    else:
        os.system("clear")


def main():
    # creates an argument parser to intercept the arguments that user enters when calling a file
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--port", type=int, help="port of the server socket (0-65535)")

    clear_screen()

    try:
        if not parser.parse_args().port:
            print("Port (-p) of the socket wasn't given. Default port: 8383\n")
            Server(socket.gethostbyname(socket.gethostname()), 8383).start()
        else:
            Server(socket.gethostbyname(socket.gethostname()), parser.parse_args().port).start()
            
    except socket.error as e:
        print("Socket Error\n%s" % e)


class Server:
    # defines our ip, port, socket to variables
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    
    def start(self):        
        try:
            self.socket.bind((self.host, self.port))
            print("%s:%s" % (self.host, self.port))
            
            # waits for new connections
            self.socket.listen()
            print("[%s] Waiting for new connections\n" % datetime.now().strftime("%H:%M"))

            # when we found new client --> start new thread specially for him
            threading.Thread(target=self.new_client, daemon=True).start()

            while True:
                self.command = input()

                if self.command == "exit()":
                    break

        except (KeyboardInterrupt, SystemExit):
            print("\nServer connection closed")

        finally:
            self.socket.close()

    
    def new_client(self):
        while True:
            sock, addr = self.socket.accept()

            # starts server interaction with user in a new thread
            threading.Thread(target=Client(sock, addr).handling, daemon=True).start()


class Client:    
    def __init__(self, sock, addr):
        self.socket = sock
        self.address = addr[0]


    def handling(self):
        print("[%s] (%s) Client connected" % (datetime.now().strftime("%H:%M"), self.address))

        with clients_lock:
            clients.append(self.socket)

        try:
            while True:
                data = self.socket.recv(1024) # getting user data

                if data: # checks if data is not nothing
                    msg = pickle.loads(data)

                    with clients_lock:
                        for client in clients:
                            if client != self.socket:
                                client.send(pickle.dumps(msg))

                    print("[%s] %s: %s" % (datetime.now().strftime("%H:%M"), msg.nickname, msg.content))

        except ConnectionResetError:
            print("[%s] (%s) Client disconected" % (datetime.now().strftime("%H:%M"), self.address))

            with clients_lock:
                clients.remove(self.socket)

        finally:
            self.socket.close()


class Message:
    pass


if __name__ == "__main__":
    main()