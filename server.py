import asyncio
import threading
import subprocess
import time
from websockets.asyncio.server import serve
from RTSP_Stream import RTSPStream
from Detector import Detector

# địa chị private của máy hoặc localhost
stream_url = "rtsp://192.168.162.172:8554/cam1"
# tạo biến global 
detector = None

# hàm đọc stream và chạy tracking
def run_detector():
    # sử dụng biến toàn cục detector để dùng cho việc capture khi nhận yêu cầu từ client
    global detector
    while True:
        #tạo đối tượng RTSPStream với địa chỉ stream dành cho việc đọc luồng stream từ pi5 
        rtsp_Stream = RTSPStream(stream_url)
        print(rtsp_Stream.isOpened())
        
        # nếu luồng stream mở thành công thì mới chạy tracking
        if rtsp_Stream.isOpened():
            print("Detector is running...")
            detector = Detector(rtsp_Stream)
            detector.run()
            break
        else:
            print("Try connect to RTSP...")
            time.sleep(5)

# hàm xử lý kết nối từ client - nhận dữ liệu từ client và kiểm tra khoảng cách
async def echo(websocket):
    global detector
    async for message in websocket:
        # if detector:
            print(f"Received message: {message}")
            
            # if (int(message) < 50):
            #     print("Distance is less than 50 cm, starting notice and capture...")    
            #     detector.isCapture = True
            # else:
            #     print("Distance is greater than 50 cm, stopping notice and capture...")

# Hàm chính để khởi động server và kiểm tra trạng thái của mediatmx server
async def main():
    # khởi chạy luồng detector trên một thread riêng
    # print("Starting detection...")
    # thread = threading.Thread(target=run_detector, daemon=True)
    # thread.start()

    # # Kiểm tra xem mediatmx server đã chạy chưa
    # result = subprocess.run('netstat -ano | findstr /i /c:8554 /c:8000 /c:8889', capture_output=True, text=True, shell=True)

    # # Nếu không có kết quả, khởi động mediatmx server trong một của sổ CMD mới để theo dõi
    # if not result.stdout:
    #     print("Starting mediatmx server...")
    #     # Chạy trên anaconda prompt nên cần đường dẫn tuyệt đốiđối
    #     completed = subprocess.run(
    #     'start cmd /k E:\\Nam3\\IOT_HD\\Project\\blind_sunglasses\\mediamtx\\mediamtx.exe E:\\Nam3\\IOT_HD\\Project\\blind_sunglasses\\mediamtx\\mediamtx.yml',
    #     shell=True,
    #     creationflags=subprocess.CREATE_NEW_CONSOLE)
        # Nếu chạy trên CMD thì chạy đoạn code dưới
        # completed = subprocess.run(
        # 'start cmd /k mediamtx.exe mediamtx.yml',
        # shell=True,
        # creationflags=subprocess.CREATE_NEW_CONSOLE)
    # else:
    #     print("Mediatmx server is already running.")

    # Khởi động WebSocket server      
    async with serve(echo, "192.168.142.172", 8765) as server:
        print("WebSocket server started on ws://192.168.142.172:8765")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())