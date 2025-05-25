import cv2
from ultralytics.utils import LOGGER
LOGGER.setLevel("ERROR")

from ultralytics import YOLO



import time
from deep_sort_realtime.deepsort_tracker import DeepSort
import asyncio
import websockets
from shared import proximity_event
from shared import proximity_data




class Detector:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.model = YOLO("best_v8n_2.pt")
        self.tracker  = DeepSort(max_age=30)
        self.class_names = self.model.names 


        # self.target_classes = [
        #     "Chair", "Sofa", "Table", "bath unit", "bed", "book", "bottle", "cabinet",
        #     "ceramic tiles", "chair", "couch", "cup", "cupboard", "curtains", "dining table",
        #     "door", "gypsum board", "keyboard", "laptop", "mouse", "shower cabinet",
        #     "sideboard", "table", "trashbin", "tv unit", "tvmonitor", "wall cladding",
        #     "wall cover - 3d tiles", "wall panel", "wardrobe", "window", "stairs"
        # ]
        self.target_classes = [
            "chair", "door", "stair", "table", "wet sign"
        ]
        self.object_sizes = {}
    async def send_alert_ws(self, message):
        try:
            async with websockets.connect("ws://localhost:8765") as websocket:
                await websocket.send(message)
                await websocket.close()

        except Exception as e:
            print("[WebSocket Error]:", e)
    def run(self):
        cap = cv2.VideoCapture(self.stream_url)
        if not cap.isOpened():
            print("Không mở được camera.")
            exit()
        prev_time = 0   

        previous_y2_values = {}
        id2label = {}


        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Tính thời gian hiện tại để tính FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
            prev_time = curr_time

            # Chạy mô hình YOLOv8
            results = self.model(frame, imgsz=640, conf=0.3)  # conf: confidence threshold
            boxes = results[0].boxes

            detections=[]

            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = self.class_names[cls_id]

                if class_name.lower() in [c.lower() for c in self.target_classes]:
                    
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = xyxy.astype(int)
                    conf = float(box.conf[0])
                    detections.append(([x1, y1, x2 - x1, y2 - y1], conf, class_name))

            tracks = self.tracker.update_tracks(detections, frame=frame)

            proximity_alert = False
            for track in tracks:
                if not track.is_confirmed():
                    continue
                track_id = track.track_id
                x1, y1, x2, y2 = [int(i) for i in track.to_ltrb()]
                w, h = x2 - x1, y2 - y1

                size = w*h
                prev_size = self.object_sizes.get(track_id, size)

                delta = size  -prev_size    
                if delta > 3000:
                    severity  ="HIGH"
                elif delta > 1000:
                    severity = "MEDIUM"

                frame_center = frame.shape[1]//2
                object_center = (x1+x2)//2
                
                if object_center < frame_center -100:
                    direction  = "LEFT"
                elif object_center > frame_center + 100:
                    direction = "RIGHT"
                else:
                    direction = "CENTER"
                if size - prev_size >1000: 
                    proximity_alert = True
                    proximity_data["direction"]  = direction
                    proximity_data["severity"] = severity
                    proximity_data["label"] = class_name

                self.object_sizes[track_id] = size                          
                label = f"ID {track_id}"
                if hasattr(track, "det_class") and isinstance(track.det_class, str):
                    label += f" {track.det_class}"
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"ALERT: {class_name}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if proximity_alert:
                cv2.putText(frame, "WARNING: Object approaching!", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 3)
                #asyncio.run(self.send_alert_ws("Object approaching!"))
                proximity_event.set()

                    # Hiển thị FPS
            cv2.putText(frame, f"FPS: {fps:.2f}", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("Foot-level Object Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()
