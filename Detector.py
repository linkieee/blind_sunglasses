import torch
from ultralytics import YOLO
import cv2
import os
from datetime import datetime

# Class này dùng để phát hiện đối tượng trong luồng RTSP phục vụ cho tracking
# Sửa file này cho deepsort

class Detector:
    # Khởi tạo đối tượng Detector với luồng RTSP
    def __init__(self, rtsp_stream):
        self.model = YOLO('yolov8n.pt')
        if torch.cuda.is_available():
            self.model.to('cuda')
            print("Us GPU.")
        else:
            print("Using CPU.")
        self.stream = rtsp_stream
        self.frame_count = 0
        self.skip_frame = 2
        # Biến này dùng để xác định có capture ảnh hay không
        self.isCapture = False
        print("Set RTSP read stream...")

    # Hàm chạy thử để test detect bằng yolo
    def run(self):
        while True: 
            ret, frame = self.stream.read()
            if (self.isCapture):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"capture_{timestamp}.jpg", frame)
                self.isCapture = False
                print('Absolute path of file: ', os.path.abspath(f"capture_{timestamp}.jpg"))
            
            if (not ret) or (frame is None):
                print("Don't read frame!!")
                break
            if (self.frame_count % self.skip_frame) == 0:
                results = self.model(frame, verbose=False)
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            conf = float(box.conf[0])
                            cls_id = int(box.cls[0])
                            label = f"{self.model.names[cls_id]} {conf:.2f}"
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, label, (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            self.frame_count += 1
            cv2.imshow("RTSP Stream Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.stream.release()
        cv2.destroyAllWindows()

    # Hàm để xác định có capture ảnh hay không được gọi ở hàm echo trong server.py
    def isCapture(self, capture):
        self.isCapture = capture
