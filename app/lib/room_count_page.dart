import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';

// Hard-coded for now; later this could come from a room picker.
const String roomUid = '2OYdpmvifh2pjNl0WQu9';

class RoomCountPage extends StatefulWidget {
  const RoomCountPage({super.key});

  @override
  State<RoomCountPage> createState() => _RoomCountPageState();
}

class _RoomCountPageState extends State<RoomCountPage> {
  // Created once and kept in State. If it were created inside build(), every rebuild
  // would open a brand-new Firestore listener.
  final Stream<DocumentSnapshot<Map<String, dynamic>>> _roomStream =
      FirebaseFirestore.instance.collection('rooms').doc(roomUid).snapshots();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Door Sensor')),
      body: Center(
        child: StreamBuilder<DocumentSnapshot<Map<String, dynamic>>>(
          stream: _roomStream,
          builder: (context, snapshot) {
            if (snapshot.hasError) {
              return Text('Error: ${snapshot.error}');
            }
            if (!snapshot.hasData) {
              return const CircularProgressIndicator();
            }

            final doc = snapshot.data!;
            // Like the API's 404: a missing document is not an error, just exists == false.
            if (!doc.exists) {
              return const Text('Room not found');
            }

            final count = doc.data()?['count'] ?? 0;
            return Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Room $roomUid'),
                const SizedBox(height: 16),
                Text('$count', style: Theme.of(context).textTheme.displayLarge),
              ],
            );
          },
        ),
      ),
    );
  }
}
