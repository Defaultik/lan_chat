import threading
import argparse
import socket
import sys
import os
from datetime import datetime


current_time = datetime.now().strftime("%H:%M")


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
            Client("127.0.0.1", 8383).connect()
        # if the argument is found then start the server with the user port
        else:
            Client("127.0.0.1", int(parser.parse_args().port)).connect()
    except socket.error as e:
        print("Socket error: %s" % e)


class Client:
    # defines our ip, port, socket to variables
    def __init__(client, host, port):
        client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.host = host
        client.port = port


    def connect(client):
        print("[%s] Trying to connect to the server..." % current_time)

        try:
            client.socket.connect((client.host, client.port))
            print("[%s] Connection with the server establishment!\n" % current_time)
            
            threading.Thread(target=client.receive).start() # starts a loop to receive messages in a new thread
            threading.Thread(target=client.send).start() # starts a loop to send messages in a new thread
        except socket.error as e:
            print("Socket error: %s" % e)
        except KeyboardInterrupt:
            print("[%s] You disconnected from the server!" % current_time)
            client.socket.close()

    
    def send(client):
        while True:
            message = input()
            client.socket.send(message.encode("utf-8")) # encodes our message to utf-8 format


    def receive(client):
        while True:
            try:
                data = client.socket.recv(1024) # gets data from the server in utf-8 format

                if data:
                    print(data.decode("utf-8")) # prints data in unicode format
            except:
                print("[%s] Connection with server lost" % current_time)
                client.socket.close()
                break


if __name__ == "__main__":
    main()