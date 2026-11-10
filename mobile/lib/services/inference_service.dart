import 'dart:convert';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/services.dart';
import 'package:image/image.dart' as image_lib;
import 'package:tflite_flutter/tflite_flutter.dart';

class InferenceResult {
  const InferenceResult(this.disease, this.confidence);
  final String disease;
  final double confidence;
}

class InferenceService {
  Interpreter? _interpreter;
  List<String> _classes = [];

  Future<void> load() async {
    _interpreter = await Interpreter.fromAsset('assets/models/applecare_vgg19.tflite');
    _classes = List<String>.from(jsonDecode(await rootBundle.loadString('assets/models/classes.json')));
  }

  Future<InferenceResult> classify(Uint8List bytes) async {
    final interpreter = _interpreter;
    if (interpreter == null) throw StateError('Inference model is not loaded');
    final decoded = image_lib.decodeImage(bytes);
    if (decoded == null) throw FormatException('Image could not be decoded');
    final resized = image_lib.copyResize(decoded, width: 224, height: 224);
    final input = List.generate(1, (_) => List.generate(224, (y) => List.generate(224, (x) => List.generate(3, (channel) {
          final pixel = resized.getPixel(x, y);
          final value = channel == 0 ? pixel.r : channel == 1 ? pixel.g : pixel.b;
          return (value / 255.0 - [0.485, 0.456, 0.406][channel]) / [0.229, 0.224, 0.225][channel];
        }))));
    final output = [List<double>.filled(_classes.length, 0)];
    interpreter.run(input, output);
    final logits = output.first;
    final maximum = logits.reduce(math.max);
    final exponentials = logits.map((value) => math.exp(value - maximum)).toList();
    final total = exponentials.reduce((a, b) => a + b);
    final probabilities = exponentials.map((value) => value / total).toList();
    final best = probabilities.indexWhere((value) => value == probabilities.reduce(math.max));
    return InferenceResult(_classes[best], probabilities[best]);
  }

  void close() => _interpreter?.close();
}
