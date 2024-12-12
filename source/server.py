import asyncio
import socket
import logging
import pickle
from encryption import RSA


clients = []
clients_lock = asyncio.Lock()


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M'
    )


async def main():
    setup_logging()

    ip = socket.gethostbyname(socket.gethostname())
    port = 8383

    await Server(ip, port).start()


class Server:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port


    async def start(self):
        try:
            self.server = await asyncio.start_server(self.new_client, self.host, self.port)

            logging.info(f"{self.host}:{self.port}")
            logging.info("Waiting for new connections...\n")

            async with self.server:
                await self.server.serve_forever()
        except (asyncio.CancelledError, KeyboardInterrupt):
            logging.info("Server is closing...")
        finally:
            self.server.close()
            await self.server.wait_closed()
            
            logging.info("Server closed")


    async def new_client(self, reader, writer):
        ip = writer.get_extra_info("peername")[0]
        await User(ip, reader, writer).handshake()


class User:
    def __init__(self, ip_address, reader, writer):
        self.ip_address = ip_address
        self.reader = reader
        self.writer = writer
        self.public_key = ""


    async def handshake(self):
        logging.info(f"[{self.ip_address}] Connected to the server")
        logging.info(f"[{self.ip_address}] Waiting for encryption key...")

        for _ in range(3):
            logging.info(f"[{self.ip_address}] Trying to get encryption key...")

            data = await self.reader.read(1024)
            if data:
                data = pickle.loads(data)

                # checks if user's message is rsa key
                if RSA.key_validation(data):
                    logging.info(f"[{self.ip_address}] Client encryption key collected")

                    self.public_key = data

                    if self.writer:
                        self.writer.write(pickle.dumps("OK"))
                        await self.writer.drain()

                    break
                
                
                await asyncio.sleep(5)

        if self.public_key:
            await self.handling()
        else:
            logging.info(f"[{self.ip_address}] Failed to get an encryption key")

            self.writer.close()
            await self.writer.wait_closed()

            logging.info(f"[{self.ip_address}] Disconnected from the server")


    async def handling(self):
        async with clients_lock:
            clients.append(self)

        while True:
            data = await self.reader.read(1024)

            if not data:
                break

            try:
                data = pickle.loads(data)
            except pickle.PickleError:
                logging.error(f"[{self.ip_address}] Failed to deserialize message")
                break

            if isinstance(data, Message):
                # TODO: send to other clients this message
                ...


        self.writer.close()
        await self.writer.wait_closed()

        async with clients_lock:
            clients.remove(self)

        logging.info(f"[{self.ip_address}] Disconnected from the server")


class Message:
    ...


if __name__ == "__main__":
    asyncio.run(main())