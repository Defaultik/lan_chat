import threading
import argparse
import socket
import sys
import os
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
    parser.add_argument("-p", "--port", help="port of server socket (0-65535)")

    clear_screen()

    # trying to start server
    try:
        # if didn't find an argument then start the server with port 8383
        if parser.parse_args().port is None:
            print("Port (-p) wasn't selected. Default port: 8383\n")
            Server(socket.gethostbyname(socket.gethostname()), 8383).start()
        # if the argument is found then start the server with the user port
        else:
            Server(socket.gethostbyname(socket.gethostname()), int(parser.parse_args().port)).start()
    except socket.error as e:
        print("Socket Error: %s" % e)


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
            print("[%s] Waiting for new connections!\n" % datetime.now().strftime("%H:%M"))

            # when we found new client --> start new thread specially for him
            threading.Thread(target=self.new_client, daemon=True).start()

            while True:
                self.command = input()

                if self.command == "exit()":
                    break
        except KeyboardInterrupt:
            pass
        finally:
            print("Server shut down")
            self.socket.close()

    
    def new_client(self):
        while True:
            sock, addr = self.socket.accept()

            # starts server interaction with user in a new thread
            threading.Thread(target=Client(sock, addr).handling, daemon=True).start()


class Client:    
    def __init__(self, sock, addr):
        self.socket = sock
        self.address = addr


    def handling(self):
        print("[%s] (%s) Client connected" % (datetime.now().strftime("%H:%M"), self.address[0]))

        with clients_lock:
                clients.append(self.socket)

        while True:
            try:
                data = self.socket.recv(1024) # getting user data

                if data: # checks if data is not nothing
                    msg = data.decode("utf-8") # decodes our data from utf-8 code to unicode
                    msg = "[%s] %s: %s" % (datetime.now().strftime("%H:%M"), self.address[0], msg)

                    with clients_lock:
                        for client in clients:
                            if client != self.socket: # if client is not sender
                                try:
                                    client.send(msg.encode("utf-8"))
                                except:
                                    clients.remove(client)
                                
                        print(msg)
            except:
                self.socket.close()
                print("[%s] (%s) Client disconected" % (datetime.now().strftime("%H:%M"), self.address[0]))
                break


if __name__ == "__main__":
    main()