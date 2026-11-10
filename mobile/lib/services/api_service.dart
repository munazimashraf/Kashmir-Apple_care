import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../models/diagnosis.dart';
import 'local_store.dart';

class ApiService {
  ApiService(this.baseUrl, this.store);
  final String baseUrl;
  final LocalStore store;
  String? token;

  Future<void> sync() async {
    if (token == null) return;
    for (final row in await store.pendingRows()) {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/v1/diagnoses/upload'));
      request.headers['Authorization'] = 'Bearer $token';
      request.fields['growth_stage'] = row['growth_stage']! as String;
      request.fields['rain_within_12_hours'] = 'false';
      final imagePath = row['image_path'] as String?;
      if (imagePath == null || !File(imagePath).existsSync()) continue;
      request.files.add(await http.MultipartFile.fromPath('file', imagePath));
      final response = await request.send();
      if (response.statusCode >= 200 && response.statusCode < 300) await store.markSynced(row['id']! as String);
    }
  }
}
