# -*- coding: iso-8859-1 -*-
import paho.mqtt.client as mqtt
from ultrasonic import UltrasonicSensor
from adxl345 import Acceloremeter
import time
import json
from datetime import datetime
import threading
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
from pydub.effects import speedup

def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio = AudioSegment.from_file(fp, format="mp3")
    faster_audio = speedup(audio, playback_speed=1.5)
    play(faster_audio)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"Received message: {data}")
        label = data.get('label', None)
        
        direction = data.get('direction', None)
        if direction == 'LEFT':
            direction = 'on the left'
        elif direction == 'RIGHT':
            direction = 'on the right'
        elif direction == 'CENTER':
            direction = 'in the middle'
        else:
            direction = None
    
        if label and direction:
            speak(f"Warning, there is a {label} {direction}.")
        else:
            print("JSON missing 'label' or 'direction'")
    except json.JSONDecodeError:
        print("Received invalid JSON message.")
    except Exception as e:
        print(f"Error processing message: {e}")


def on_connect(client, userdata, flags, rc):
    global is_connected_to_mqtt
    if rc == 0:
        print ("Connected to MQTT broker successfully.")
        is_connected_to_mqtt = True
    else:
        print(f"Failed to connect, return code {rc}")
        is_connected_to_mqtt = False

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker.") 



def check_every_seconds(client):
    global right_ultrasonic_value
    global left_ultrasonic_value

    global check_thread_running
    check_thread_running = True
    global check_thread

    threshold_1 =  right_ultrasonic_value
    threshold_2 = left_ultrasonic_value

    i = 0

    while i < 30 and check_thread_running:
        if right_ultrasonic_value - 2 < threshold_1 < right_ultrasonic_value + 2 and left_ultrasonic_value -2 < threshold_2 < left_ultrasonic_value + 2:
            print("========================================================================================================================")
            print(f"Check {i+1} time...")
            print(f"Right Ultrasonic Value: {right_ultrasonic_value} cm \nLeft Ultrasonic Value: {left_ultrasonic_value} cm")
            i += 1
            time.sleep(1)
        else:
            print("Values changed, stopping check.")
            return
    if check_thread_running:
        client.publish(publish_topic2, json.dumps({"waring": "unconscious"}))
        print({"waring": "unconscious"})
    check_thread_running = False
    

right_ultrasonic_value = 0
left_ultrasonic_value = 0
check_thread_running = True
check_thread = None
is_connected_to_mqtt = False

publish_topic = "blind_sunglasses/Calert"
publish_topic2 = "blind_sunglasses/warning"
subscribe_topic = "blind_sunglasses/notice"

def main():
    global is_connected_to_mqtt
    global right_ultrasonic_value
    global left_ultrasonic_value
    global check_thread_running
    global check_thread

    client = mqtt.Client(clean_session=True)
    client.connect("172.16.16.217", 1883)
    client.on_connect = on_connect 
    client.on_disconnect = on_disconnect
    client.loop_start()


    while not is_connected_to_mqtt:
        print("Waiting for MQTT connection...")
        print(is_connected_to_mqtt)
        time.sleep(2)

    client.on_message = on_message
    client.subscribe(subscribe_topic, qos=1)

    left_ultrasonic = UltrasonicSensor(24, 23)
    print("Ultrasonic Sensor 1 initialized.")
    right_ultrasonic_2 = UltrasonicSensor(27, 17)
    print("Ultrasonic Sensor 2 initialized.")
    adxl345 = Acceloremeter()  
    print("ADXL345 Accelerometer initialized.")

    while True:
        try:
            acceloremeter_value = adxl345.get_acceleration()
            left_ultrasonic_value = left_ultrasonic.get_distance()
            right_ultrasonic_value = right_ultrasonic_2.get_distance()
            print("========================================================================================================================")
            # print(f"Left Ultrasonic Distance: {left_ultrasonic_value} cm\nRight Ultrasonic Distance: {right_ultrasonic_value} cm\nAcceleration: {acceloremeter_value:.2f} g")
            is_send_distance = False
            is_send_acceleration = False
            if left_ultrasonic_value > 0 and right_ultrasonic_value > 0 and (left_ultrasonic_value < 100 or right_ultrasonic_value < 100):
                is_send_distance = True
            else:
                is_send_distance = False
            
            if acceloremeter_value > 2.0:
                is_send_acceleration = True
                print("Acceleration exceeds threshold, checking every second...")
                if check_thread_running:
                    check_thread_running = False
                    if check_thread is not None:
                        check_thread.join()
                
                check_thread = threading.Thread(target=check_every_seconds, args=(client,))
                check_thread.start() 
            else:
                is_send_acceleration = False 

            if is_send_distance or is_send_acceleration:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                payload = {
                    "timestamp": timestamp,
                    "left_distance": left_ultrasonic_value,
                    "right_distance2": left_ultrasonic_value,
                    "isFall": is_send_acceleration
                }
                print(f"Publishing payload: {payload}")
                payload_json = json.dumps(payload)
                client.publish(publish_topic, payload_json, qos=1)
            time.sleep(3)  # Adjust the sleep time as needed
        except Exception as e:
            print(f"Error in main loop: {e}")


if __name__ == "__main__":
    main()
