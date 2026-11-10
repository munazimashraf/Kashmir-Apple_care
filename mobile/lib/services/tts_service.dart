import 'package:flutter_tts/flutter_tts.dart';

class TtsService {
  final FlutterTts _tts = FlutterTts();

  Future<void> speak(String text, {required String language}) async {
    await _tts.setLanguage(language);
    await _tts.setSpeechRate(0.42);
    await _tts.speak(text);
  }

  Future<void> stop() => _tts.stop();
}
