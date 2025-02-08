import asyncio
import logging
import pickle


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

            await asyncio.gather(self.receive(), self.send(), self.input_handler())
        except (asyncio.CancelledError, KeyboardInterrupt):
            self.writer.close()
            await self.writer.wait_closed()

            logging.info("You disconnected from the server")

        
    async def input_handler(self):
        loop = asyncio.get_event_loop()
        
        while True:
            msg = await loop.run_in_executor(None, input)
            await self.message_queue.put(msg)

    
    async def send(self):
        while True:
            msg = await self.message_queue.get()
            msg = Message("CHAT", self.nickname, msg)

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
                    if data.category == "CHAT":
                        logging.info(f"{data.nickname}: {data.content}")
            except (asyncio.IncompleteReadError, ConnectionResetError):
                break

        self.writer.close()
        await self.writer.wait_closed()

        logging.warning("Connection lost")


class Message:
    def __init__(self, category, nickname, content):
        self.category = category
        self.nickname = nickname
        self.content = content
        

if __name__ == "__main__":
    asyncio.run(main())