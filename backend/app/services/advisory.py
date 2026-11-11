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


def build_advisory(
    disease: str,
    growth_stage: str,
    rain_within_12_hours: bool,
    variety: str = "Red Delicious",
    root_type: str = "Seedling (Standard Vigorous)",
) -> Dict[str, Any]:
    """Generates the comprehensive SKUAST-K Kashmir disease advisory."""
    info = SKUAST_ADVISORIES.get(disease)
    
    if not info:
        # Fallback / uncertain
        return {
            "disease_common": "Uncertain / Unconfirmed Symptom",
            "disease_scientific": "Requires Expert Verification",
            "kashmiri_name": "Tashkhees Ghair Wazih",
            "variety": variety,
            "root_type": root_type,
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

    # Variety-specific susceptibility intelligence
    var_lower = (variety or "").lower()
    if "gala" in var_lower or "chief" in var_lower:
        guardrails.append("🍎 VARIETAL SENSITIVITY (Gala / Super Chief): High susceptibility to Powdery Mildew and early-season Fire Blight. Inspect young spur leaves diligently.")
    elif "golden" in var_lower:
        guardrails.append("🍏 VARIETAL SENSITIVITY (Golden Delicious): Highly prone to fruit russeting. Strictly avoid copper sprays and harsh emulsifiable concentrates after Pink Bud.")
    elif "ambri" in var_lower:
        guardrails.append("🌸 INDIGENOUS HERITAGE (Ambri Kashmiri): Prized aromatic Kashmiri apple with delicate thin skin. Prioritize early Scab (Tchoke) prevention and calcium sprays to prevent Bitter Pit.")
    elif "fuji" in var_lower:
        guardrails.append("❄️ VARIETAL SENSITIVITY (Fuji): Prone to Cedar Apple Rust, Alternaria blotch, and late watercore.")
    elif "delicious" in var_lower:
        guardrails.append("🍎 VARIETAL SENSITIVITY (Delicious Group): Highly susceptible to Apple Scab (Tchoke). Maintain continuous protective film before rain events.")

    # Rootstock canopy & spray volume calibration
    root_lower = (root_type or "").lower()
    if "m9" in root_lower or "dwarf" in root_lower:
        guardrails.append("🌿 CANOPY CALIBRATION (M9 High-Density): Dwarf canopy requires low-volume mist spray (350–500 L water/ha). Check drip fertigation and maintain trellis wire tension.")
    elif "mm106" in root_lower:
        guardrails.append("🪴 CANOPY CALIBRATION (MM106 Semi-Dwarf): Intermediate tree canopy requiring ~800–1200 L/ha spray volume. Avoid waterlogged soils to prevent collar rot.")
    elif "seedling" in root_lower or "standard" in root_lower:
        guardrails.append("🌳 CANOPY CALIBRATION (Seedling Vigorous): High canopy volume (1500–2500 L water/ha). Ensure tractor air-blast or gun pressure reaches top central leader branches.")

    return {
        "disease_common": info.get("common_name", disease.replace("_", " ").title()),
        "disease_scientific": info.get("scientific_name", ""),
        "kashmiri_name": info.get("kashmiri_name", ""),
        "description": info.get("description", ""),
        "growth_stage": growth_stage,
        "variety": variety,
        "root_type": root_type,
        "recommendations": products,
        "cultural_measures": info.get("cultural_measures", []),
        "guardrails": guardrails,
    }


# ==============================================================================
# OFFICIAL SKUAST-KASHMIR ANNUAL APPLE SPRAY CALENDAR (8 PHENOLOGICAL STAGES)
# ==============================================================================

SKUAST_ANNUAL_SPRAY_CALENDAR: List[Dict[str, Any]] = [
    {
        "id": "delayed_dormant",
        "stage_number": 1,
        "stage_name": "Delayed Dormant",
        "kashmiri_name": "Khamosh Marhalah (سست مرحلہ)",
        "timing": "Late February – Early March",
        "tree_phenology": "Fruit and leaf buds swell noticeably but green tissue has not yet separated.",
        "target_pests": [
            "San Jose Scale (overwintering nymphs)",
            "European Red Mite (overwintering eggs)",
            "Stem Cankers & Lichens",
        ],
        "products": [
            {
                "product": "Tree Spray Oil (TSO) / Horticulture Mineral Oil (HMO)",
                "common_brands": "Servo Orchard Spray Oil, HP HMO, Mak All Season",
                "dosage_per_100l": "2.0 Liters",
                "dosage_per_1000l": "20.0 Liters",
                "dosage_per_16l": "320 ml",
                "purpose": "Suffocates overwintering scale insects and red mite eggs on bark",
                "type": "Horticultural mineral oil",
            },
            {
                "product": "Copper Oxychloride 50 WP (Blitox)",
                "common_brands": "Blitox 50, Tata Rallcop",
                "dosage_per_100l": "300 grams",
                "dosage_per_1000l": "3.0 kg",
                "dosage_per_16l": "48 grams",
                "purpose": "Bactericidal and fungicidal cover for cankers and pruning wounds",
                "type": "Inorganic copper protectant",
            },
        ],
        "cultural_sanitation": [
            "Prune diseased, broken, dead, and cankered branches prior to spraying.",
            "Apply Chaubattia paste (Copper Carbonate 1 part + Red Lead 1 part + Raw Linseed Oil 1.25 parts) to cut surfaces > 2 cm.",
            "Scrape loose bark sheltering San Jose scale with dull iron scrapers onto ground tarps.",
        ],
        "precautions": [
            "⚠️ Do NOT apply TSO if temperature is below 4°C or freezing frost is expected within 24 hours.",
            "⚠️ Maintain a minimum 21-day gap between oil application and any sulphur-containing fungicide.",
        ],
    },
    {
        "id": "green_tip",
        "stage_number": 2,
        "stage_name": "Green Tip",
        "kashmiri_name": "Sabz Nok (سبز نوک)",
        "timing": "Late March – Early April",
        "tree_phenology": "Terminal and lateral buds break; 2–5 mm green leaf tissue visible at bud tips.",
        "target_pests": [
            "Apple Scab (Venturia inaequalis - Primary ascospore discharge)",
            "Blossom Blight",
        ],
        "products": [
            {
                "product": "Mancozeb 75 WP (Indofil M-45)",
                "common_brands": "Indofil M-45, UPL Dithane M-45",
                "dosage_per_100l": "300 grams",
                "dosage_per_1000l": "3.0 kg",
                "dosage_per_16l": "48 grams",
                "purpose": "Broad-spectrum contact protectant against primary scab ascospores",
                "type": "Dithiocarbamate multi-site contact fungicide",
            },
            {
                "product": "Propineb 70 WP (Antracol)",
                "common_brands": "Bayer Antracol",
                "dosage_per_100l": "300 grams",
                "dosage_per_1000l": "3.0 kg",
                "dosage_per_16l": "48 grams",
                "purpose": "Protective contact fungicide providing supplementary foliar Zinc (Zn)",
                "type": "Propineb contact protectant",
            },
            {
                "product": "Captan 50 WP",
                "common_brands": "Tata Captaf, Dhanuka Captan",
                "dosage_per_100l": "300 grams",
                "dosage_per_1000l": "3.0 kg",
                "dosage_per_16l": "48 grams",
                "purpose": "Protective multi-site contact fungicide",
                "type": "Phthalimide protectant",
            },
            {
                "product": "Dodine 65 WP (Syllit)",
                "common_brands": "Syllit 65 WP",
                "dosage_per_100l": "60 grams",
                "dosage_per_1000l": "600 grams",
                "dosage_per_16l": "10 grams",
                "purpose": "Translaminar and curative scab control if wetness exceeds 12h",
                "type": "Guanidine translaminar fungicide",
            },
        ],
        "cultural_sanitation": [
            "Ensure entire tree canopy is drenched uniformly until run-off.",
            "If autumn 5% Urea was missed, spray orchard floor leaf litter with 5% Urea before bud burst to hasten perithecial decay.",
        ],
        "precautions": [
            "⚠️ Spray immediately before predicted rain spells; once primary ascospores germinate, contact fungicides cannot cure infection.",
        ],
    },
    {
        "id": "pink_bud",
        "stage_number": 3,
        "stage_name": "Pink Bud",
        "kashmiri_name": "Gulabi Kali (گلابی کلی)",
        "timing": "Mid to Late April",
        "tree_phenology": "Flower buds separate from cluster and display distinct bright pink petals before opening.",
        "target_pests": [
            "Apple Scab",
            "Powdery Mildew (Podosphaera leucotricha)",
            "Alternaria Leaf Blotch",
        ],
        "products": [
            {
                "product": "Difenoconazole 25 EC (Score)",
                "common_brands": "Syngenta Score 25 EC",
                "dosage_per_100l": "30 ml",
                "dosage_per_1000l": "300 ml",
                "dosage_per_16l": "5 ml",
                "purpose": "Systemic triazole with 72-96h kick-back curative activity against scab",
                "type": "Systemic DMI triazole fungicide",
            },
            {
                "product": "Flusilazole 40 EC (Cursor)",
                "common_brands": "Cursor 40 EC, Dupont Punch",
                "dosage_per_100l": "20 ml",
                "dosage_per_1000l": "200 ml",
                "dosage_per_16l": "3.5 ml",
                "purpose": "High-potency systemic sterol inhibitor for Scab and Mildew",
                "type": "Systemic triazole fungicide",
            },
            {
                "product": "Hexaconazole 5 EC (Contaf)",
                "common_brands": "Tata Contaf 5 EC",
                "dosage_per_100l": "50 ml",
                "dosage_per_1000l": "500 ml",
                "dosage_per_16l": "8 ml",
                "purpose": "Systemic control of Powdery Mildew and Scab",
                "type": "Systemic triazole fungicide",
            },
            {
                "product": "Zineb 68% + Hexaconazole 4% WP (Avatar)",
                "common_brands": "Indofil Avatar",
                "dosage_per_100l": "100 grams",
                "dosage_per_1000l": "1.0 kg",
                "dosage_per_16l": "16 grams",
                "purpose": "Combination contact + systemic protection",
                "type": "Combination fungicide",
            },
        ],
        "cultural_sanitation": [
            "Cut out white powdery 'silver terminal' shoots infected with powdery mildew and dispose off-site.",
            "Install yellow sticky traps for monitoring sucking pest emergence.",
        ],
        "precautions": [
            "⚠️ Do NOT spray during strong winds (> 14 km/h) to avoid chemical drift into water bodies or neighboring fields.",
        ],
    },
    {
        "id": "full_bloom",
        "stage_number": 4,
        "stage_name": "Full Bloom",
        "kashmiri_name": "Phool Marhalah / Gul (پھول مرحلہ)",
        "timing": "Late April – Early May",
        "tree_phenology": "70–80% of apple blossoms are open; active honeybee cross-pollination taking place.",
        "target_pests": [
            "CRITICAL POLLINATOR PROTECTION PERIOD",
        ],
        "products": [
            {
                "product": "NO-SPRAY: All chemical insecticides and fungicides discouraged",
                "common_brands": "Strict SKUAST-K Honeybee Protection Protocol",
                "dosage_per_100l": "N/A",
                "dosage_per_1000l": "N/A",
                "dosage_per_16l": "N/A",
                "purpose": "Preserves foraging worker honeybees necessary for fruit set and commercial crop yield",
                "type": "Pollinator shield",
            },
        ],
        "cultural_sanitation": [
            "Place 2–3 active Apis mellifera / Apis cerana bee colonies per acre in sunny, wind-protected orchard corners.",
            "Mow ground dandelion weeds prior to bloom so bees focus exclusively on apple blossoms.",
            "Provide clean, shallow water pans with floating wooden sticks so foraging bees do not drown.",
        ],
        "precautions": [
            "🚨 STRICT DIRECTIVE: Application of any synthetic pyrethroid, organophosphate, or neonicotinoid during bloom is prohibited by SKUAST-K. Insecticides cause immediate bee mortality and colony collapse.",
        ],
    },
    {
        "id": "petal_fall",
        "stage_number": 5,
        "stage_name": "Petal Fall (75% Petal Drop)",
        "kashmiri_name": "Pattian Girna (پتیاں گرنا)",
        "timing": "Early to Mid May",
        "tree_phenology": "75–80% of flower petals have fallen; young fruitlets (2–5 mm) have begun setting.",
        "target_pests": [
            "Apple Scab",
            "Powdery Mildew",
            "Alternaria Leaf Blotch",
            "European Red Mite (first generation nymphs)",
        ],
        "products": [
            {
                "product": "Dodine 65 WP (Syllit)",
                "common_brands": "Syllit 65 WP",
                "dosage_per_100l": "60 grams",
                "dosage_per_1000l": "600 grams",
                "dosage_per_16l": "10 grams",
                "purpose": "Translaminar and curative scab control on tender newly formed leaves",
                "type": "Guanidine translaminar fungicide",
            },
            {
                "product": "Trifloxystrobin + Tebuconazole (Nativo 75 WG)",
                "common_brands": "Bayer Nativo 75 WG",
                "dosage_per_100l": "40 grams",
                "dosage_per_1000l": "400 grams",
                "dosage_per_16l": "6.5 grams",
                "purpose": "Broad-spectrum systemic control of Scab, Alternaria, and Mildew",
                "type": "Strobilurin + Triazole combination",
            },
            {
                "product": "Kresoxim-methyl 44.3 SC (Ergon)",
                "common_brands": "Rallis Ergon",
                "dosage_per_100l": "50 ml",
                "dosage_per_1000l": "500 ml",
                "dosage_per_16l": "8 ml",
                "purpose": "Mesostemic protective and curative activity with vapor phase distribution",
                "type": "Strobilurin fungicide",
            },
        ],
        "cultural_sanitation": [
            "Inspect underside of young leaves with 10x hand lens for red mite infestation (> 5 mites/leaf warrants acaricide).",
            "Maintain clean tree basins free of dense weed competition.",
        ],
        "precautions": [
            "⚠️ Spray only after dusk or early morning when remaining straggler bees have returned to hives.",
        ],
    },
    {
        "id": "fruit_growth_1",
        "stage_number": 6,
        "stage_name": "Fruit Development I (Walnut / Pea Size)",
        "kashmiri_name": "Gird Phalayee - Awal (پھل کی بڑھوتری - ۱)",
        "timing": "Late May – June",
        "tree_phenology": "Fruitlets reach 15–25 mm (walnut size); rapid shoot extension.",
        "target_pests": [
            "Secondary Apple Scab",
            "Alternaria Leaf Blotch",
            "Fruit Spot / Rot",
            "San Jose Scale (crawler stage)",
            "Woolly Apple Aphid",
        ],
        "products": [
            {
                "product": "Metiram 55% + Pyraclostrobin 5% WG (Cabrio Top)",
                "common_brands": "BASF Cabrio Top",
                "dosage_per_100l": "100 grams",
                "dosage_per_1000l": "1.0 kg",
                "dosage_per_16l": "16 grams",
                "purpose": "Dual protective and translaminar control of Alternaria and Scab",
                "type": "Strobilurin + Dithiocarbamate combination",
            },
            {
                "product": "Mancozeb 75 WP (Indofil M-45)",
                "common_brands": "Indofil M-45",
                "dosage_per_100l": "300 grams",
                "dosage_per_1000l": "3.0 kg",
                "dosage_per_16l": "48 grams",
                "purpose": "Continuous protective multi-site shield against summer spore wash",
                "type": "Contact protectant",
            },
            {
                "product": "Spiromesifen 22.9 SC (Oberon)",
                "common_brands": "Bayer Oberon",
                "dosage_per_100l": "40 ml",
                "dosage_per_1000l": "400 ml",
                "dosage_per_16l": "6.5 ml",
                "purpose": "Selective acaricide for European Red Mite nymphs and adults",
                "type": "Lipid biosynthesis inhibitor miticide",
            },
        ],
        "cultural_sanitation": [
            "Thin overloaded fruit clusters down to 1–2 king fruits per spur to optimize fruit sizing and allow chemical spray penetration.",
            "Summer prune vigorous upright water sprouts shading inner canopy.",
        ],
        "precautions": [
            "⚠️ Do NOT use DMI triazole fungicides (Score/Contaf) more than twice per season to prevent resistant fungal strains.",
        ],
    },
    {
        "id": "fruit_growth_2",
        "stage_number": 7,
        "stage_name": "Fruit Development II (Pre-Harvest / Coloration)",
        "kashmiri_name": "Gird Phalayee - Doum (پھل کی بڑھوتری - ۲)",
        "timing": "July – August",
        "tree_phenology": "Fruit sizing complete; anthocyanin red skin color development commences.",
        "target_pests": [
            "Alternaria Leaf Blotch",
            "Bitter Rot (Colletotrichum)",
            "Sooty Blotch & Flyspeck",
            "Storage Rots",
        ],
        "products": [
            {
                "product": "Ziram 27 SC",
                "common_brands": "Dhanuka Cuman L, Indofil Ziram",
                "dosage_per_100l": "200 ml",
                "dosage_per_1000l": "2.0 Liters",
                "dosage_per_16l": "32 ml",
                "purpose": "Protective summer fungicide effective against late-season Alternaria blotch and fruit rot",
                "type": "Dithiocarbamate protectant",
            },
            {
                "product": "Captan 50 WP",
                "common_brands": "Tata Captaf",
                "dosage_per_100l": "300 grams",
                "dosage_per_1000l": "3.0 kg",
                "dosage_per_16l": "48 grams",
                "purpose": "Improves fruit finish and shields against pre-harvest fungal infections",
                "type": "Contact protectant",
            },
            {
                "product": "Calcium Chloride (Food/Agri Grade)",
                "common_brands": "Soluble Calcium Chloride / Calcium Nitrate",
                "dosage_per_100l": "300–400 grams",
                "dosage_per_1000l": "3.5 kg",
                "dosage_per_16l": "50 grams",
                "purpose": "Foliar nutrient spray strengthening cell walls to prevent Bitter Pit and storage breakdown",
                "type": "Foliar micronutrient",
            },
        ],
        "cultural_sanitation": [
            "Mow orchard floor sod to maintain low relative humidity inside canopy.",
            "Remove dropped and sunburned apples from orchard floor.",
        ],
        "precautions": [
            "⚠️ Observe Pre-Harvest Interval (PHI): Maintain a strict 20-day interval between last pesticide application and commercial harvest.",
        ],
    },
    {
        "id": "post_harvest",
        "stage_number": 8,
        "stage_name": "Post-Harvest / Pre-Leaf Fall",
        "kashmiri_name": "Fasal Bardasht Baad (فصل برادشت بعد)",
        "timing": "October – November",
        "tree_phenology": "Post fruit harvest; leaves mature and prepare for senescence and natural abscission.",
        "target_pests": [
            "Apple Scab Overwintering Pseudothecia Inoculum",
            "Bacterial Blight and Fungal Cankers",
        ],
        "products": [
            {
                "product": "Agricultural Urea (5%)",
                "common_brands": "Commercial Agricultural Urea 46% N",
                "dosage_per_100l": "5.0 kg",
                "dosage_per_1000l": "50.0 kg",
                "dosage_per_16l": "800 grams",
                "purpose": "Accelerates fallen leaf decomposition and eradicates overwintering scab pseudothecia",
                "type": "Nitrogenous leaf litter eradicant",
            },
            {
                "product": "Copper Oxychloride 50 WP (Blitox)",
                "common_brands": "Blitox 50, Tata Rallcop",
                "dosage_per_100l": "300 grams",
                "dosage_per_1000l": "3.0 kg",
                "dosage_per_16l": "48 grams",
                "purpose": "Disinfects leaf scar abscission zones and fresh pruning cuts against canker entry",
                "type": "Inorganic copper bactericide/fungicide",
            },
        ],
        "cultural_sanitation": [
            "Drench both tree canopy and the fallen orchard floor leaf litter with 5% Urea immediately after harvest while leaves are still on branches.",
            "Collect and burn or bury heavily cankered branch debris.",
        ],
        "precautions": [
            "⚠️ Do NOT spray Urea earlier than mid-October to avoid triggering untimely tender autumn vegetative flushes susceptible to early winter freeze.",
        ],
    },
]


# Chemical Tank Compatibility Matrix (SKUAST-K guidelines)
CHEMICAL_COMPATIBILITY_RULES: List[Dict[str, Any]] = [
    {
        "combination": "Tree Spray Oil (TSO/HMO) + Sulphur Fungicides",
        "status": "incompatible",
        "symbol": "❌",
        "verdict": "STRICTLY INCOMPATIBLE",
        "details": "Causes severe foliage phytotoxicity, leaf scorch, and bark injury. Minimum 21-day interval required between oil and sulphur.",
    },
    {
        "combination": "Copper Oxychloride + Dodine / Lime Sulphur",
        "status": "incompatible",
        "symbol": "❌",
        "verdict": "INCOMPATIBLE TANK MIX",
        "details": "Causes chemical precipitation and rapid breakdown of active fungicidal ingredients. Do not mix.",
    },
    {
        "combination": "Mancozeb 75 WP + Chlorpyrifos / Dimethoate",
        "status": "compatible",
        "symbol": "✅",
        "verdict": "COMPATIBLE MIXTURE",
        "details": "Widely tested and safe tank mixture for combined scab protection and sucking pest/aphid control.",
    },
    {
        "combination": "Captan 50 WP + Difenoconazole 25 EC (Score)",
        "status": "compatible",
        "symbol": "✅",
        "verdict": "COMPATIBLE MIXTURE",
        "details": "Standard SKUAST-K protective contact + curative systemic combination during high-pressure scab infection windows.",
    },
    {
        "combination": "Agricultural Urea (5%) + Alkaline Sprays / Lime",
        "status": "incompatible",
        "symbol": "❌",
        "verdict": "INCOMPATIBLE MIXTURE",
        "details": "Alkaline pH causes rapid ammonia volatilization and foliar scorch. Spray Urea separately on orchard floor.",
    },
    {
        "combination": "Dodine 65 WP + Hard Water / Alkaline Agents",
        "status": "caution",
        "symbol": "⚠️",
        "verdict": "USE WITH CAUTION",
        "details": "Dodine flocculates in hard water. Always add Dodine to tank first under continuous agitation.",
    },
]


def get_spray_calendar() -> List[Dict[str, Any]]:
    """Returns the full 8-stage SKUAST-Kashmir Apple Spray Calendar."""
    return SKUAST_ANNUAL_SPRAY_CALENDAR


def get_compatibility_rules() -> List[Dict[str, Any]]:
    """Returns chemical compatibility and tank mixing rules."""
    return CHEMICAL_COMPATIBILITY_RULES


def calculate_tank_mix(chemical_name: str, water_liters: float) -> Dict[str, Any]:
    """Calculates exact required chemical weight or volume for any spray tank capacity."""
    # Find product in calendar
    for stage in SKUAST_ANNUAL_SPRAY_CALENDAR:
        for prod in stage["products"]:
            if chemical_name.lower() in prod["product"].lower():
                dos_str = prod["dosage_per_100l"]
                # Parse rate per 100L
                rate = 0.0
                unit = "grams"
                try:
                    parts = dos_str.split()
                    rate = float(parts[0])
                    unit = parts[1]
                except Exception:
                    pass
                
                total_qty = (rate / 100.0) * water_liters
                formatted_qty = f"{round(total_qty / 1000.0, 2)} kg" if unit in {"grams", "g"} and total_qty >= 1000 else (f"{round(total_qty, 1)} {unit}")
                
                return {
                    "chemical": prod["product"],
                    "water_liters": water_liters,
                    "dosage_per_100l": dos_str,
                    "total_quantity": formatted_qty,
                    "stage_name": stage["stage_name"],
                    "purpose": prod["purpose"],
                }

    # Default rate if not found
    return {
        "chemical": chemical_name,
        "water_liters": water_liters,
        "dosage_per_100l": "300 grams / 100L",
        "total_quantity": f"{round((300 / 100.0) * water_liters, 1)} grams",
        "stage_name": "Standard Protective Cover",
        "purpose": "General protective cover",
    }

