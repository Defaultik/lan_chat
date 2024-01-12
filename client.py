import socket, threading, sys, os
from datetime import datetime


def server_connect(host, port):
    if (sys.platform == "win32"):
        os.system("cls")
    else:
        os.system("clear")

    print("Trying to connect to the server...")

    try:
        # defines our socket as a variable and connects to the server
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((host, port))

        print("Connection with server establishment!\n")

        threading.Thread(target=send, args=(connection, )).start() # starts loop to send messages in a new thread
        threading.Thread(target=receive, args=(connection, )).start() # starts loop to receive messages in a new thread
    except socket.error as error:
        print("Connection failed: %s" % (error))
    except KeyboardInterrupt:
        connection.close()


# simple function to send messages to the server
def send(conn):
    while True:
        message = input()
        conn.send(message.encode("utf-8")) # encodes our message to utf-8 format


# simple function to receive data from the server
def receive(conn):
    while True:
        try:
            data = conn.recv(1024) # gets data from the server in utf-8 format

            if data: # checks if data is not nothing
                print("[%s] %s" % (datetime.now().strftime("%H:%M:%S"), data.decode("utf-8"))) # brings data to the user in unicode format
        except:
            conn.close()
            print("[!] Connection lost")
            break


if __name__ == "__main__":
    try:
        server_connect("0.0.0.0", int(sys.argv[1]))
    except:
        print("Invalid argument!\nExample: python %s <PORT>" % (sys.argv[0]))