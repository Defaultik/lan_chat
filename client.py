import asyncio
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


def nickname_creation():
    nickname = input("Enter your nickname: ")
    return nickname


def init():
    global parser
    
    # creates an argument parser to intercept the arguments that user enters when calling a file
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", required=True, help="ip of the server socket")
    parser.add_argument("-p", "--port", type=int, help="port of the server socket (0-65535)")

    clear_screen()
    asyncio.run(main())


async def main():
    ip = parser.parse_args().ip
    port = parser.parse_args().port or 8383

    nickname = nickname_creation()

    try:
        await Client(ip, port, nickname).connect()
    except socket.error as e:
        print(f"\n[Socket Error]\n{e}")


class Client:
    # defines our ip, port, socket to variables
    def __init__(self, host, port, nickname):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.nickname = nickname


    async def connect(self):
        print(f"[{datetime.now().strftime("%H:%M")}] Trying to connect to the server...")

        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            print(f"[{datetime.now().strftime("%H:%M")}] Connection with the server established!\n")

            await asyncio.gather(self.receive(), self.send())
        except ConnectionResetError:
            print("Server connection closed")
        except asyncio.CancelledError:
            print("You disconnected from the server")
        except socket.error as e:
            print(f"\nSocket Error\n{e}")

    
    async def send(self):
        loop = asyncio.get_event_loop()
            
        while True:
            msg = await loop.run_in_executor(None, input)
            msg = Message("msg", datetime.now().strftime("%H:%M"), self.nickname, msg)

            if self.writer:
                self.writer.write(pickle.dumps(msg))
                await self.writer.drain()


    async def receive(self):
        while True:
            if self.reader:
                data = await self.reader.read(1024) # gets data from the server in utf-8 format

                if data:
                    msg = pickle.loads(data)
                    print(f"[{datetime.now().strftime("%H:%M")}] {msg.nickname}: {msg.content}")


class Message:
    def __init__(self, type, time, nickname, content):
        self.type = type
        self.time = time
        self.nickname = nickname
        self.content = content


if __name__ == "__main__":
    init()