import 'package:flutter/material.dart';
import 'dart:ui'; // Import for ImageFilter

class EmergencyCall extends StatelessWidget {
  final VoidCallback? onClose;
  const EmergencyCall({super.key, this.onClose});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal.shade50,
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('lib/assets/images/background.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 8.0, sigmaY: 8.0),
          child: SafeArea(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "EMERGENCY CALL",
                      style: TextStyle(
                        fontFamily: 'Montserrat',
                        fontSize: 26,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF3E4562),
                      ),
                    ),
                    SizedBox(height: 100),
                    CircleAvatar(
                      radius: 65,
                      backgroundColor: Colors.teal.shade400,
                      child: Icon(
                        Icons.person,
                        size: 80,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 80),
                    Text(
                      "Users may be in danger\nafter falling!",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontFamily: 'Montserrat',
                        fontSize: 22,
                        color: Colors.black54,
                      ),
                    ),
                    SizedBox(height: 100),
                    ElevatedButton(
                      onPressed: () {
                        if (onClose != null) onClose!();
                        Navigator.pop(context);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.teal,
                        shape: StadiumBorder(),
                        padding: EdgeInsets.symmetric(
                          horizontal: 42,
                          vertical: 12,
                        ),
                      ),
                      child: Text(
                        "CLOSE",
                        style: TextStyle(
                          fontFamily: 'Montserrat',
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}