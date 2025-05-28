import 'package:blind_sunglasses/notification.dart';
import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:blind_sunglasses/emergencycall.dart'; // màn hình khẩn cấp

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    FirebaseMessaging.instance.requestPermission();

    FirebaseMessaging.instance.getToken().then((token) {
      print("🔑 FCM Token: $token");
    });

    // Khi đang mở app (foreground)
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      _handleNotification(message);
    });

    // Khi mở app qua thông báo
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      _handleNotification(message);
    });
  }

  void _handleNotification(RemoteMessage message) {
    final data = message.data;
    final title = message.notification?.title ?? "Không có tiêu đề";
    final body = message.notification?.body ?? "Không có nội dung";

    Future.delayed(Duration.zero, () {
      if (!mounted) return;

      if (data['type'] == 'call_request') {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => EmergencyCallNoti()),
        );
      } else {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (_) => WarningDialog(title: title, content: body),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Home'),
      ),
      body: Center(
        child: Text('HomeScreen'),
      ),
    );
  }
}
