import 'package:zego_express_engine/zego_express_engine.dart';
import 'package:flutter/material.dart';


class EmergencyCall extends StatelessWidget {
  const EmergencyCall({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal.shade50,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text("EMERGENCY CALL", style: TextStyle(
                  fontFamily: 'Montserrat',
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF3E4562))),
              SizedBox(height: 100),
              CircleAvatar(radius: 65, backgroundColor: Colors.teal.shade400,
                  child: Icon(
                      Icons.person,
                      size: 80,
                      color: Colors.white)),
              SizedBox(height: 80),
              Text("Users may be in danger\nafter falling!",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontFamily: 'Montserrat',
                      fontSize: 22,
                      color: Colors.black54)),
              SizedBox(height: 100),

              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  shape: StadiumBorder(),
                  padding: EdgeInsets.symmetric(horizontal: 42, vertical: 12),
                ),
                child: Text("CLOSE",
                    style: TextStyle(
                        fontFamily: 'Montserrat',
                        color: Colors.white,
                        fontSize: 22,
                        fontWeight: FontWeight.bold),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
