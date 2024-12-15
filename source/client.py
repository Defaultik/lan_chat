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
        except (asyncio.CancelledError, KeyboardInterrupt):
            self.writer.close()
            await self.writer.wait_closed()

            logging.info("You disconnected from the server")


    async def handshake(self):
        try:
            self.private_key, self.public_key = RSA.generate_keys()
            logging.info("Encryption keys successfully generated")
        except:
            logging.error("Failed to generate encryption keys\n")

            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()

            logging.info("You disconnected from the server")
            return
        
        try:
            self.writer.write(pickle.dumps(self.public_key))
            await self.writer.drain()
            logging.info("Encryption key sent successfully\n")
        except:
            logging.error("Failed to send encryption key")

            self.writer.close()
            await self.writer.wait_closed()

            return
        
        for _ in range(3):
            logging.info("Waiting for server response...")

            try:
                data = await asyncio.wait_for(self.reader.read(1024), timeout=5)
            except asyncio.TimeoutError:
                continue

            if not data:
                break

            try:
                data = pickle.loads(data)
            except pickle.UnpicklingError:
                logging.error("Failed to deserialize server response")
                continue

            if data == "OK":
                logging.info("Encryption successfuly established")

                await self.lone_check()
                await asyncio.gather(self.receive(), self.send(), self.input_handler())

                break

        if not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()

            logging.info("You disconnected from the server")


    async def lone_check(self):
        if self.writer:
            self.writer.write(pickle.dumps("ALONE"))
            await self.writer.drain()

        
    async def input_handler(self):
        loop = asyncio.get_event_loop()
        
        while True:
            msg = await loop.run_in_executor(None, input)
            await self.message_queue.put(msg)

    
    async def send(self):
        while True:
            msg = await self.message_queue.get()
            msg = Message(msg)
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
                else:
                    logging.info(f"{data}")
            except (asyncio.IncompleteReadError, ConnectionResetError):
                break

        self.writer.close()
        await self.writer.wait_closed()

        logging.warning("Connection lost")


class Message:
    def __init__(self, content):
        self.content = content
        

if __name__ == "__main__":
    asyncio.run(main())