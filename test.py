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
from notice import FirebaseService


from notice import FirebaseService
import json


device_id = "U8F-MKH-GJ6"
print("[FIREBASE] run.")
try:
    firebase_service = FirebaseService("service_account.json")
    ref = f"tokens/device"
    doc = firebase_service.get_document(ref)
    if not doc:
        print("[ERROR] No token data found in Firebase.")


    matched_token = None
    for key, value in doc.items():
        if value == device_id:
            matched_token = key
            break
    if matched_token is None:
        print(f"[ERROR] No token found for device ID: {device_id}")

    firebase_service.send_notification(
        title="Unconscious Alert",
        body="The user is unconscious, please check immediately.",
        token=matched_token
    )
    print("[FIREBASE] Alert sent.")
    # Reset flags
    has_fall_confirmed = False
    has_warning_unconscious = False
except Exception as e:
    print("[FIREBASE] Failed to send alert:", e)
