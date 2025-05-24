import asyncio
import threading
import time 
from websockets.asyncio.server import serve
from RTSP_Stream import RTSPStream
from Detector import Detector

stream_url = "rtsp://192.168.162.234:8554/cam1" 

def run_detector():
    rtmp_Stream = RTSPStream(stream_url)
    detector = Detector(rtmp_Stream)
    detector.run()

async def echo(websocket):
    async for message in websocket:
        print(f"Received message: {message}")
        if message == "start":
            print("Starting detection...")
            threading.Thread(target=run_detector).start()
            await websocket.send("Detection started.")
        elif message == "stop":
            print("Stopping detection...")
            # Add logic to stop the detector if needed
            await websocket.send("Detection stopped.")
        else:
            await websocket.send(f"Unknown command: {message}")

async def main():
    async with serve(echo, "localhost", 8765) as server:
        print("Starting detection...")
        thread = threading.Thread(target=run_detector, daemon=True)
        thread.start()
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())