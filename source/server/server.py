import asyncio
import socket
import logging
import pickle


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
        await User(ip, reader, writer).handling()

    
    async def get_users_count(self) -> int:
        return len(clients)


class User(Server):
    def __init__(self, ip_address, reader, writer):
        self.ip_address = ip_address
        self.reader = reader
        self.writer = writer
        self.public_rsa_key = ""


    async def handling(self):
        logging.info(f"Client ({self.ip_address}) connected")
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
            
            if (await self.get_users_count() == 1):
                msg = Message("CHAT", "SYSTEM", "You are the only client on the server, please wait until the other person connects...")
                if self.writer:
                    self.writer.write(pickle.dumps(msg))
                    await self.writer.drain()

            if isinstance(data, Message):
                async with clients_lock:
                    for client in clients:
                        if client != self:
                            client.writer.write(pickle.dumps(data))
                            await client.writer.drain()
                
                logging.info(f"{data.nickname}: {data.content}")


        self.writer.close()
        await self.writer.wait_closed()

        async with clients_lock:
            clients.remove(self)

        logging.info(f"[{self.ip_address}] Disconnected from the server")


class Message:
    def __init__(self, category, nickname, content):
        self.category = category
        self.nickname = nickname
        self.content = content


if __name__ == "__main__":
    asyncio.run(main())