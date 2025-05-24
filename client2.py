import random
import time
from websockets.asyncio.client import connect


# Client để gửi dữ liệu khoảng cách đến server mô phỏng ultrasonic
async def hello():
    async with connect("ws://192.168.162.172:8765") as websocket:
        while True:
            distance = random.randint(40, 60)
            print(distance)
            await websocket.send(distance)
            print(f"Sent message: {distance}")
            # response = await websocket.recv()
            # print(f"Received response: {response}")
            time.sleep(2)


if __name__ == "__main__":
    asyncio.run(hello())