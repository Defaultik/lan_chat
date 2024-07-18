import asyncio
import argparse
import pickle
import socket
import sys
import os
from datetime import datetime


clients = []
clients_lock = asyncio.Lock()


# terminal screen clearing function in both types of systems (unix-like & win)
def clear_screen():
    if (sys.platform == "win32"):
        os.system("cls")
    else:
        os.system("clear")


def init():
    global parser

    # creates an argument parser to intercept the arguments that user enters when calling a file
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, help="port of the server socket (0-65535)")

    clear_screen()
    asyncio.run(main())


async def main():
    ip = socket.gethostbyname(socket.gethostname())
    port = parser.parse_args().port or 8383

    try:
        await Server(ip, port).start()
    except socket.error as e:
        print(f"\n[Socket Error]\n{e}")


class Server:
    # defines our ip, port, socket to variables
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    
    async def start(self):        
        try:
            self.server = await asyncio.start_server(self.new_client, self.host, self.port)
            print("%s:%s" % (self.host, self.port))
            print("[%s] Waiting for new connections\n" % datetime.now().strftime("%H:%M"))

            async with self.server:
                await self.server.serve_forever()
        except (asyncio.CancelledError, KeyboardInterrupt):
            print("Server is closing...")
        except socket.error as e:
            print(f"\nSocket Error\n{e}")
        finally:
            self.server.close()
            await self.server.wait_closed()
            print("Server closed")


    async def new_client(self, reader, writer):
        addr = writer.get_extra_info("peername")
        await Client(reader, writer, addr[0]).handling()


class Client:    
    def __init__(self, reader, writer, address):
        self.reader = reader
        self.writer = writer
        self.address = address


    async def handling(self):
        print("[%s] (%s) Client connected" % (datetime.now().strftime("%H:%M"), self.address))
        async with clients_lock:
            clients.append(self)

        while True:
            data = await self.reader.read(1024) # getting user data

            if data: # checks if data is not nothing
                msg = pickle.loads(data)

                async with clients_lock:
                    for client in clients:
                        if client != self:
                            client.writer.write(pickle.dumps(msg))
                            await client.writer.drain()

                print("[%s] %s: %s" % (datetime.now().strftime("%H:%M"), msg.nickname, msg.content))
            else:
                break

        async with clients_lock:
            clients.remove(self)

        self.writer.close()
        await self.writer.wait_closed()

        print("[%s] (%s) Client disconnected" % (datetime.now().strftime("%H:%M"), self.address))


class Message:
    pass


if __name__ == "__main__":
    init()