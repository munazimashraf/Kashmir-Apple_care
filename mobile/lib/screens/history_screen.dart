import 'package:flutter/material.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key, required this.items});
  final List<String> items;
  @override
  Widget build(BuildContext context) => ListView(children: items.map((item) => ListTile(title: Text(item))).toList());
}
