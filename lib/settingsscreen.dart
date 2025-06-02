import 'dart:io';

import 'package:flutter/material.dart';
import 'package:blind_sunglasses/loginscreen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:blind_sunglasses/services/notification_service.dart';


class SettingsScreen extends StatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool notificationEnabled = true;
  String selectedSound = 'sound2';
  List<String> soundOptions = ['sound1', 'sound2', 'sound3'];
  Map<String, String> soundDisplayNames = {
    'sound1': 'Sound 1',
    'sound2': 'Sound 2',
    'sound3': 'Sound 3',
  };

  final LayerLink _layerLink = LayerLink();
  final GlobalKey _soundRowKey = GlobalKey();
  OverlayEntry? _dropdownOverlay;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      notificationEnabled = prefs.getBool('notificationEnabled') ?? true;
      selectedSound = prefs.getString('selectedSound') ?? 'sound2';
    });
  }

  Future<void> _saveNotificationSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('notificationEnabled', notificationEnabled);
  }

  Future<void> _saveSoundSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('selectedSound', selectedSound);
    await NotificationService.instance.updateSoundSetting(selectedSound);
  }

  void _updateNotification(bool value) {
    setState(() {
      notificationEnabled = value;
    });
    _saveNotificationSettings();
  }

  void _updateSound(String soundKey) async {
    if (selectedSound == soundKey) {
      _hideDropdownOverlay(); // Không đổi gì, không cần hỏi
      return;
    }

    // Lưu tạm
    setState(() {
      selectedSound = soundKey;
    });
    await _saveSoundSettings();

    _hideDropdownOverlay();

    // Hiện dialog yêu cầu restart
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        title: const Text("Restart Required"),
        content: const Text("The sound has been changed. Please restart the app to apply the new notification sound."),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text("Cancel"),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();

              await Future.delayed(Duration(milliseconds: 300));
              await Process.run(
                'am',
                ['start', '-n', 'com.example.blind_sunglasses/.MainActivity'],
              );
              exit(0);
            },
            child: const Text("Restart now"),
          ),
        ],
      ),
    );

  }


  @override
  void dispose() {
    _hideDropdownOverlay();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFFE3F2FD),
              Color(0xFFF8F9FA),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Expanded(
                flex: 2,
                child: Center(
                  child: Container(
                    width: 140,
                    height: 140,
                    decoration: BoxDecoration(
                      color: Color(0xFF329C95),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.person,
                      color: Colors.white,
                      size: 90,
                    ),
                  ),
                ),
              ),
              Expanded(
                flex: 3,
                child: Container(
                  margin: EdgeInsets.symmetric(horizontal: 20),
                  padding: EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 10,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Notification',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w500,
                              color: Colors.black87,
                            ),
                          ),
                          Switch(
                            value: notificationEnabled,
                            onChanged: _updateNotification,
                            activeColor: Color(0xFF329C95),
                          ),
                        ],
                      ),
                      Divider(color: Colors.grey[300]),
                      CompositedTransformTarget(
                        link: _layerLink,
                        child: GestureDetector(
                          key: _soundRowKey,
                          onTap: () {
                            if (_dropdownOverlay == null) {
                              _showDropdownOverlay(context);
                            } else {
                              _hideDropdownOverlay();
                            }
                          },
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Notification sound',
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.w500,
                                  color: Colors.black87,
                                ),
                              ),
                              Row(
                                children: [
                                  Text(
                                    soundDisplayNames[selectedSound] ?? selectedSound,
                                    style: TextStyle(
                                      fontSize: 18,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Icon(
                                    _dropdownOverlay == null
                                        ? Icons.keyboard_arrow_down
                                        : Icons.keyboard_arrow_up,
                                    color: Colors.grey[600],
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                      Spacer(),
                      Container(
                        width: double.infinity,
                        height: 50,
                        child: ElevatedButton(
                          onPressed: () {
                            showDialog(
                              context: context,
                              builder: (context) => AlertDialog(
                                title: Text('Sign Out'),
                                content: Text('Are you sure you want to sign out?'),
                                actions: [
                                  TextButton(
                                    onPressed: () => Navigator.pop(context),
                                    child: Text('Cancel'),
                                  ),
                                  TextButton(
                                    onPressed: () {
                                      Navigator.pop(context);
                                      Navigator.of(context).pushAndRemoveUntil(
                                        MaterialPageRoute(builder: (context) => LoginScreen()),
                                            (Route<dynamic> route) => false,
                                      );
                                    },
                                    child: Text('Sign Out'),
                                  ),
                                ],
                              ),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Color(0xFFFF5252),
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(25),
                            ),
                          ),
                          child: Text(
                            'Sign out',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 50),
            ],
          ),
        ),
      ),
    );
  }

  void _showDropdownOverlay(BuildContext context) {
    final overlay = Overlay.of(context);
    final renderBox = _soundRowKey.currentContext?.findRenderObject() as RenderBox?;

    if (renderBox == null) return;

    final offset = renderBox.localToGlobal(Offset.zero);

    _dropdownOverlay = OverlayEntry(
      builder: (context) => Positioned(
        left: offset.dx,
        top: offset.dy + renderBox.size.height + 8,
        width: renderBox.size.width,
        child: Material(
          elevation: 4,
          borderRadius: BorderRadius.circular(8),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey[300]!),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: soundOptions.map((soundKey) {
                return ListTile(
                  title: Text(soundDisplayNames[soundKey] ?? soundKey),
                  trailing: selectedSound == soundKey
                      ? Icon(Icons.check, color: Color(0xFF329C95), size: 18)
                      : null,
                  onTap: () {
                    _updateSound(soundKey);
                    _hideDropdownOverlay();
                  },
                );
              }).toList(),
            ),
          ),
        ),
      ),
    );

    overlay.insert(_dropdownOverlay!);
    setState(() {}); // Trigger rebuild to update arrow icon
  }

  void _hideDropdownOverlay() {
    _dropdownOverlay?.remove();
    _dropdownOverlay = null;
    if (mounted) {
      setState(() {}); // Trigger rebuild to update arrow icon
    }
  }
}