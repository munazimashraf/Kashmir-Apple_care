class Diagnosis {
  const Diagnosis({
    required this.id,
    required this.disease,
    required this.confidence,
    required this.growthStage,
    required this.createdAt,
    this.recommendations = const [],
    this.guardrails = const [],
    this.synced = false,
    this.imagePath,
  });

  final String id;
  final String disease;
  final double confidence;
  final String growthStage;
  final DateTime createdAt;
  final List<Map<String, String>> recommendations;
  final List<String> guardrails;
  final bool synced;
  final String? imagePath;

  Map<String, Object?> toMap() => {
        'id': id,
        'disease': disease,
        'confidence': confidence,
        'growth_stage': growthStage,
        'created_at': createdAt.toIso8601String(),
        'recommendations': recommendations.toString(),
        'guardrails': guardrails.join('\n'),
        'synced': synced ? 1 : 0,
        'image_path': imagePath,
      };

  factory Diagnosis.fromMap(Map<String, Object?> map) => Diagnosis(
        id: map['id']! as String,
        disease: map['disease']! as String,
        confidence: (map['confidence']! as num).toDouble(),
        growthStage: map['growth_stage']! as String,
        createdAt: DateTime.parse(map['created_at']! as String),
        guardrails: (map['guardrails'] as String? ?? '').split('\n').where((e) => e.isNotEmpty).toList(),
        synced: (map['synced'] as int? ?? 0) == 1,
        imagePath: map['image_path'] as String?,
      );
}
