import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';

import 'firebase_options.dart';
import 'room_count_page.dart';

Future<void> main() async {
  // Required before any `await` in main(): plugins talk to native code through
  // Flutter's engine binding, which isn't set up until this is called.
  WidgetsFlutterBinding.ensureInitialized();

  // Must finish before any Firestore call, otherwise you get "No Firebase App '[DEFAULT]'".
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  runApp(const DoorSensorApp());
}

class DoorSensorApp extends StatelessWidget {
  const DoorSensorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Door Sensor',
      theme: ThemeData(colorSchemeSeed: Colors.teal),
      home: const RoomCountPage(),
    );
  }
}
