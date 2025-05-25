import 'package:blind_sunglasses/notification.dart';
import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

class HomeScreen extends StatefulWidget {
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

    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      final title = message.notification?.title ?? "Không có tiêu đề";
      final body = message.notification?.body ?? "Không có nội dung";

      Future.delayed(Duration.zero, () {
        if (!mounted) return;
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (_) => WarningDialog(title: title, content: body),
        );
      });
    });



    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        final title = message.notification?.title ?? "Không có tiêu đề";
        final body = message.notification?.body ?? "Không có nội dung";

        Future.delayed(Duration.zero, () {
          if (!mounted) return;
          showDialog(
            context: context,
            barrierDismissible: false,
            builder: (_) => WarningDialog(title: title, content: body),
          );
        });
      });
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
