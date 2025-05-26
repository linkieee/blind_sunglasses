from gpiozero import DistanceSensor
from datetime import datetime
import websockets
import json
import smbus2 as smbus
import asyncio
import math
import threading
import pyttsx3

ADXL345_ADDRESS = 0x53
POWER_CTL = 0x2D
DATA_FORMAT = 0x31
DATAX0 = 0x32

bus = smbus.SMBus(1) 

sensor1 = DistanceSensor(echo=24, trigger=23, max_distance=2.0)
sensor2 = DistanceSensor(echo=27, trigger=17, max_distance=2.0)


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 = nam, 1 = nữ (nếu có)
engine.setProperty('rate', 150)  # Tốc độ nói
engine.setProperty('volume', 0.8)  # Âm lượng (0.0 - 1.0)


def init_adxl345():
    # Bật chế độ đo
    bus.write_byte_data(ADXL345_ADDRESS, POWER_CTL, 0x08)
    # Định dạng dữ liệu: độ phân giải đầy đủ, phạm vi ±2g
    bus.write_byte_data(ADXL345_ADDRESS, DATA_FORMAT, 0x08)


def read_axis_data(register):
    # Đọc 2 byte dữ liệu (16-bit, little endian)
    low = bus.read_byte_data(ADXL345_ADDRESS, register)
    high = bus.read_byte_data(ADXL345_ADDRESS, register + 1)
    # Kết hợp 2 byte thành giá trị 16-bit
    value = (high << 8) | low
    # Xử lý số âm (bù 2)
    if value & (1 << 15):
        value = value - (1 << 16)
    return value

def read_acceleration():
    x = read_axis_data(DATAX0)
    y = read_axis_data(DATAX0 + 2)
    z = read_axis_data(DATAX0 + 4)
    # Chuyển đổi thành đơn vị g (dựa vào scale ±2g, 10-bit)
    factor = 0.0039  # 3.9 mg/LSB (theo datasheet)
    ax = x * factor
    ay = y * factor
    az = z * factor
    return ax, ay, az

async def send_to_server(payload_json: str):
    uri = "ws://192.168.142.167:8765"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(payload_json)
            print(f"Sent: {payload_json}")
    except Exception as e:
        print(f"Error: {e}")
        return None

def read_distance(sensor):
    return round(sensor.distance * 100, 2)

def received_message():
    uri = "ws://192.168.142.167:8765"
    try:
        async def listen():
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv()
                    print(f"Received message: {message}")
                    # Xử lý tin nhắn nếu cần
                    try:
                        if "label" in data and "direction" in data:
                            notice = f"There is a {data['label']} on the {data['direction']}"
                            print(notice)
                            speak_message(notice)
                        else:
                            print("JSON thiếu 'label' hoặc 'direction'")               
                    except:
                        message = "Tin nhắn không hợp lệ"

        asyncio.run(listen())
    except Exception as e:
        print(f"Error in received_message: {e}")

async def main():
    try:
        init_adxl345()
        print("ADXL345 initialized.")

        receive = threading.Thread(target=received_message, daemon=True)
        receive.start()

        while True:
            ax, ay, az = read_acceleration()
            a_total = math.sqrt(ax**2 + ay**2 + az**2)
            print(f"Total={a_total:.2f}g")
            distance1 = read_distance(sensor1)
            distance2 = read_distance(sensor2)
            print(f"Distance Sensor 1: {distance1} cm, Sensor 2: {distance2} cm")
            isSent_distance = False
            isSent_acceleration = False
            if distance1 > 0 and distance2 > 0 and (distance1 < 100 or distance2 < 100):
                isSent_distance = True
            if a_total > 2.0:
                isSent_acceleration = True
            if isSent_distance or isSent_acceleration:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                payload = {
                    "timestamp": timestamp,
                    "distance1": distance1,
                    "distance2": distance2,
                    "isFall": isSent_acceleration
                }
                payload_json = json.dumps(payload)
                await send_to_server(payload_json)
            await asyncio.sleep(3) 
    except Exception as e:
            print(f"Error in main loop: {e}")

def speak_message(message):
    try:
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"Lỗi phát âm: {e}")

if __name__ == "__main__":
    asyncio.run(main())