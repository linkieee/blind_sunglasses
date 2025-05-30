import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';


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
