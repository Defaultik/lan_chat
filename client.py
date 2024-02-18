import threading
import argparse
import pickle
import socket
import sys
import os
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
    parser.add_argument("-p", "--port", help="port of server socket (0-65535)")

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
        print("Socket error: %s" % e)


class Client:
    # defines our ip, port, socket to variables
    def __init__(client, host, port):
        client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.host = host
        client.port = port


    def connect(client):
        print("[%s] Trying to connect to the server..." % datetime.now().strftime("%H:%M"))

        try:
            client.socket.connect((client.host, client.port))
            print("[%s] Connection with the server establishment!\n" % datetime.now().strftime("%H:%M"))
            
            threading.Thread(target=client.receive).start() # starts a loop to receive messages in a new thread
            threading.Thread(target=client.send).start() # starts a loop to send messages in a new thread
        except socket.error as e:
            print("Connecting error: %s" % e)
        except KeyboardInterrupt:
            print("[%s] You disconnected from the server!" % datetime.now().strftime("%H:%M"))
            client.socket.close()

    
    def send(client):
        while True:
            msg = input()
            client.socket.send(msg.encode("utf-8")) # encodes our message to utf-8 format


    def receive(client):
        while True:
            try:
                data = client.socket.recv(1024) # gets data from the server in utf-8 format

                if data:
                    print(data.decode("utf-8")) # prints data in unicode format
            except:
                print("[%s] Connection lost" % datetime.now().strftime("%H:%M"))
                client.socket.close()


class Message:
    def __init__(self, type, length, msg):
        self.type = type
        self.length = length
        self.content = msg


if __name__ == "__main__":
    main()