import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/material.dart';
import 'package:blind_sunglasses/emergencycall.dart';
import 'package:blind_sunglasses/notification.dart';
import 'package:firebase_core/firebase_core.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  await NotificationService.instance.setupFlutterNotifications();
  await NotificationService.instance.showNotification(message);
}

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
    );
    print('Permission status: ${settings.authorizationStatus}');
  }

  Future<void> setupFlutterNotifications() async {
    if (_isFlutterLocalNotificationsInitialized) return;

    // 🔔 Channel for emergency calls
    const emergencyChannel = AndroidNotificationChannel(
      'emergency_channel',
      'Emergency Notifications',
      description: 'Thông báo cuộc gọi khẩn cấp từ kính thông minh',
      importance: Importance.max,
      playSound: true,
    );

    // 🔔 Channel for regular high-priority notifications
    const highChannel = AndroidNotificationChannel(
      'high_importance_channel',
      'High Importance Notifications',
      description: 'This channel is used for important notifications.',
      importance: Importance.high,
      playSound: true,
    );

    final androidPlugin = _localNotifications.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();

    await androidPlugin?.createNotificationChannel(emergencyChannel);
    await androidPlugin?.createNotificationChannel(highChannel);

    const initSettings = InitializationSettings(
      android: AndroidInitializationSettings('@mipmap/ic_launcher'),
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: (details) {
        if (details.payload == 'call_request') {
          navigatorKey.currentState?.push(
            MaterialPageRoute(builder: (_) => const EmergencyCall()),
          );
        }
      },
    );

    _isFlutterLocalNotificationsInitialized = true;
  }

  Future<void> showNotification(RemoteMessage message) async {
    final type = message.data['type'] ?? '';
    if (type == 'call_request') {
      await _showAlarmNotification(message);
      return;
    }

    final context = navigatorKey.currentContext;
    final title = message.notification?.title ?? "Không có tiêu đề";
    final body = message.notification?.body ?? "Không có nội dung";

    if (context != null) {
      showDialog(
        context: context,
        builder: (_) => WarningDialog(title: title, content: body),
      );
    } else {
      await _localNotifications.show(
        message.hashCode,
        title,
        body,
        const NotificationDetails(
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

  Future<void> _showAlarmNotification(RemoteMessage message) async {
    await _localNotifications.show(
      0,
      'EMERGENCY CALL',
      'Users may be in danger after falling!',
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'emergency_channel',
          'Emergency Notifications',
          channelDescription: 'Thông báo cuộc gọi khẩn cấp từ người dùng kính',
          importance: Importance.max,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
          playSound: true,
          sound: RawResourceAndroidNotificationSound('alarm'),
          enableVibration: true,
          timeoutAfter: 30000,
          visibility: NotificationVisibility.public,
          fullScreenIntent: true,
        ),
      ),
      payload: 'call_request',
    );
  }

  Future<void> _setupMessageHandlers() async {
    FirebaseMessaging.onMessage.listen((message) {
      print('Foreground message received: ${message.notification?.title}');
      showNotification(message);
    });

    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      print('App opened from notification: ${message.notification?.title}');
      showNotification(message);
    });
  }
}
