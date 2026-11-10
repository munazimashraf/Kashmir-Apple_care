import 'package:flutter/material.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});
  @override
  Widget build(BuildContext context) => const ListView(children: [ListTile(title: Text('Language'), subtitle: Text('English / Urdu')), ListTile(title: Text('Offline model'), subtitle: Text('VGG19 TFLite'))]);
}
