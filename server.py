import socket, threading, sys, os
from datetime import datetime

clients = []

current_time = datetime.now().strftime("%H:%M:%S")
banner = """
··············································
: ╔═╗┌─┐┬─┐┬  ┬┌─┐┬─┐  ┌─┐┌┬┐┌─┐┬─┐┌┬┐┌─┐┌┬┐ :
: ╚═╗├┤ ├┬┘└┐┌┘├┤ ├┬┘  └─┐ │ ├─┤├┬┘ │ ├┤  ││ :
: ╚═╝└─┘┴└─ └┘ └─┘┴└─  └─┘ ┴ ┴ ┴┴└─ ┴ └─┘─┴┘ :
··············································
"""


def run_server(host, port):
    try:
        # defines our socket for a variable and sets up ip and host of the server
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.bind((host, port))

        if (sys.platform == "win32"):
            os.system("cls")
        else:
            os.system("clear")
            
        print(banner)

        connection.listen() # waits for new clients
        print("Waiting for new connections...\n")

        # when we found new client --> start new thread specially for him
        threading.Thread(target=new_client, args=(connection, ), daemon=True).start()

        while input() != "exit()":
            pass
    except KeyboardInterrupt:
        connection.close()


def new_client(conn):
    while True:
        client_socket, address = conn.accept() # set up variables with user data
        clients.append(client_socket)

        print("[%s] New client connected! (%s)" % (current_time, address[0]))

        # starts server interaction with user in a new thread
        threading.Thread(target=server_processing, args=(client_socket, address), daemon=True).start()


def server_processing(client_socket, address):
    while True:
        try:
            data = client_socket.recv(1024) # accepts user data that he sent

            if data: # checks if data is not nothing
                message = data.decode("utf-8") # decodes our data from utf-8 code to unicode
                message = "%s: %s" % (address[0], message)

                for client in clients:
                    if client != client_socket: # if client is not sender
                        try:
                            client.send(message.encode("utf-8"))
                        except:
                            clients.remove[client]

                print("[%s] %s" % (current_time, message))
        except Exception:
                print("[%s] Client disconected! (%s)" % (current_time, address[0]))
                break


if __name__ == "__main__":
    try:
        run_server("0.0.0.0", int(sys.argv[1]))
    except:
        print("Invalid argument!\nExample: python %s <PORT>" % (sys.argv[0]))