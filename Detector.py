import torch
from ultralytics import YOLO
import cv2

class Detector:
    def __init__(self, rtsp_stream):
        self.model = YOLO('yolov8n.pt')
        if torch.cuda.is_available():
            self.model.to('cuda')
            print("Đang sử dụng GPU.")
        else:
            print("Sử dụng CPU.")
        self.stream = rtsp_stream
        self.frame_count = 0
        self.skip_frame = 2
        print("Đã khởi động luồng đọc RTMP.")

    def run(self):
        while True: 
            ret, frame = self.stream.read()
            if (not ret) or (frame is None):
                print("Không đọc được frame")
                break
            if (self.frame_count % self.skip_frame) == 0:
                results = self.model(frame)
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
            cv2.imshow("RTMP Stream Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.stream.release()
        cv2.destroyAllWindows()