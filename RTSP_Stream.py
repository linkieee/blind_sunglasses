import cv2
import threading

# Sử dụng model YOLOv8 nhỏ để tăng tốc
# model = YOLO('yolov8n.pt')

# Nếu có GPU thì dùng
# if torch.cuda.is_available():
#     model.to('cuda')
#     print("Đang sử dụng GPU.")
# else:
#     print("Sử dụng CPU.")
# stream_url = "rtsp://192.168.162.42:1935/live/stream" 

# Class để đọc RTMP stream theo luồng riêng
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

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def release(self):
        self.stopped = True
        self.cap.release()

    
# Địa chỉ RTMP
 # Cập nhật nếu khác

# Khởi động stream
# stream = RTMPStream(stream_url)

# frame_count = 0
# skip_frame = 2  # xử lý mỗi 2 frame

# while True:
#     ret, frame = stream.read()
#     if not ret or frame is None:
#         print("Không đọc được frame")
#         break

#     if frame_count % skip_frame == 0:   
#         results = model(frame)

#         for result in results:
#             boxes = result.boxes
#             if boxes is not None:
#                 for box in boxes:
#                     x1, y1, x2, y2 = map(int, box.xyxy[0])
#                     conf = float(box.conf[0])
#                     cls_id = int(box.cls[0])
#                     label = f"{model.names[cls_id]} {conf:.2f}"

#                     # Vẽ bounding box và label
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                     cv2.putText(frame, label, (x1, y1 - 10),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#     frame_count += 1

#     cv2.imshow("RTMP Stream Detection", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# stream.release()
# cv2.destroyAllWindows()
