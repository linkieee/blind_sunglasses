import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/material.dart';
import 'package:blind_sunglasses/emergencycall.dart';
import 'package:blind_sunglasses/notification.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:audioplayers/audioplayers.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  await NotificationService.instance.setupFlutterNotifications();
  await NotificationService.instance.showNotification(message);
}

bool isEmergencyScreenOpen = false;


class NotificationService {
  NotificationService._();
  static final NotificationService instance = NotificationService._();

  final _messaging = FirebaseMessaging.instance;
  final _localNotifications = FlutterLocalNotificationsPlugin();
  bool _isFlutterLocalNotificationsInitialized = false;

  Future<void> initialize() async {
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
    await _requestPermission();
    await _setupMessageHandlers();

    final token = await _messaging.getToken();
    print('🔑 FCM Token: $token');
  }

  Future<void> _requestPermission() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
      announcement: false,
      carPlay: false,
      criticalAlert: false,
    );
    print('Permission status: ${settings.authorizationStatus}');
  }

  Future<void> setupFlutterNotifications() async {
    if (_isFlutterLocalNotificationsInitialized) return;

    const channel = AndroidNotificationChannel(
      'emergency_channel',
      'Emergency Notifications',
      description: 'Thông báo cuộc gọi khẩn cấp từ kính thông minh',
      importance: Importance.max,
      playSound: true,
    );

    await _localNotifications.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>()?.createNotificationChannel(
      channel,
    );

    const initializationSettings = InitializationSettings(
      android: AndroidInitializationSettings('@mipmap/ic_launcher'),
    );

    await _localNotifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (details) {
        if (details.payload == 'Unconscious Alert') {
          navigatorKey.currentState?.push(
            MaterialPageRoute(builder: (_) => const EmergencyCall()),
          );
        }
      },
    );

    _isFlutterLocalNotificationsInitialized = true;
  }

  Future<void> showNotification(RemoteMessage message) async {
    final type = message.data['title'];
    final context = navigatorKey.currentContext;
    final title = message.notification?.title ?? message.data['title'] ?? "Không có tiêu đề";
    final body  = message.notification?.body  ?? message.data['body']  ?? "Không có nội dung";

    if (type == 'Unconscious Alert') {
      if (context != null && !isEmergencyScreenOpen) {
        isEmergencyScreenOpen = true;
        navigatorKey.currentState?.push(
          MaterialPageRoute(
            builder: (_) => EmergencyCall(
              onClose: () => isEmergencyScreenOpen = false,
            ),
          ),
        );
      } else {
        await _showAlarmNotification(message);
        playAlarm();
      }
      return;
    }

    if (context != null) {
      showDialog(
        context: context,
        builder: (_) => WarningDialog(title: title, content: body),
      );
    } else {
      RemoteNotification? notification = message.notification;
      AndroidNotification? android = message.notification?.android;
      if (notification != null && android != null) {
        await _localNotifications.show(
          notification.hashCode,
          title,
          body,
          NotificationDetails(
            android: AndroidNotificationDetails(
              'high_importance_channel',
              'High Importance Notifications',
              channelDescription: 'This channel is used for important notifications.',
              importance: Importance.high,
              priority: Priority.high,
              icon: '@mipmap/ic_launcher',
            ),
          ),
          payload: message.data.toString(),
        );
      }
    }
  }

  Future<void> _showAlarmNotification(RemoteMessage message) async {
    // Ưu tiên lấy từ message.notification nếu có, sau đó tới message.data, cuối cùng là mặc định
    final title = message.notification?.title ??
        message.data['title'] ??
        'EMERGENCY ALERT';

    final body = message.notification?.body ??
        message.data['body'] ??
        'Users may be in danger after falling!';

    await _localNotifications.show(
      0,
      title,
      body,
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'emergency_channel',
          'Emergency Notifications',
          channelDescription: 'Thông báo cuộc gọi khẩn cấp từ người dùng kính',
          importance: Importance.max,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
          playSound: true,
          sound: null,
          enableVibration: true,
          timeoutAfter: 30000,
          visibility: NotificationVisibility.public,
          fullScreenIntent: true,
        ),
      ),
      payload: 'Unconscious Alert',
    );
  }

  void playAlarm() async {
    final player = AudioPlayer();
    await player.play(AssetSource('alarm.mp3'));
  }


  Future<void> _setupMessageHandlers() async {
    await setupFlutterNotifications();

    FirebaseMessaging.onMessage.listen((message) {
      print('Received message: ${message.notification?.title}');
      showNotification(message);
    });

    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      showNotification(message);
    });
  }
}
