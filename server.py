import asyncio
import threading
import subprocess
import time
from websockets.asyncio.server import serve
from websockets import WebSocketServerProtocol
from RTSP_Stream import RTSPStream
from shared import proximity_event
from shared import proximity_data
from Detector import Detector
from typing import Set
import json
import cv2



# địa chị private của máy hoặc localhost
stream_url = "rtsp://10.0.123.103:8554/cam1"
detector_started = threading.Event()

# tạo biến global 
detector = None
connected_clients: Set[WebSocketServerProtocol] = set()

async def broadcast_alert(message: str):
    for ws in connected_clients.copy():
        try:
            await ws.send(message)  
        except Exception as e:
            print(f" Failed to send to a client: {e}")
            connected_clients.remove(ws)


async def monitor_proximity():
    while True:
        await asyncio.sleep(0.1)
        if proximity_event.is_set():
            print(" Detected proximity alert, broadcasting...")
            try:
                data = {
                    "type": "proximity_alert",
                    "direction": proximity_data.get("direction", "UNKNOWN"),
                    "severity": proximity_data.get("severity", "LOW"),
                    "label": proximity_data.get("label", "unknown")
                }
                await broadcast_alert(json.dumps(data))
            except Exception as e:
                print("Error sending alert:", e)
            finally:
                
                proximity_event.clear()



# hàm đọc stream và chạy tracking
def run_detector():
    # sử dụng biến toàn cục detector để dùng cho việc capture khi nhận yêu cầu từ client
    global detector
    # while True:
    #     #tạo đối tượng RTSPStream với địa chỉ stream dành cho việc đọc luồng stream từ pi5 
    #     rtsp_Stream = RTSPStream(stream_url)
    #     print(rtsp_Stream.isOpened())
        
    #     #nếu luồng stream mở thành công thì mới chạy tracking
    #     if rtsp_Stream.isOpened():
    #         cap = rtsp_Stream.get_capture()

    #         print("Detector is running...")
    #         detector = Detector(cap)
    #         detector.run()
    #         break
    #     else:
    #         print("Try connect to RTSP...")
    #         time.sleep(5)
    
    while True:
            print(f"Trying to open stream {stream_url}...")
            cap = cv2.VideoCapture(stream_url)
            if cap.isOpened():
                cap.release()  # test OK rồi tắt liền
                print("Detector is running...")
                detector = Detector(stream_url)
                detector.run()
                break
            else:
                print("Waiting for RTSP stream...")
                time.sleep(5)

# hàm xử lý kết nối từ client - nhận dữ liệu từ client và kiểm tra khoảng cách
async def echo(websocket):
    connected_clients.add(websocket)
    global detector
    try:
        async for message in websocket:
            if detector:
                print(f"Received message: {message}")
                if message == "start":
                    if not detector_started.is_set():
                        print("Starting detection...")
                        threading.Thread(target=run_detector).start()
                        detector_started.set()
                        await websocket.send("Detection started.")
                elif (int(message) < 50):
                    print("Distance is less than 50 cm, starting notice and capture...")    
                    detector.isCapture = True
                
                else:
                    print("Distance is greater than 50 cm, stopping notice and capture...")

    finally:
        connected_clients.remove(websocket)

# Hàm chính để khởi động server và kiểm tra trạng thái của mediatmx server
async def main():
    # khởi chạy luồng detector trên một thread riêng
    # subprocess.Popen(["mediamtx\mediamtx.exe"], shell=True)
    
    print("Starting detection...")
    thread = threading.Thread(target=run_detector, daemon=True)
    thread.start()

    # Kiểm tra xem mediatmx server đã chạy chưa
    result = subprocess.run('netstat -ano | findstr /i /c:8554 /c:8000 /c:8889', capture_output=True, text=True, shell=True)

    # Nếu không có kết quả, khởi động mediatmx server trong một của sổ CMD mới để theo dõi
    if not result.stdout:
        print("Starting mediatmx server...")
        # Chạy trên anaconda prompt nên cần đường dẫn tuyệt đốiđối
        # completed = subprocess.run(
        # 'start cmd /k E:\\Nam 3\\IoTHD\\server2\\blind_sunglasses\\mediamtx\\mediamtx.exe E:\\Nam 3\\IoTHD\\server2\\blind_sunglasses\\mediamtx\\mediamtx.yml',
        # shell=True,
        # creationflags=subprocess.CREATE_NEW_CONSOLE)
        # Nếu chạy trên CMD thì chạy đoạn code dưới
        completed = subprocess.run(
        'start cmd /k mediamtx\mediamtx.exe mediamtx\mediamtx.yml',
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        print("Mediatmx server is already running.")

    # Khởi động WebSocket server      
    async with serve(echo, "10.0.123.103", 8765) as server:
        print("WebSocket server started on ws://10.0.123.103:8765")
        await asyncio.gather(
                server.serve_forever(),
                monitor_proximity()
        )
if __name__ == "__main__":
    asyncio.run(main())