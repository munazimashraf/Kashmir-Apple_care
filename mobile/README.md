# Flutter client

This client is intentionally artifact-driven. Before running it, train and
review the model from `../ml/train_apple_model.py`, then copy:

```text
artifacts/applecare/applecare_mobilenetv3.tflite -> assets/models/
artifacts/applecare/classes.json                   -> assets/models/
```

The scanner uses TFLite locally and writes each diagnosis to SQLite before
attempting cloud sync. Set the API URL for a physical device or emulator:

```bash
flutter run --dart-define=API_BASE_URL=https://api.example.com
```

Add these platform permissions in the generated Flutter host projects:

- Android: `CAMERA`, `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`, and
  `INTERNET`.
- iOS: `NSCameraUsageDescription`,
  `NSLocationWhenInUseUsageDescription`, and speech/audio usage descriptions.

The current workspace does not include the Flutter SDK, so `flutter analyze`
and native builds must be run on a Flutter-enabled development machine.
