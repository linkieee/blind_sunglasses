import asyncio
from websockets.asyncio.client import connect


async def hello():
    async with connect("ws://localhost:8765") as websocket:
        while True:
            message = input("Enter a message to send (or 'exit' to quit): ")
            if message.lower() == "exit":
                break
            await websocket.send(message)
            print(f"Sent message: {message}")
            response = await websocket.recv()
            print(f"Received response: {response}")


if __name__ == "__main__":
    asyncio.run(hello())