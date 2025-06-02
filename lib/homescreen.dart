import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';

class NotificationModel {
  final String id;
  final String title;
  final String body;
  final String deviceId;
  final String timestamp;

  NotificationModel({
    required this.id,
    required this.title,
    required this.body,
    required this.deviceId,
    required this.timestamp,
  });

  factory NotificationModel.fromJson(String key, Map<dynamic, dynamic> json) {
    return NotificationModel(
        id: key,
        title: json['title'] ?? '',
        body: json['body'] ?? '',
        deviceId: json['device_id'] ?? '',
        timestamp: json['timestamp'] ?? ''
    );
  }

  DateTime get dateTime {
    try {
      return DateFormat("yyyy-MM-dd HH:mm:ss").parse(timestamp);
    } catch (e) {
      print("Parse error: $e - timestamp: $timestamp");
      return DateTime.now();
    }
  }

  String get formattedTime {
    try {
      final date = DateFormat("yyyy-MM-dd HH:mm:ss").parse(timestamp);
      return DateFormat('dd/MM/yyyy HH:mm').format(date);
    } catch (e) {
      return 'Unknown time';
    }
  }
}

class HomeScreen extends StatefulWidget {
  final VoidCallback? onShowAll;
  const HomeScreen({Key? key, this.onShowAll}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final DatabaseReference _database = FirebaseDatabase.instance.ref();

  String appStatus = "off";
  int numDetect = 0;
  List<NotificationModel> notifications = [];
  int nowHourCount = 0;
  int prevHourCount = 0;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _setupFirebaseListeners();
    _loadNotifications();
  }

  void _loadNotifications() async {
    try {
      setState(() {
        isLoading = true;
      });

      final snapshot = await _database.child('notifications').get();

      if (snapshot.exists && snapshot.value != null) {
        final data = snapshot.value as Map<dynamic, dynamic>;
        final List<NotificationModel> loadedNotifications = [];
        int nowHour = DateTime.now().hour;
        int prevHour = (nowHour - 1) % 24;
        int nowCount = 0;
        int prevCount = 0;

        data.forEach((key, value) {
          if (value is Map) {
            try {
              final notification = NotificationModel.fromJson(key, value);
              loadedNotifications.add(notification);

              // Count notifications by hour
              try {
                final notificationHour = notification.dateTime.hour;
                if (notificationHour == nowHour) nowCount++;
                if (notificationHour == prevHour) prevCount++;
              } catch (e) {
                print('Error parsing hour for notification ${notification.id}: $e');
              }
            } catch (e) {
              print('Error parsing notification $key: $e');
            }
          }
        });

        // Sort notifications by timestamp (newest first)
        loadedNotifications.sort((a, b) => b.dateTime.compareTo(a.dateTime));

        setState(() {
          notifications = loadedNotifications;
          nowHourCount = nowCount;
          prevHourCount = prevCount;
          isLoading = false;
        });
      } else {
        setState(() {
          notifications = [];
          nowHourCount = 0;
          prevHourCount = 0;
          isLoading = false;
        });
      }
    } catch (e) {
      print('Error loading notifications: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  void _setupFirebaseListeners() {
    // Listen to app status and detection count
    _database.child('app').onValue.listen((event) {
      if (event.snapshot.exists) {
        final data = Map<String, dynamic>.from(event.snapshot.value as Map);
        setState(() {
          appStatus = data['status'] ?? "off";
          numDetect = data['num_detect'] ?? 0;
        });
      }
    });

    // Listen to notifications for real-time updates
    _database.child('notifications').onValue.listen((event) {
      _loadNotifications();
    });
  }

  List<BarChartGroupData> _generateChartData() {
    return [
      BarChartGroupData(
        x: 0,
        barRods: [
          BarChartRodData(
            toY: prevHourCount.toDouble(),
            color: const Color(0xFFFF6B6B),
            width: 48,
            borderRadius: BorderRadius.circular(4),
          ),
        ],
      ),
      BarChartGroupData(
        x: 1,
        barRods: [
          BarChartRodData(
            toY: nowHourCount.toDouble(),
            color: const Color(0xFFFF6B6B),
            width: 48,
            borderRadius: BorderRadius.circular(4),
          ),
        ],
      ),
    ];
  }

  String _formatTimestamp(String timestamp) {
    try {
      final dateTime = DateFormat("yyyy-MM-dd HH:mm:ss").parse(timestamp);
      return DateFormat('dd/MM/yyyy HH:mm').format(dateTime);
    } catch (e) {
      return timestamp;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        image: DecorationImage(
          image: AssetImage('lib/assets/images/background.jpg'),
          fit: BoxFit.cover,
        ),
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Card
                Card(
                  color: Colors.white,
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Good Morning',
                                style: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.grey[800],
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Welcome to your smart eyewear',
                                style: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontSize: 15,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          width: 60,
                          height: 60,
                          decoration: const BoxDecoration(
                            color: Color(0xFF368C8B),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.person,
                            color: Colors.white,
                            size: 30,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 20),

                // Smart Glasses Image
                Card(
                  color: Colors.white,
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Image.asset(
                      'lib/assets/images/glasses.jpg',
                      fit: BoxFit.fitWidth,
                      width: double.infinity,
                      height: 180,
                    ),
                  ),
                ),

                const SizedBox(height: 20),

                // Latest Notification Card
                if (notifications.isNotEmpty)
                  Card(
                    color: Colors.white,
                    elevation: 4,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Latest',
                                style: TextStyle(
                                  fontFamily: 'Montserrat',
                                  color: Colors.grey[800],
                                  fontSize: 12,
                                ),
                              ),
                              Text(
                                _formatTimestamp(notifications[0].timestamp),
                                style: TextStyle(
                                  fontFamily: 'Montserrat',
                                  color: Colors.grey[600],
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            notifications[0].title,
                            style: TextStyle(
                              fontFamily: 'Montserrat',
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            notifications[0].body,
                            style: TextStyle(
                              fontFamily: 'Montserrat',
                              fontSize: 14,
                              color: Colors.grey[700],
                            ),
                          ),
                          if (notifications[0].deviceId.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 4),
                              child: Text(
                                'Device: ${notifications[0].deviceId}',
                                style: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontSize: 12,
                                  color: Colors.grey[500],
                                ),
                              ),
                            ),
                          const SizedBox(height: 12),
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton(
                              onPressed: widget.onShowAll, // FIX: Thêm widget. prefix
                              child: const Text(
                                'Show all',
                                style: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontSize: 15,
                                  color: Colors.grey,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                // Status + Chart Row
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        children: [
                          SizedBox(
                            width: 170,
                            height: 120,
                            child: Card(
                              color: Colors.white,
                              elevation: 1,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 14.0,
                                ),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      'Active status',
                                      style: TextStyle(
                                        fontFamily: 'Montserrat',
                                        fontSize: 15,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                    Text(
                                      appStatus.toUpperCase(),
                                      style: TextStyle(
                                        fontSize: 20,
                                        fontWeight: FontWeight.bold,
                                        color: appStatus == "on"
                                            ? Colors.green
                                            : Colors.red,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          SizedBox(
                            width: 170,
                            height: 120,
                            child: Card(
                              color: Colors.white,
                              elevation: 1,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 20.0,
                                ),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      'Detections',
                                      style: TextStyle(
                                        fontFamily: 'Montserrat',
                                        fontSize: 15,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                    Text(
                                      numDetect.toString(),
                                      style: const TextStyle(
                                        fontFamily: 'Montserrat',
                                        fontSize: 20,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF368C8B),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      child: SizedBox(
                        width: 240,
                        height: 240,
                        child: Card(
                          color: Colors.white,
                          elevation: 1,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Alert',
                                  style: TextStyle(
                                    fontFamily: 'Montserrat',
                                    fontSize: 15,
                                    color: Colors.grey[600],
                                  ),
                                ),
                                const SizedBox(height: 16),
                                Expanded(
                                  child: BarChart(
                                    BarChartData(
                                      alignment: BarChartAlignment.spaceAround,
                                      maxY: (nowHourCount > prevHourCount ? nowHourCount : prevHourCount).toDouble() + 1,
                                      barTouchData: BarTouchData(
                                        enabled: false,
                                      ),
                                      titlesData: FlTitlesData(
                                        show: true,
                                        bottomTitles: AxisTitles(
                                          sideTitles: SideTitles(
                                            showTitles: true,
                                            getTitlesWidget: (value, meta) {
                                              return Text(
                                                value == 0 ? 'Prev' : 'Now',
                                                style: const TextStyle(
                                                  fontFamily: 'Montserrat',
                                                  fontSize: 10,
                                                  color: Colors.grey,
                                                ),
                                              );
                                            },
                                          ),
                                        ),
                                        leftTitles: AxisTitles(
                                          sideTitles: SideTitles(
                                            showTitles: false,
                                          ),
                                        ),
                                        topTitles: AxisTitles(
                                          sideTitles: SideTitles(
                                            showTitles: false,
                                          ),
                                        ),
                                        rightTitles: AxisTitles(
                                          sideTitles: SideTitles(
                                            showTitles: false,
                                          ),
                                        ),
                                      ),
                                      borderData: FlBorderData(show: false),
                                      barGroups: _generateChartData(),
                                      gridData: FlGridData(show: false),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }
}