import 'package:blind_sunglasses/notificationscreen.dart';
import 'package:blind_sunglasses/settingsscreen.dart';
import 'package:flutter/material.dart';
import 'package:blind_sunglasses/homescreen.dart';

class Navigation extends StatefulWidget {
  const Navigation({Key? key}) : super(key: key);

  @override
  State<Navigation> createState() => _NavigationState();
}

class _NavigationState extends State<Navigation> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const HomeScreen(),
    const NotificationScreen(),
    const SettingsScreen()
  ];

  final List<Color> _selectedColors = [
    const Color(0xFF368C8B), // Home - Teal
    const Color(0xFFFF6B6B), // Notifications - Red
    const Color(0xFF4ECDC4), // Settings - Light Blue
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          selectedItemColor: _selectedColors[_currentIndex],
          unselectedItemColor: Colors.grey,
          backgroundColor: Colors.transparent,
          elevation: 0,
          items: [
            BottomNavigationBarItem(
              icon: Icon(
                Icons.home,
                color: _currentIndex == 0 ? _selectedColors[0] : Colors.grey,
              ),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(
                Icons.notifications,
                color: _currentIndex == 1 ? _selectedColors[1] : Colors.grey,
              ),
              label: 'Notifications',
            ),
            BottomNavigationBarItem(
              icon: Icon(
                Icons.settings,
                color: _currentIndex == 2 ? _selectedColors[2] : Colors.grey,
              ),
              label: 'Settings',
            ),
          ],
        ),
      ),
    );
  }
}