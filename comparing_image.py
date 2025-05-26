import cv2
import time

class ImageComparer:
    def __init__(self):
        self.last_frame = None

    def capture_frame(self, cap):
        if cap is not None:
            ret, frame = cap.read()
            if ret:
                return frame
        return None
    def calculate_similarity(self, img1, img2):
        if img1 is None or img2 is None:
            return None
        diff = cv2.absdiff(img1, img2)
        return cv2.mean(diff)[0]
    
    def monitor_for_fall(self, frame_streamer, on_confirmed_callback=None, threshold=20.0, duration=30, interval = 2):
        print("[COMPARE] start monitor in 30s by image")
        stable_count = 0
        previous_frame = None
        
        start_time = time.time()


        # while time.time() - start_time<duration:
        #     frame = self.capture_frame(cap)
        #     if frame is None:
        #         print("[COMPARE] Không capture được khung hình.")
        #         time.sleep(interval)
        #         continue
        while time.time() - start_time < duration:
            frame = frame_streamer.read()
            if frame is None:
                continue
            
            if previous_frame is not None:
                similarity = self.calculate_similarity(previous_frame, frame)
                print(f"[COMPARE] Similarity: {similarity:.2f}")
                if similarity<threshold:
                    stable_count+=1
            previous_frame = frame
            time.sleep(interval)
        
        print(f"[COMPARE] result: {stable_count} frame stabilization for {duration} second.")
        if stable_count>=(duration//interval)*0.7:
            print("[ALERT] Detect unconscious user!")
            if on_confirmed_callback:
                on_confirmed_callback()
            else:
                print("[SAFE] have movement, not unconscious.")