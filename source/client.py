import asyncio
import logging
import pickle
from encryption import RSA


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M'
    )


async def main():
    setup_logging()

    ip = input("Enter IP of the server: ")
    port = 8383

    nickname = input("Enter nickname: ")

    await Client(ip, port, nickname).connect()


class Client:
    def __init__(self, host, port, nickname):
        self.host = host
        self.port = port
        self.nickname = nickname
        self.message_queue = asyncio.Queue()


    async def connect(self):
        logging.info("Trying to connect to the server...")

        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            logging.info("Connection with the server established!\n")

            await self.handshake()
            # await asyncio.gather(self.receive(), self.send(), self.input_handler())
        except (asyncio.CancelledError, KeyboardInterrupt):
            self.writer.close()
            self.writer.wait_closed()

            logging.info("You disconnected from the server")


    async def handshake(self):
        logging.info("Trying to generate encryption keys...")

        try:
            self.private_key, self.public_key = RSA.generate_keys()
            logging.info("Encryption keys successfully generated")
        except:
            logging.error("Failed to generate encryption keys")

            self.writer.close()
            self.writer.wait_closed()

            logging.info("You disconnected from the server")
        
        if self.writer:
            self.writer.write(pickle.dumps(self.public_key))
            await self.writer.drain()

            logging.info("Encryption key sent successfully")
        
            for _ in range(3):
                logging.info("Waiting for server response...")

                data = await self.reader.read(1024)
                if data:
                    data = pickle.loads(data)

                    if data == "OK":
                        logging.info("Encryption successfuly established")
                        # TODO: Receive; Send functions to the server
                        break
                        
                    await asyncio.sleep(2)

        
    async def input_handler(self):
        loop = asyncio.get_event_loop()
        
        while True:
            msg = await loop.run_in_executor(None, input)
            await self.message_queue.put(msg)

    
    async def send(self):
        while True:
            msg = await self.message_queue.get()
            # msg = Message("msg", datetime.now().strftime("%H:%M"), self.nickname, encrypt(msg))

            if self.writer:
                self.writer.write(pickle.dumps(msg))
                await self.writer.drain()


    async def receive(self):
        while True:
            try:
                data = await self.reader.read(1024)

                if not data:
                    break
                
                try:
                    data = pickle.loads(data)
                except pickle.PickleError:
                    logging.error("Failed to deserialize message")
                    break

                if isinstance(data, Message):
                    logging.info(f"{data.nickname}: {data.content}")
            except (asyncio.IncompleteReadError, ConnectionResetError):
                break

        self.writer.close()
        await self.writer.wait_closed()

        logging.warning("Connection lost")


class Message:
    pass
        

if __name__ == "__main__":
    asyncio.run(main())