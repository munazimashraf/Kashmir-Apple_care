import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

import '../models/diagnosis.dart';

class LocalStore {
  Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    final directory = await getApplicationDocumentsDirectory();
    _database = await openDatabase(
      join(directory.path, 'applecare.sqlite'),
      version: 1,
      onCreate: (db, _) async {
        await db.execute('CREATE TABLE diagnoses (id TEXT PRIMARY KEY, disease TEXT NOT NULL, confidence REAL NOT NULL, growth_stage TEXT NOT NULL, created_at TEXT NOT NULL, recommendations TEXT, guardrails TEXT, image_path TEXT, synced INTEGER NOT NULL DEFAULT 0)');
        await db.execute('CREATE INDEX diagnoses_created_at ON diagnoses(created_at)');
      },
    );
    return _database!;
  }

  Future<void> saveDiagnosis(Diagnosis diagnosis) async {
    final db = await database;
    await db.insert('diagnoses', diagnosis.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Diagnosis>> recentDiagnoses() async {
    final db = await database;
    final rows = await db.query('diagnoses', orderBy: 'created_at DESC');
    return rows.map(Diagnosis.fromMap).toList();
  }

  Future<List<Map<String, Object?>>> pendingRows() async {
    final db = await database;
    return db.query('diagnoses', where: 'synced = 0', orderBy: 'created_at ASC');
  }

  Future<void> markSynced(String id) async {
    final db = await database;
    await db.update('diagnoses', {'synced': 1}, where: 'id = ?', whereArgs: [id]);
  }
}
