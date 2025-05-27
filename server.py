import asyncio
import threading
import subprocess
import time
from websockets.asyncio.server import serve
from shared import proximity_event
from shared import proximity_data
from Detector import Detector
from typing import Set
import json
import cv2
from comparing_image import ImageComparer
from RTSP_Stream import FrameStreamer
import paho.mqtt.client as mqtt


# địa chị private của máy hoặc localhost
stream_url = "rtsp://172.16.16.15:8554/cam1"
detector_started = threading.Event()
comparer = ImageComparer()
frame_streamer = None
main_loop = None
isCompare = False
mqtt_client = None
mqtt_broker  = "172.16.16.217"
mqtt_port = 1883
mqtt_topic_command = "sunglasses/commands"
mqtt_topic_alert = "sunglasses/alerts"
mqtt_topic_Calert = "blind_sunglasses/Calert"
mqtt_topic_warning = "blind_sunglasses/warning"
mqtt_topic_notice = "blind_sunglasses/notice"
detector = Detector()


def mqtt_alert(topic, message, qos=1):
    result = mqtt_client.publish(topic, message, qos=qos)
    if result.rc == 0:
        print(f"[MQTT] Sent to {topic} with QoS {qos}: {message}")
    else:
        print(f"[MQTT] Failed to send to {topic}: {mqtt.error_string(result.rc)}")

def run_detector():
    print("[SYSTEM] Detector is running...")
    global frame_streamer

    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print("[ERROR] Stream not available. Detector will not start.")
        cap.release()
        return
    
    cap.release()
    frame_streamer = FrameStreamer(stream_url)
    frame_streamer.start()
    detector.resume()

    try:
        detector.run(frame_streamer)
    except Exception as e:
            
        print(f"[DETECTOR] Error: {e}")
    print("[SYSTEM] Detector stopped.")
    frame_streamer.stop()
    global detector_started
    detector_started.clear()


# hàm xử lý kết nối từ client - nhận dữ liệu từ client và kiểm tra khoảng cách

def on_message(client, userdata, msg):
    global isCompare
    topic = msg.topic
    payload = msg.payload.decode()
    
    print(f"[MQTT] Message from topic {topic}:{payload}")
    try:
        data = json.loads(payload)
    except Exception as e:
        print(f"[MQTT] JSON decode error: {e}")
        return
    if data.get("command") == "start":
        if not detector_started.is_set():
            print("[SYSTEM] Starting detection...")
            threading.Thread(target=run_detector, daemon=True).start()
            detector_started.set()
            mqtt_alert(mqtt_topic_alert, "start successfull")
        else:
            print("[SYSTEM] Detector already running. Ignoring start command.")
    elif data.get("isFall") is True:
        print("[FALL] fall signal from client, monitoring in 30s")
        isCompare = True
        detector.pause()

        def on_fall_confirmed():
            print("[SYSTEM] Fall confirmed callback triggered by image comparison")
            try:
                mqtt_alert(mqtt_topic_alert, json.dumps({
                    "type": "compare_fall_confirmed",
                    "method": "image",
                    "message": "Fall confirmed by image similarity",
                    "unconscious": True
                }))
            except Exception as e:
                print("[MQTT] Failed to send compare_fall_confirmed:", e)
        def run_monitor():
            comparer.monitor_for_fall(frame_streamer, on_fall_confirmed)
            print("[SYSTEM] resume detector")
            detector.resume()
            global isCompare
            isCompare = False
        threading.Thread(target=run_monitor, daemon=True).start()


    



async def monitor_proximity():
    global isCompare
    while True:
        await asyncio.sleep(5)
        if proximity_event.is_set():
            print("[SYSTEM] Detected proximity alert, broadcasting...")
            try:
                data = {
                    "type": "proximity_alert",
                    "direction": proximity_data.get("direction", "UNKNOWN"),
                    "severity": proximity_data.get("severity", "LOW"),
                    "label": proximity_data.get("label", "unknown")
                }
                mqtt_alert(mqtt_topic_notice, json.dumps(data))
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



def init_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.subscribe(mqtt_topic_command)
    mqtt_client.subscribe(mqtt_topic_Calert)
    mqtt_client.subscribe(mqtt_topic_warning)
    mqtt_client.loop_start()
    print(f"[MQTT] Connected to {mqtt_broker}:{mqtt_port}, subscribed to {mqtt_topic_command}")




# Hàm chính để khởi động server và kiểm tra trạng thái của mediatmx server
async def main():
    # khởi chạy luồng detector trên một thread riêng
    # subprocess.Popen(["mediamtx\mediamtx.exe"], shell=True)
    global frame_streamer, main_loop
    main_loop = asyncio.get_running_loop()
    # print("[SYSTEM] Starting detector thread...")
    # threading.Thread(target=run_detector, daemon=True).start()
    completed = subprocess.run(
    'start cmd /k mediamtx\mediamtx.exe mediamtx\mediamtx.yml',
    shell=True,
    creationflags=subprocess.CREATE_NEW_CONSOLE)
    # Kiểm tra xem mediatmx server đã chạy chưa
    result = subprocess.run('netstat -ano | findstr /i /c:8554 /c:8000 /c:8889', capture_output=True, text=True, shell=True)

    # Nếu không có kết quả, khởi động mediatmx server trong một của sổ CMD mới để theo dõi
    if not result.stdout:
        print("[SYSTEM] Starting mediatmx server...")
        # Chạy trên anaconda prompt nên cần đường dẫn tuyệt đốiđối
        # completed = subprocess.run(
        # 'start cmd /k E:\\Nam 3\\IoTHD\\server2\\blind_sunglasses\\mediamtx\\mediamtx.exe E:\\Nam 3\\IoTHD\\server2\\blind_sunglasses\\mediamtx\\mediamtx.yml',
        # shell=True,
        # creationflags=subprocess.CREATE_NEW_CONSOLE)
        # Nếu chạy trên CMD thì chạy đoạn code dưới

        
    else:
        print("[SYSTEM] Mediatmx server is already running.")

    #khởi động mqtt server
    init_mqtt()

    await monitor_proximity()
if __name__ == "__main__":
    asyncio.run(main())

