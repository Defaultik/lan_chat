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
        self.public_rsa_key = ""


    async def handshake(self):
        logging.info(f"[{self.ip_address}] Connected to the server")

        for _ in range(3):
            logging.info(f"[{self.ip_address}] Trying to get encryption key...")

            try:
                data = await asyncio.wait_for(self.reader.read(1024), timeout=5)
            except asyncio.TimeoutError:
                continue

            if not data:
                break
            
            try:
                data = pickle.loads(data)
            except pickle.UnpicklingError:
                logging.error(f"[{self.ip_address}] Failed to deserialize message")
                continue

            # checks if user's message is rsa key
            if RSA.key_validation(data):
                logging.info(f"[{self.ip_address}] Encryption key collected")
                self.public_rsa_key = data

                if self.writer:
                    self.writer.write(pickle.dumps("OK"))
                    await self.writer.drain()

                break

        if self.public_rsa_key:
            await self.handling()
        else:
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
            except pickle.UnpicklingError:
                logging.error(f"[{self.ip_address}] Failed to deserialize message")
                break

            if (len(clients) == 1) and (data == "ALONE"):
                msg = "You are the only client on the server, please wait until the other person connects..."
                if self.writer:
                    self.writer.write(pickle.dumps(msg))
                    await self.writer.drain()

            if isinstance(data, Message):
                # TODO: send message to companion
                print(data.content)


        self.writer.close()
        await self.writer.wait_closed()

        async with clients_lock:
            clients.remove(self)

        logging.info(f"[{self.ip_address}] Disconnected from the server")


class Message:
    ...


if __name__ == "__main__":
    asyncio.run(main())