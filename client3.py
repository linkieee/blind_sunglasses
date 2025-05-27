import paho.mqtt.client as mqtt
import json
import time

# Thông tin kết nối broker
mqtt_broker = "172.16.16.30"  # Hoặc IP nội bộ như "192.168.142.167"
mqtt_port = 1883
mqtt_topic_command = "sunglasses/commands"
mqtt_topic_alerts = "sunglasses/alerts"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[CLIENT] Connected to MQTT broker successfully.")
        message = {
            "isFall": True
            #"command":"start"
        }
        client.publish(mqtt_topic_command, json.dumps(message))
        print(f"[CLIENT] Sent command: {message}")


        client.subscribe(mqtt_topic_alerts)
        print(f"[CLIENT] Subscribed to: {mqtt_topic_alerts}")

    else:
        print(f"[CLIENT] Failed to connect. Return code: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        print(f"[ALERT] Topic: {msg.topic} | Message: {data}")
    except Exception as e:
        print(f"[ERROR] Failed to parse message: {e}")






def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_broker, mqtt_port, 60)

    client.loop_forever()

if __name__ == "__main__":
    main()
