import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import messaging

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

    def send_notification(self, title, body, token):
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        response = messaging.send(message)
        print(f'Successfully sent message: {response}')    
    

