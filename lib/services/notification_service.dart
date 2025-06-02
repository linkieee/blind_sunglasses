// notification_service.dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/material.dart';
import 'package:blind_sunglasses/emergencycall.dart';
import 'package:blind_sunglasses/notification.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:shared_preferences/shared_preferences.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  await NotificationService.instance.setupFlutterNotifications();
  await NotificationService.instance.showNotification(message);
}

bool isEmergencyScreenOpen = false;
bool isNotificationOpen = false;


class NotificationService {
  NotificationService._();
  static final NotificationService instance = NotificationService._();

  final _messaging = FirebaseMessaging.instance;
  final _localNotifications = FlutterLocalNotificationsPlugin();

  Future<void> initialize() async {
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
    await _requestPermission();
    await setupFlutterNotifications();
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
    final plugin = _localNotifications.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();

    for (String sound in ['sound1', 'sound2', 'sound3']) {
      final channel = AndroidNotificationChannel(
        'emergency_channel_$sound',
        'Emergency Notifications ($sound)',
        description: 'This channel is used for $sound alerts.',
        importance: Importance.max,
        playSound: true,
        sound: RawResourceAndroidNotificationSound(sound),
      );
      await plugin?.createNotificationChannel(channel);
      print('Created channel: ${channel.id}');
    }

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
  }

  Future<void> updateSoundSetting(String selectedSound) async {
    final prefs = await SharedPreferences.getInstance();
    final channelId = 'emergency_channel_$selectedSound';
    await prefs.setString('selectedChannelId', channelId);
    print('Switched to channel: $channelId');
  }

  Future<void> showNotification(RemoteMessage message) async {
    final prefs = await SharedPreferences.getInstance();
    final isEnabled = prefs.getBool('notificationEnabled') ?? true;
    if (!isEnabled) {
      print("Notification blocked by user settings.");
      return;
    }

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
      }
      return;
    }

    if (type == 'Warning Notification') {
      if (context != null && !isNotificationOpen) {
        isNotificationOpen = true;
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (_) => WarningDialog(title: title, content: body),
        ).then((_) => isNotificationOpen = false);
      } else {
        await _localNotifications.show(
          0,
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
    final prefs = await SharedPreferences.getInstance();
    final isEnabled = prefs.getBool('notificationEnabled') ?? true;
    if (!isEnabled) {
      print("Alarm notification blocked by user settings.");
      return;
    }
    final selectedChannelId = prefs.getString('selectedChannelId') ?? 'emergency_channel_sound2';
    final sound = selectedChannelId.replaceAll('emergency_channel_', '');

    print('Using channel ID: $selectedChannelId with sound: $sound');

    final title = message.notification?.title ?? message.data['title'] ?? 'EMERGENCY ALERT';
    final body = message.notification?.body ?? message.data['body'] ?? 'User may be in danger.';

    await _localNotifications.show(
      0,
      title,
      body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          selectedChannelId,
          'Emergency Notifications',
          channelDescription: 'Emergency notifications with $sound',
          importance: Importance.max,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
          playSound: true,
          sound: RawResourceAndroidNotificationSound(sound),
          enableVibration: true,
          fullScreenIntent: true,
          visibility: NotificationVisibility.public,
        ),
      ),
      payload: 'Unconscious Alert',
    );
  }

  Future<void> _setupMessageHandlers() async {
    FirebaseMessaging.onMessage.listen((message) {
      print('📩 Received message: ${message.notification?.title}');
      showNotification(message);
    });

    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      showNotification(message);
    });
  }
}
