import cv2
import threading

class RTSPStream:
    def __init__(self,url):
        self.cap = cv2.VideoCapture(url)
        # Giảm độ phân giải để tăng tốc
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        self.ret, self.frame = self.cap.read()
        self.stopped = False
        threading.Thread(target=self.update, daemon=True).start()
        print("Đã khởi động luồng đọc RTMP.")

    def isOpened(self):
        return self.cap.isOpened()

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def release(self):
        self.stopped = True
        self.cap.release()
