import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'models/diagnosis.dart';
import 'services/inference_service.dart';
import 'services/local_store.dart';
import 'services/tts_service.dart';
import 'services/api_service.dart';
import 'screens/history_screen.dart';
import 'screens/scanner_screen.dart';
import 'screens/settings_screen.dart';

void main() => runApp(const AppleCareApp());

class AppleCareApp extends StatelessWidget {
  const AppleCareApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'AppleCare Kashmir',
        theme: ThemeData(colorSchemeSeed: const Color(0xff047857), useMaterial3: true),
        home: const HomeScreen(),
      );
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _store = LocalStore();
  final _inference = InferenceService();
  final _tts = TtsService();
  late final ApiService _api;
  late final StreamSubscription<List<ConnectivityResult>> _connectivitySubscription;
  List<Diagnosis> _history = [];
  String _stage = 'Green Tip';
  bool _loading = true;
  String _location = 'Location not set';
  int _tab = 0;

  @override
  void initState() {
    super.initState();
    _api = ApiService(const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000'), _store);
    _connectivitySubscription = Connectivity().onConnectivityChanged.listen((_) => _api.sync());
    _initialize();
  }

  @override
  void dispose() {
    _connectivitySubscription.cancel();
    _inference.close();
    super.dispose();
  }

  Future<void> _initialize() async {
    try {
      await _inference.load();
    } finally {
      _history = await _store.recentDiagnoses();
      await _api.sync();
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _scan() async {
    final file = await ImagePicker().pickImage(source: ImageSource.camera, imageQuality: 90);
    if (file == null) return;
    final bytes = await file.readAsBytes();
    final result = await _inference.classify(bytes);
    final diagnosis = Diagnosis(id: DateTime.now().microsecondsSinceEpoch.toString(), disease: result.disease, confidence: result.confidence, growthStage: _stage, createdAt: DateTime.now(), recommendations: const [], imagePath: file.path);
    await _store.saveDiagnosis(diagnosis);
    if (mounted) setState(() => _history = [diagnosis, ..._history]);
    await _tts.speak('${result.disease} detected. Follow the spray advisory and postpone spraying if rain is forecast.', language: 'en-US');
  }

  Future<void> _locate() async {
    if (!await Geolocator.isLocationServiceEnabled()) return;
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied || permission == LocationPermission.deniedForever) return;
    final position = await Geolocator.getCurrentPosition();
    if (mounted) setState(() => _location = '${position.latitude.toStringAsFixed(4)}, ${position.longitude.toStringAsFixed(4)}');
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    final content = switch (_tab) {
      1 => ScannerScreen(onScan: _scan),
      2 => HistoryScreen(items: _history.map((item) => '${item.disease} · ${(item.confidence * 100).toStringAsFixed(1)}%').toList()),
      3 => const SettingsScreen(),
      _ => _dashboard(context),
    };
    return Scaffold(
      appBar: AppBar(title: const Text('AppleCare Kashmir'), actions: [IconButton(onPressed: _locate, icon: const Icon(Icons.my_location))]),
      body: content,
      bottomNavigationBar: NavigationBar(selectedIndex: _tab, onDestinationSelected: (index) => setState(() => _tab = index), destinations: const [
        NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
        NavigationDestination(icon: Icon(Icons.camera_alt_outlined), selectedIcon: Icon(Icons.camera_alt), label: 'Scanner'),
        NavigationDestination(icon: Icon(Icons.history), label: 'History'),
        NavigationDestination(icon: Icon(Icons.settings_outlined), selectedIcon: Icon(Icons.settings), label: 'Settings'),
      ]),
    );
  }

  Widget _dashboard(BuildContext context) => ListView(padding: const EdgeInsets.all(18), children: [
        Text('Field health dashboard', style: Theme.of(context).textTheme.headlineSmall),
        Text('GPS: $_location'),
        const SizedBox(height: 18),
        DropdownButtonFormField<String>(value: _stage, decoration: const InputDecoration(labelText: 'Orchard growth stage'), items: ['Green Tip', 'Pink Bud', 'Full Bloom', 'Petal Fall', 'Fruit Development'].map((value) => DropdownMenuItem(value: value, child: Text(value))).toList(), onChanged: (value) => setState(() => _stage = value!)),
        const SizedBox(height: 18),
        FilledButton.icon(onPressed: _scan, icon: const Icon(Icons.camera_alt), label: const Text('Scan apple leaf offline')),
        const SizedBox(height: 18),
        Text('Recent diagnoses', style: Theme.of(context).textTheme.titleLarge),
        ..._history.map((item) => Card(child: ListTile(title: Text(item.disease), subtitle: Text('${(item.confidence * 100).toStringAsFixed(1)}% · ${item.growthStage}'), trailing: IconButton(onPressed: () => _tts.speak('${item.disease} detected', language: 'ur-PK'), icon: const Icon(Icons.volume_up)))),
      ]);
}
