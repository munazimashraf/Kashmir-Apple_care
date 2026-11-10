import 'package:flutter/material.dart';

class ScannerScreen extends StatelessWidget {
  const ScannerScreen({super.key, required this.onScan});
  final VoidCallback onScan;
  @override
  Widget build(BuildContext context) => Center(child: FilledButton.icon(onPressed: onScan, icon: const Icon(Icons.camera_alt), label: const Text('Scan leaf')));
}
