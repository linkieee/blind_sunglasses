import cv2
import threading
import queue
import time

class FrameStreamer:
    def __init__(self, stream_url, maxsize=10):
        self.cap = cv2.VideoCapture(stream_url)
        self.frame_queue = queue.Queue(maxsize=maxsize)
        self.running = False
        self.stream_failed = False

    def start(self):
        self.running = True
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        failure_count = 0
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                failure_count += 1
                if failure_count >= 30:  # sau ~0.3s nếu fail liên tục
                    self.stream_failed = True
                continue
            failure_count = 0
            self.stream_failed = False
            if self.frame_queue.full():
                self.frame_queue.get()
            self.frame_queue.put(frame)
            time.sleep(0.01)

    def read(self):
        try:
            return self.frame_queue.get(timeout=1)
        except queue.Empty:
            return None

    def stop(self):
        self.running = False
        self.cap.release()
