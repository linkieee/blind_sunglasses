from notice import FirebaseService

while True:
    notice = FirebaseService("E:\\Nam3\\IOT_HD\\Project\\blind_sunglasses\\blind_sunglasses\\service_account.json")
    try:
        ref = input("Enter the reference path (e.g., 'blind_sunglasses/notice'): ")
        if notice.get_document(ref) is None:
            print("No data found at the specified reference path.")
            continue
        
        data = notice.get_document(ref)
        print(f"Data at {ref}: {data}")
        token=f"{data['AAAA']}"
        print(token)

        notice.send_notification(body="Test Notification", title="Test Title", token=token)
        
    except Exception as e:
        print(f"An error occurred: {e}")