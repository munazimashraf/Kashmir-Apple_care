"""SKUAST-Kashmir Apple Disease Advisory & Integrated Pest Management (IPM) Engine.

Formulates stage-specific chemical recommendations, dosages, cultural sanitation
practices, and environmental/pollinator guardrails aligned with official SKUAST-K
(Sher-e-Kashmir University of Agricultural Sciences & Technology of Kashmir)
annual spray schedules for Kashmir valley apple orchards.
"""
from __future__ import annotations

from typing import Any, Dict, List


SKUAST_ADVISORIES: Dict[str, Dict[str, Any]] = {
    "apple_scab": {
        "common_name": "Apple Scab",
        "scientific_name": "Venturia inaequalis",
        "kashmiri_name": "Tchoke",
        "description": "Fungal infection causing velvety olive-green to black lesions on leaves and cracked corky scab lesions on fruit.",
        "stages": {
            "Green Tip": [
                {"product": "Mancozeb 75 WP (Indofil M-45)", "dosage": "300g / 100L water", "type": "Protective contact fungicide"},
                {"product": "Propineb 70 WP (Antracol)", "dosage": "300g / 100L water", "type": "Protective contact fungicide"},
                {"product": "Captan 50 WP", "dosage": "300g / 100L water", "type": "Multi-site protective fungicide"},
            ],
            "Pink Bud": [
                {"product": "Difenoconazole 25 EC (Score)", "dosage": "30ml / 100L water", "type": "Systemic triazole fungicide"},
                {"product": "Flusilazole 40 EC (Cursor)", "dosage": "20ml / 100L water", "type": "Systemic sterol inhibitor"},
                {"product": "Dodine 65 WP (Syllit)", "dosage": "60g / 100L water", "type": "Curative and translaminar fungicide"},
            ],
            "Full Bloom": [
                {"product": "NO-SPRAY: Chemical fungicides discouraged during Full Bloom", "dosage": "N/A", "type": "Honeybee protection period"},
            ],
            "Petal Fall": [
                {"product": "Dodine 65 WP", "dosage": "60g / 100L water", "type": "Curative and protective fungicide"},
                {"product": "Zineb 68% + Hexaconazole 4% WP (Avatar)", "dosage": "100g / 100L water", "type": "Combination fungicide"},
                {"product": "Trifloxystrobin + Tebuconazole (Nativo 75 WG)", "dosage": "40g / 100L water", "type": "Broad-spectrum systemic"},
            ],
            "Fruit Growth": [
                {"product": "Kresoxim-methyl 44.3 SC (Ergon)", "dosage": "50ml / 100L water", "type": "Strobilurin class fungicide"},
                {"product": "Metiram 55% + Pyraclostrobin 5% WG (Cabrio Top)", "dosage": "100g / 100L water", "type": "Dual protective & translaminar"},
                {"product": "Mancozeb 75 WP", "dosage": "300g / 100L water", "type": "Protective contact fungicide"},
            ],
        },
        "cultural_measures": [
            "Prune inner canopy branches to increase sun penetration and promote rapid leaf drying.",
            "Collect and destroy or deep-bury fallen autumn leaves to eradicate primary overwintering perithecia.",
            "Apply a 5% agricultural Urea spray on orchard leaf litter immediately post-harvest to accelerate decomposition.",
        ],
    },
    "alternaria_leaf_blotch": {
        "common_name": "Alternaria Leaf Blotch",
        "scientific_name": "Alternaria mali",
        "kashmiri_name": "Dag / Blotch",
        "description": "Circular brownish necrotic spots surrounded by reddish-purple halos, coalescing under humid summer heat and causing premature defoliation.",
        "stages": {
            "Green Tip": [
                {"product": "Mancozeb 75 WP", "dosage": "300g / 100L water", "type": "Protective contact fungicide"},
                {"product": "Propineb 70 WP", "dosage": "300g / 100L water", "type": "Protective contact fungicide"},
            ],
            "Pink Bud": [
                {"product": "Difenoconazole 25 EC", "dosage": "30ml / 100L water", "type": "Systemic triazole fungicide"},
            ],
            "Full Bloom": [
                {"product": "NO-SPRAY: Protect active pollinating bees", "dosage": "N/A", "type": "Pollinator shield"},
            ],
            "Petal Fall": [
                {"product": "Zineb 68% + Hexaconazole 4% WP", "dosage": "125g / 100L water", "type": "Combination protective & systemic"},
                {"product": "Dodine 65 WP", "dosage": "60g / 100L water", "type": "Translaminar curative fungicide"},
            ],
            "Fruit Growth": [
                {"product": "Metiram 55% + Pyraclostrobin 5% WG (Cabrio Top)", "dosage": "100g / 100L water", "type": "Translaminar protective"},
                {"product": "Difenoconazole 25 EC", "dosage": "30ml / 100L water", "type": "Systemic fungicide"},
                {"product": "Zineb 68% + Hexaconazole 4% WP", "dosage": "125g / 100L water", "type": "Combination fungicide"},
            ],
        },
        "cultural_measures": [
            "Maintain adequate spacing and summer prune water sprouts to enhance canopy aeration.",
            "Avoid excessive nitrogenous fertilization which promotes succulent leaf susceptibility.",
            "Ensure effective drainage in heavy soil blocks to mitigate humidity build-up in the orchard floor.",
        ],
    },
    "powdery_mildew": {
        "common_name": "Powdery Mildew",
        "scientific_name": "Podosphaera leucotricha",
        "kashmiri_name": "Phophund / Sufaid Dag",
        "description": "White powdery fungal mycelial growth on young leaves, shoots, and terminal buds, leading to leaf curling, stunting, and russeting.",
        "stages": {
            "Green Tip": [
                {"product": "Wettable Sulphur 80 WP", "dosage": "250g / 100L water", "type": "Inorganic protective fungicide (avoid T > 30°C)"},
            ],
            "Pink Bud": [
                {"product": "Penconazole 10 EC (Topas)", "dosage": "50ml / 100L water", "type": "Systemic triazole fungicide"},
                {"product": "Hexaconazole 5 EC (Contaf)", "dosage": "50ml / 100L water", "type": "Systemic fungicide"},
            ],
            "Full Bloom": [
                {"product": "NO-SPRAY during Full Bloom", "dosage": "N/A", "type": "Pollinator protection"},
            ],
            "Petal Fall": [
                {"product": "Penconazole 10 EC", "dosage": "50ml / 100L water", "type": "Systemic ergosterol biosynthesis inhibitor"},
                {"product": "Flusilazole 40 EC", "dosage": "20ml / 100L water", "type": "Systemic curative fungicide"},
            ],
            "Fruit Growth": [
                {"product": "Penconazole 10 EC", "dosage": "50ml / 100L water", "type": "Systemic fungicide"},
                {"product": "Myclobutanil 10 WP (Systhane)", "dosage": "50g / 100L water", "type": "Systemic protective & curative"},
            ],
        },
        "cultural_measures": [
            "Mechanically clip infected 'silver terminals' and white powdery shoots early morning into a collection bag and burn them.",
            "Disinfect pruning secateurs in 5% sodium hypochlorite or methylated spirit between trees.",
        ],
    },
    "black_rot": {
        "common_name": "Black Rot (Frogeye Leaf Spot & Canker)",
        "scientific_name": "Botryosphaeria obtusa",
        "kashmiri_name": "Siyahi Dag / Sarun",
        "description": "Circular purple spots enlarging into frogeye leaf spots with tan centers and dark concentric rings; cankers on limbs and black mummified fruit.",
        "stages": {
            "Green Tip": [
                {"product": "Mancozeb 75 WP", "dosage": "300g / 100L water", "type": "Protective contact fungicide"},
                {"product": "Copper Oxychloride 50 WP", "dosage": "300g / 100L water", "type": "Copper bactericide / fungicide"},
            ],
            "Pink Bud": [
                {"product": "Thiophanate-methyl 70 WP (Roko)", "dosage": "100g / 100L water", "type": "Systemic broad-spectrum"},
                {"product": "Mancozeb 75 WP", "dosage": "300g / 100L water", "type": "Protective contact"},
            ],
            "Full Bloom": [
                {"product": "NO-SPRAY during Full Bloom", "dosage": "N/A", "type": "Bee safety"},
            ],
            "Petal Fall": [
                {"product": "Captan 50 WP", "dosage": "300g / 100L water", "type": "Protective multi-site"},
                {"product": "Thiophanate-methyl 70 WP", "dosage": "100g / 100L water", "type": "Systemic curative"},
            ],
            "Fruit Growth": [
                {"product": "Mancozeb 75 WP", "dosage": "300g / 100L water", "type": "Protective contact fungicide"},
                {"product": "Difenoconazole 25 EC", "dosage": "30ml / 100L water", "type": "Systemic triazole"},
            ],
        },
        "cultural_measures": [
            "Prune out dead branches, cankered limbs, and fire blight strikes 15cm into healthy green wood.",
            "Apply Chaubattia paste (Copper carbonate 1: Red lead 1: Linseed oil 1.25) or Copper paste on all pruning wounds.",
            "Remove and burn mummified apples hanging from trees or lying on the ground.",
        ],
    },
    "cedar_apple_rust": {
        "common_name": "Cedar Apple Rust",
        "scientific_name": "Gymnosporangium juniperi-virginianae",
        "kashmiri_name": "Zang Dag / Rust",
        "description": "Bright orange-yellow spots on upper leaf surface producing sticky pycnia and orange tubular aecia on the leaf underside.",
        "stages": {
            "Green Tip": [
                {"product": "Mancozeb 75 WP", "dosage": "300g / 100L water", "type": "Protective contact fungicide"},
            ],
            "Pink Bud": [
                {"product": "Myclobutanil 10 WP (Systhane)", "dosage": "50g / 100L water", "type": "Systemic triazole fungicide"},
                {"product": "Difenoconazole 25 EC", "dosage": "30ml / 100L water", "type": "Systemic fungicide"},
            ],
            "Full Bloom": [
                {"product": "NO-SPRAY during Full Bloom", "dosage": "N/A", "type": "Pollinator shield"},
            ],
            "Petal Fall": [
                {"product": "Mancozeb 75 WP", "dosage": "300g / 100L water", "type": "Protective contact"},
                {"product": "Trifloxystrobin + Tebuconazole (Nativo)", "dosage": "40g / 100L water", "type": "Systemic combination"},
            ],
            "Fruit Growth": [
                {"product": "Difenoconazole 25 EC", "dosage": "30ml / 100L water", "type": "Systemic triazole"},
                {"product": "Mancozeb 75 WP", "dosage": "300g / 100L water", "type": "Protective contact"},
            ],
        },
        "cultural_measures": [
            "Inspect and remove cedar/juniper galls located within 500 meters of the orchard perimeter.",
            "Prune apple trees to encourage rapid drying of foliage during springtime infection periods.",
        ],
    },
    "healthy": {
        "common_name": "Healthy Apple Leaf",
        "scientific_name": "Malus domestica (Clean foliage)",
        "kashmiri_name": "Sehatmand Paan",
        "description": "Clean, vigorous green leaf tissue with no observable pathogenic lesions, necrosis, or fungal mycelium.",
        "stages": {
            "all": [
                {"product": "No chemical pesticide spray required", "dosage": "N/A", "type": "Foliage is clean and uninfected"},
            ],
        },
        "cultural_measures": [
            "Maintain weekly scouting: inspect 10 leaves on 10 random trees per orchard block.",
            "Ensure balanced fertilization: soil test every 2 years to calibrate N, P, K, and micro-nutrients.",
            "Maintain clean floor management, regular mowing, and weed-free strips along the tree row.",
        ],
    },
}


def build_advisory(disease: str, growth_stage: str, rain_within_12_hours: bool) -> Dict[str, Any]:
    """Generates the comprehensive SKUAST-K Kashmir disease advisory."""
    info = SKUAST_ADVISORIES.get(disease)
    
    if not info:
        # Fallback / uncertain
        return {
            "disease_common": "Uncertain / Unconfirmed Symptom",
            "disease_scientific": "Requires Expert Verification",
            "kashmiri_name": "Tashkhees Ghair Wazih",
            "recommendations": [],
            "cultural_measures": ["Consult a local SKUAST-K horticulture development officer (HDO) before chemical spraying."],
            "guardrails": ["Low confidence: retake a clear, well-focused close-up photo in bright daylight."],
        }

    # Fetch recommendations for the stage
    stages_dict = info.get("stages", {})
    if growth_stage in stages_dict:
        products = stages_dict[growth_stage]
    elif "all" in stages_dict:
        products = stages_dict["all"]
    elif "Fruit Growth" in stages_dict:
        products = stages_dict["Fruit Growth"]
    else:
        products = []

    # Filter out empty or no-spray placeholder if needed
    guardrails: List[str] = []
    
    # Weather safety
    if rain_within_12_hours:
        guardrails.append("⚠️ POSTPONE SPRAYING: Rain is forecast within 12 hours. Chemical wash-off will cause financial loss and inadequate control.")
    else:
        guardrails.append("✅ DRY WINDOW: No rain forecast in the next 12 hours. Spray only on dry leaves when ambient temperature is below 28°C.")

    # Growth stage & pollinator safety
    if growth_stage == "Full Bloom":
        guardrails.append("🐝 POLLINATOR SHIELD: Full Bloom detected. Strictly DO NOT spray chemical insecticides or acaricides to protect pollinating honeybees.")
    else:
        guardrails.append("🐝 BEE-SAFE APPLICATION: Spray only after dusk or early morning; avoid spraying when ground weeds are flowering.")

    # Calcium booster for fruit development
    if growth_stage in {"Fruit Growth", "Fruit Development"}:
        guardrails.append("🧊 STORAGE & QUALITY BOOSTER: Foliar spray of Calcium Chloride 3–4g / Litre of water (or Calcium Nitrate 4g/L) helps prevent Bitter Pit and physiological breakdown in cold storage.")

    # Specific disease tips
    if disease == "powdery_mildew":
        guardrails.append("✂️ TERMINAL PRUNING: Mechanically prune out and bag white powdery 'silver terminals' early morning before spore dispersal.")
    elif disease == "apple_scab":
        guardrails.append("🔬 FUNGICIDE ROTATION: Alternate contact protectants (Mancozeb/Propineb) with systemic fungicides (Score/Dodine) to prevent fungal resistance.")
    elif disease == "healthy":
        guardrails.append("🌿 CLEAN ORCHARD: Foliage is healthy. Avoid unneeded chemical applications to preserve natural predatory mites and beneficial insects.")

    return {
        "disease_common": info.get("common_name", disease.replace("_", " ").title()),
        "disease_scientific": info.get("scientific_name", ""),
        "kashmiri_name": info.get("kashmiri_name", ""),
        "description": info.get("description", ""),
        "growth_stage": growth_stage,
        "recommendations": products,
        "cultural_measures": info.get("cultural_measures", []),
        "guardrails": guardrails,
    }
