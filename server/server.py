import asyncio
import threading
import subprocess
from websockets.asyncio.server import serve
from websockets import WebSocketServerProtocol

from shared import proximity_event
from shared import proximity_data
from Detector import Detector
from typing import Set
import json
from comparing_image import ImageComparer
from RTSP_Stream import FrameStreamer

# địa chị private của máy hoặc localhost
stream_url = "rtsp://192.168.142.172:8554/cam1"
detector_started = threading.Event()
comparer = ImageComparer()
frame_streamer = None
main_loop = None
isCompare = False



detector = Detector()
connected_clients: Set[WebSocketServerProtocol] = set()

async def broadcast_alert(message: str):
    for ws in connected_clients.copy():
        try:
            await ws.send(message)  
        except Exception as e:
            print(f"[SYSTEM] Failed to send to a client: {e}")
            connected_clients.remove(ws)


async def monitor_proximity():
    while True:
        await asyncio.sleep(5)
        if proximity_event.is_set():
            print("[SYSTEM] Detected proximity alert, broadcasting...")
            try:
                if isCompare:
                    data = {
                        "type": "fall_confirmed",
                        "message": "Fall detected and confirmed by continuous image similarity"
                    }
                    await broadcast_alert(json.dumps(data))
                    
                else:
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

# # hàm đọc stream và chạy tracking
# def run_detector():
#     # sử dụng biến toàn cục detector để dùng cho việc capture khi nhận yêu cầu từ client
#     global detector
#     while True:
#             print(f"Trying to open stream {stream_url}...")
#             cap = cv2.VideoCapture(stream_url)
#             if cap.isOpened():
#                 cap.release()  # test OK rồi tắt liền
#                 print("Detector is running...")
#                 detector = Detector(stream_url)
#                 detector.run()
#                 break
#             else:
#                 print("Waiting for RTSP stream...")
#                 time.sleep(5)
def run_detector():
    print("[SYSTEM] Detector is running...")
    global frame_streamer
    frame_streamer = FrameStreamer(stream_url)
    frame_streamer.start()
    detector.run(frame_streamer)

# hàm xử lý kết nối từ client - nhận dữ liệu từ client và kiểm tra khoảng cách
async def echo(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if detector:
                print(f"[SYSTEM] Received message: {message}")
                if message == "start":
                    if not detector_started.is_set():
                        print("[SYSTEM] Starting detection...")
                        threading.Thread(target=run_detector, daemon=True).start()
                        detector_started.set()
                        await websocket.send("Detection started.")
                elif data.get("isFall") == True:

                    print("[FALL] fall signal from client, monitoring in 30s")
                    isCompare = True
                    detector.pause()
                    def on_fall_confirmed():
                        asyncio.run_coroutine_threadsafe(
                        )
                    def run_monitor():
                        comparer.monitor_for_fall(frame_streamer, on_fall_confirmed)
                        print("[SYSTEM] resume detector")
                        detector.resume()
                        isCompare = False
                    threading.Thread(
                        target=run_monitor,
                        daemon=True
                    ).start()


    finally:
        connected_clients.remove(websocket)

# Hàm chính để khởi động server và kiểm tra trạng thái của mediatmx server
async def main():
    # khởi chạy luồng detector trên một thread riêng
    # subprocess.Popen(["mediamtx\mediamtx.exe"], shell=True)
    global frame_streamer, main_loop
    main_loop = asyncio.get_running_loop()
   
    # Kiểm tra xem mediatmx server đã chạy chưa
    result = subprocess.run('netstat -ano | findstr /i /c:8554 /c:8000 /c:8889', capture_output=True, text=True, shell=True)

    # Nếu không có kết quả, khởi động mediatmx server trong một của sổ CMD mới để theo dõi
    if not result.stdout:
        print("[SYSTEM] Starting mediatmx server...")
        # Chạy trên anaconda prompt nên cần đường dẫn tuyệt đốiđối
        completed = subprocess.run(
        'start cmd /k E:\\Nam3\\IoT_HD\\Project\\blind_sunglasses\\mediamtx\\mediamtx.exe E:\\Nam3\\IoT_HD\\Project\\blind_sunglasses\\mediamtx\\mediamtx.yml',
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE)
        # Nếu chạy trên CMD thì chạy đoạn code dưới
        # completed = subprocess.run(
        # 'start cmd /k mediamtx\mediamtx.exe mediamtx\mediamtx.yml',
        # shell=True,
        # creationflags=subprocess.CREATE_NEW_CONSOLE)
        
    else:
        print("[SYSTEM] Mediatmx server is already running.")

    # print("[SYSTEM] Starting detector thread...")
    # threading.Thread(target=run_detector, daemon=True).start()
    # Khởi động WebSocket server      
    async with serve(echo, "192.168.142.172", 8765) as server:
        print("[SYSTEM] WebSocket server started on ws://192.168.142.172:8765")
        await asyncio.gather(
                server.serve_forever(),
                monitor_proximity()
        )
if __name__ == "__main__":
    asyncio.run(main())