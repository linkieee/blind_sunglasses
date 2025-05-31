import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import messaging
from datetime import datetime
class FirebaseService:
    def __init__(self, cred):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://blind-sunglasses-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
            self.ref = db.reference('/')
        
    def add_document(self, ref, data):
        self.ref = db.reference(ref)
        self.ref.set(data)

    def get_document(self, ref):
        self.ref = db.reference(ref)
        data = self.ref.get()
        if data:
            return data
        else:
            return None
    

    def log_notification(self, device_id, title, body, payload):
        self.ref = db.reference(f"notifications/")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "device_id": device_id,
            "title": title,
            "body": body,
            "payload": payload,
            "timestamp": timestamp
        }   
        self.ref.push(entry)
        print(f"[FIREBASE-DB] Logged notification for {device_id}")
        
    def increment_num_detect(self):
        try:
            num_ref = db.reference("app/num_detect")
            current_val = num_ref.get() or 0
            updated_val = current_val + 1
            num_ref.set(updated_val)
            print(f"[FIREBASE-DB] num_detect updated to {updated_val}")
        except Exception as e:
            print(f"[ERROR] Failed to update num_detect: {e}")


    # def send_notification(self, title, body, token):
    #     print(f"[DEBUG] Sending FCM to token={token}")
    #     message = messaging.Message(
    #         notification=messaging.Notification(
    #             title=title,
    #             body=body,
    #         ),
    #         token=token,
    #     )
    
        # response = messaging.send(message)
        # print(f'Successfully sent message: {response}')   
    
    def send_notification(self, title, body, token):
        print(f"[DEBUG] Sending FCM to token={token}")

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    sound="alert",  # hoặc "alert" nếu bạn dùng alert.mp3 trong res/raw
                    channel_id="emergency_channel",  # phải giống bên Flutter
                    priority="max",
                ),
            ),
            data={
                "title": title,
                "body": body,
            },
            token=token,
        )

        response = messaging.send(message)
        print(f"[FCM] Response: {response}") 
        return response


