import asyncio
import threading
import subprocess
import time
from websockets.asyncio.server import serve
from RTSP_Stream import RTSPStream
from Detector import Detector

stream_url = "rtsp://192.168.162.234:8554/cam1" 

def run_detector():
    while True:
        rtsp_Stream = RTSPStream(stream_url)
        print(rtsp_Stream.isOpened())
        
        if rtsp_Stream.isOpened():
            print("Detector is running...")
            detector = Detector(rtsp_Stream)
            detector.run()
            break
        else:
            print("Thử lại kết nối RTSP...")
            time.sleep(2)


async def echo(websocket):
    async for message in websocket:
        print(f"Received message: {message}")
        if message == "start":
            print("Starting detection...")
            threading.Thread(target=run_detector).start()
            await websocket.send("Detection started.")
        elif message == "stop":
            print("Stopping detection...")
            await websocket.send("Detection stopped.")
        else:
            await websocket.send(f"Unknown command: {message}")

async def main():
    print("Starting detection...")
    thread = threading.Thread(target=run_detector, daemon=True)
    thread.start()     
    async with serve(echo, "192.168.162.172", 8765) as server:
        print("WebSocket server started on ws://192.168.162.172:8765")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())