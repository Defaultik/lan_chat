import asyncio
import logging
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

    
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M'
    )


# TODO: nicknames blacklist
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
    setup_logging()

    asyncio.run(main())


async def main():
    ip = parser.parse_args().ip
    port = parser.parse_args().port or 8383
    nickname = nickname_creation()

    await Client(ip, port, nickname).connect()


class Client:
    # defines our ip, port, socket to variables
    def __init__(self, host, port, nickname):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.nickname = nickname
        self.message_queue = asyncio.Queue()


    async def connect(self):
        logging.info("Trying to connect to the server...")

        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            logging.info("Connection with the server established!\n")

            await asyncio.gather(self.receive(), self.send(), self.input_handler())
        except asyncio.CancelledError:
            logging.info("You disconnected from the server")
        except socket.error as e:
            logging.warning(f"Socket Error: {e}")

    
    async def input_handler(self):
        loop = asyncio.get_event_loop()
        
        while True:
            msg = await loop.run_in_executor(None, input)
            await self.message_queue.put(msg)

    
    async def send(self):
        while True:
            msg = await self.message_queue.get()
            msg = Message("msg", datetime.now().strftime("%H:%M"), self.nickname, msg)

            if self.writer:
                self.writer.write(pickle.dumps(msg))
                await self.writer.drain()


    async def receive(self):
        while True:
            try:
                data = await self.reader.read(1024) # gets data from the server in utf-8 format

                if data:
                    msg = pickle.loads(data)
                    logging.info(f"{msg.nickname}: {msg.content}")
                else:
                    break
            except (asyncio.IncompleteReadError, ConnectionResetError):
                break
        
        logging.info("Connection lost")

        self.writer.close()
        await self.writer.wait_closed()


class Message:
    def __init__(self, type, time, nickname, content):
        self.type = type
        self.time = time
        self.nickname = nickname
        self.content = content


if __name__ == "__main__":
    init()