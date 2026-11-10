from typing import Any

# Comprehensive Multi-Crop & Universal Fungus / Disease Advisory Engine
# SKUAST-K Kashmir & Central Plant Pathology Formulations with Dual Drum Dosages
ADVISORIES: dict[str, dict[str, list[dict[str, Any]]]] = {
    "healthy": {
        "all": [
            {
                "product": "No chemical fungicide required",
                "trade_name": "Preventative Crop Care & Balanced Nutrition",
                "dosage_100l": "Nil",
                "dosage_200l": "Nil",
                "rainfastness": "N/A",
                "phi_days": 0,
                "note": "Continue weekly field scouting; ensure proper plant spacing and drip irrigation."
            }
        ]
    },
    "apple_scab": {
        "early": [
            {
                "product": "Mancozeb 75 WP (Protectant)",
                "trade_name": "Indofil M-45 / Dithane M-45",
                "dosage_100l": "300g per 100L water",
                "dosage_200l": "600g per 200L drum",
                "rainfastness": "4 to 6 hours dry foliage required",
                "phi_days": 30,
                "note": "Forms protective barrier; apply immediately prior to rainfall infection periods."
            },
            {
                "product": "Propineb 70 WP (Zinc Boost)",
                "trade_name": "Antracol 70 WP (Bayer)",
                "dosage_100l": "300g per 100L water",
                "dosage_200l": "600g per 200L drum",
                "rainfastness": "3 to 4 hours dry foliage",
                "phi_days": 30,
                "note": "Supplies 15.8% bio-available zinc for foliar greening."
            }
        ],
        "late": [
            {
                "product": "Difenoconazole 25 EC (Curative Systemic)",
                "trade_name": "Score 25 EC (Syngenta)",
                "dosage_100l": "30ml per 100L water",
                "dosage_200l": "60ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Arrests active Venturia mycelium within 72 hours post-infection."
            },
            {
                "product": "Dodine 65 WP (Eradicant & Kickback)",
                "trade_name": "Syllit 65 WP",
                "dosage_100l": "75g per 100L water",
                "dosage_200l": "150g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "High knock-down curative action on primary foliar scab lesions."
            }
        ]
    },
    "apple_powdery_mildew": {
        "all": [
            {
                "product": "Hexaconazole 5 EC (Systemic Triazole)",
                "trade_name": "Contaf 5 EC (Rallis Tata)",
                "dosage_100l": "50ml per 100L water",
                "dosage_200l": "100ml per 200L drum",
                "rainfastness": "2 to 3 hours dry foliage",
                "phi_days": 21,
                "note": "Halts conidial germination and systemic haustorial growth."
            },
            {
                "product": "Penconazole 10 EC (Sterol Biosynthesis Inhibitor)",
                "trade_name": "Topas 10 EC (Syngenta)",
                "dosage_100l": "50ml per 100L water",
                "dosage_200l": "100ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Fast acropetal translocation to shoot tips."
            },
            {
                "product": "Wettable Sulfur 80 WDG (Contact & Mite Suppressant)",
                "trade_name": "Sulphotox 80 WDG / Sulfex",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "4 hours dry foliage",
                "phi_days": 7,
                "note": "Multi-site fungal inhibition; do not apply when ambient temp exceeds 30°C."
            }
        ]
    },
    "apple_alternaria_blotch": {
        "all": [
            {
                "product": "Mancozeb 75 WP + Hexaconazole 5 SC",
                "trade_name": "Avtar 75 WP / Companion",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "3 to 4 hours dry foliage",
                "phi_days": 21,
                "note": "Dual protectant-systemic action prevents necrotic leaf drop."
            },
            {
                "product": "Metiram 55% + Pyraclostrobin 5% WG",
                "trade_name": "Cabrio Top (BASF)",
                "dosage_100l": "200g per 100L water",
                "dosage_200l": "400g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 15,
                "note": "Broad-spectrum strobilurin improves leaf retention and fruit finish."
            }
        ]
    },
    "apple_marssonina_blotch": {
        "all": [
            {
                "product": "Zineb 68% + Hexaconazole 4% WP",
                "trade_name": "Taqat WP (Rallis)",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 20,
                "note": "Effective against summer premature defoliation complexes."
            },
            {
                "product": "Difenoconazole 25 EC",
                "trade_name": "Score 25 EC",
                "dosage_100l": "30ml per 100L water",
                "dosage_200l": "60ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "High penetration prevents lesion coalescence."
            }
        ]
    },
    "apple_cedar_rust": {
        "all": [
            {
                "product": "Myclobutanil 10 WP (Systemic Rust Specialist)",
                "trade_name": "Systhane 10 WP (Dow Agro)",
                "dosage_100l": "40g per 100L water",
                "dosage_200l": "80g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Eradicates aecial and pycnial rust stages."
            },
            {
                "product": "Mancozeb 75 WP (Protective Barrier)",
                "trade_name": "Indofil M-45",
                "dosage_100l": "300g per 100L water",
                "dosage_200l": "600g per 200L drum",
                "rainfastness": "4 hours dry foliage",
                "phi_days": 30,
                "note": "Prevents basidiospore establishment on emerging leaves."
            }
        ]
    },
    "apple_black_rot": {
        "all": [
            {
                "product": "Captan 50 WP (Multi-site Contact Protectant)",
                "trade_name": "Captaf 50 WP (Rallis)",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 14,
                "note": "Controls Botryosphaeria frogeye foliar spots and fruit calyx rot."
            },
            {
                "product": "Thiophanate Methyl 70 WP (Systemic Benzimidazole)",
                "trade_name": "Roko 70 WP (Biostadt)",
                "dosage_100l": "100g per 100L water",
                "dosage_200l": "200g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Systemic healing of cankers and twig blights."
            }
        ]
    },
    "apple_european_red_mite": {
        "all": [
            {
                "product": "Hexythiazox 5.45 EC (Ovicidal Acaricide)",
                "trade_name": "Maiden 5.45 EC (Biostadt)",
                "dosage_100l": "40ml per 100L water",
                "dosage_200l": "80ml per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 21,
                "note": "Kills mite eggs and early nymphs; preserves beneficial predatory typhlodromid mites."
            },
            {
                "product": "Spiromesifen 22.9 SC (Lipid Biosynthesis Inhibitor)",
                "trade_name": "Oberon 22.9 SC (Bayer)",
                "dosage_100l": "40ml per 100L water",
                "dosage_200l": "80ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Excellent knockdown for adult Panonychus ulmi populations."
            }
        ]
    },
    "apple_bitter_pit": {
        "all": [
            {
                "product": "Calcium Chloride 77% (Foliar Calcium Replenishment)",
                "trade_name": "Technical Grade Calcium Chloride Flakes",
                "dosage_100l": "350g per 100L water",
                "dosage_200l": "700g per 200L drum",
                "rainfastness": "2 hours dry foliage",
                "phi_days": 0,
                "note": "Apply 4 to 5 foliar sprays at 12–15 day intervals during fruit expansion."
            },
            {
                "product": "Chelated Calcium (EDTA Ca 10%)",
                "trade_name": "Calmax / ChelaCa",
                "dosage_100l": "150g per 100L water",
                "dosage_200l": "300g per 200L drum",
                "rainfastness": "1 to 2 hours dry foliage",
                "phi_days": 0,
                "note": "Rapid foliar absorption prevents corky sub-epidermal depressions."
            }
        ]
    },
    "apple_fire_blight": {
        "all": [
            {
                "product": "Streptomycin Sulphate 90% + Tetracycline 10%",
                "trade_name": "Streptocycline / Plantomycin",
                "dosage_100l": "6g per 100L water",
                "dosage_200l": "12g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 21,
                "note": "Emergency antibiotic bactericide; prune blighted shoots 30cm below visible margins."
            },
            {
                "product": "Copper Oxychloride 50 WP",
                "trade_name": "Blitox 50 WP",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "4 hours dry foliage",
                "phi_days": 30,
                "note": "Disinfect pruning shears with 70% alcohol between cuts."
            }
        ]
    },
    # Tomato & Solanaceous Diseases
    "tomato_late_blight": {
        "all": [
            {
                "product": "Metalaxyl-M 4% + Mancozeb 64% WP",
                "trade_name": "Ridomil Gold MZ 68 WG (Syngenta)",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 7,
                "note": "Systemic translaminar protection against Phytophthora water-mold blight."
            },
            {
                "product": "Cymoxanil 8% + Mancozeb 64% WP",
                "trade_name": "Curzate M-8 (Corteva)",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "2 to 3 hours dry foliage",
                "phi_days": 7,
                "note": "Strong curative post-infection kickback for cool, damp blight outbreaks."
            },
            {
                "product": "Dimethomorph 50% WP",
                "trade_name": "Acrobat 50 WP (BASF)",
                "dosage_100l": "100g per 100L water",
                "dosage_200l": "200g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 5,
                "note": "Inhibits cell wall formation in oomycete zoospores."
            }
        ]
    },
    "tomato_early_blight": {
        "all": [
            {
                "product": "Chlorothalonil 75 WP (Broad-Spectrum Protectant)",
                "trade_name": "Kavach 75 WP (Syngenta)",
                "dosage_100l": "200g per 100L water",
                "dosage_200l": "400g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 7,
                "note": "Multi-site mode of action prevents Alternaria target-board ring formation."
            },
            {
                "product": "Azoxystrobin 18.2% + Difenoconazole 11.4% SC",
                "trade_name": "Amistar Top (Syngenta)",
                "dosage_100l": "100ml per 100L water",
                "dosage_200l": "200ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 5,
                "note": "Exceptional dual systemic action controlling both early blight and anthracnose."
            }
        ]
    },
    "tomato_bacterial_spot": {
        "all": [
            {
                "product": "Copper Hydroxide 77 WP (Fixed Copper Protectant)",
                "trade_name": "Kocide 3000 (Corteva)",
                "dosage_100l": "200g per 100L water",
                "dosage_200l": "400g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 3,
                "note": "Copper ions disrupt Xanthomonas bacterial membranes."
            },
            {
                "product": "Kasugamycin 3% SL (Bactericidal Antibiotic)",
                "trade_name": "Kasu-B (Arysta)",
                "dosage_100l": "150ml per 100L water",
                "dosage_200l": "300ml per 200L drum",
                "rainfastness": "2 hours dry foliage",
                "phi_days": 7,
                "note": "Systemic protein synthesis inhibition in phytopathogenic bacteria."
            }
        ]
    },
    "tomato_leaf_mold": {
        "all": [
            {
                "product": "Fluxapyroxad + Pyraclostrobin",
                "trade_name": "Priaxor (BASF)",
                "dosage_100l": "60ml per 100L water",
                "dosage_200l": "120ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 7,
                "note": "Rapid suppression of Passalora conidial sporulation on leaf underside."
            },
            {
                "product": "Mancozeb 75 WP",
                "trade_name": "Indofil M-45",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 7,
                "note": "Preventative leaf coating under high greenhouse humidity."
            }
        ]
    },
    "tomato_septoria_leaf_spot": {
        "all": [
            {
                "product": "Chlorothalonil 75 WP",
                "trade_name": "Kavach (Syngenta)",
                "dosage_100l": "200g per 100L water",
                "dosage_200l": "400g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 7,
                "note": "Prevents lower canopy leaf yellowing and Septoria spot spreading."
            },
            {
                "product": "Difenoconazole 25 EC",
                "trade_name": "Score 25 EC",
                "dosage_100l": "30ml per 100L water",
                "dosage_200l": "60ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 5,
                "note": "Curative systemic triazole."
            }
        ]
    },
    "tomato_spider_mites": {
        "all": [
            {
                "product": "Spiromesifen 22.9 SC",
                "trade_name": "Oberon (Bayer)",
                "dosage_100l": "40ml per 100L water",
                "dosage_200l": "80ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 3,
                "note": "Spray undersides of leaves where two-spotted spider mites congregate."
            },
            {
                "product": "Abamectin 1.9 EC (Translaminar Miticide)",
                "trade_name": "Vertimec (Syngenta)",
                "dosage_100l": "40ml per 100L water",
                "dosage_200l": "80ml per 200L drum",
                "rainfastness": "2 hours dry foliage",
                "phi_days": 3,
                "note": "Controls active mites and leafminers."
            }
        ]
    },
    "tomato_target_spot": {
        "all": [
            {
                "product": "Pyraclostrobin 20% WG",
                "trade_name": "Insignia (BASF)",
                "dosage_100l": "80g per 100L water",
                "dosage_200l": "160g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 5,
                "note": "Broad-spectrum control for Corynespora target spots."
            }
        ]
    },
    "tomato_yellow_leaf_curl": {
        "all": [
            {
                "product": "Thiamethoxam 25 WG (Whitefly Vector Control)",
                "trade_name": "Actara 25 WG (Syngenta)",
                "dosage_100l": "40g per 100L water",
                "dosage_200l": "80g per 200L drum",
                "rainfastness": "2 hours dry foliage",
                "phi_days": 7,
                "note": "Controls Bemisia tabaci whiteflies transmitting TYLCV; install yellow sticky traps."
            },
            {
                "product": "Neem Oil 10,000 ppm (Azadirachtin)",
                "trade_name": "Econeem Plus",
                "dosage_100l": "300ml per 100L water",
                "dosage_200l": "600ml per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 0,
                "note": "Organic vector deterrent and oviposition repellent."
            }
        ]
    },
    "potato_late_blight": {
        "all": [
            {
                "product": "Mandipropamid 23.4% SC",
                "trade_name": "Revus 250 SC (Syngenta)",
                "dosage_100l": "80ml per 100L water",
                "dosage_200l": "160ml per 200L drum",
                "rainfastness": "1 hour rainfastness",
                "phi_days": 7,
                "note": "Exceptional rain-resistant oomycete protection for potato tubers and foliage."
            },
            {
                "product": "Metalaxyl 8% + Mancozeb 64% WP",
                "trade_name": "Ridomil Gold MZ 68 WG",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 10,
                "note": "Standard field systemic for aggressive Phytophthora late blight."
            }
        ]
    },
    "potato_early_blight": {
        "all": [
            {
                "product": "Mancozeb 75 WP",
                "trade_name": "Indofil M-45",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 14,
                "note": "Prevents Alternaria leaf spots and tuber dry rot."
            },
            {
                "product": "Difenoconazole 25 EC",
                "trade_name": "Score 25 EC",
                "dosage_100l": "30ml per 100L water",
                "dosage_200l": "60ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 7,
                "note": "Curative triazole stops necrotic lesion spread."
            }
        ]
    },
    "grape_black_rot": {
        "all": [
            {
                "product": "Myclobutanil 10 WP",
                "trade_name": "Systhane 10 WP",
                "dosage_100l": "40g per 100L water",
                "dosage_200l": "80g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Prevents Guignardia black rot mummification of grape berry clusters."
            },
            {
                "product": "Mancozeb 75 WP",
                "trade_name": "Indofil M-45",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 28,
                "note": "Early season cluster protection."
            }
        ]
    },
    "grape_downy_mildew": {
        "all": [
            {
                "product": "Fosetyl-Al 80 WP (Systemic Phosphonate)",
                "trade_name": "Aliette 80 WP (Bayer)",
                "dosage_100l": "200g per 100L water",
                "dosage_200l": "400g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Two-way basipetal and acropetal translocation; boosts vine self-defense."
            },
            {
                "product": "Copper Oxychloride 50 WP",
                "trade_name": "Blitox 50 WP",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "4 hours dry foliage",
                "phi_days": 21,
                "note": "Contact shield against oil-spot leaf infections."
            }
        ]
    },
    "grape_powdery_mildew": {
        "all": [
            {
                "product": "Penconazole 10 EC",
                "trade_name": "Topas 10 EC",
                "dosage_100l": "40ml per 100L water",
                "dosage_200l": "80ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Prevents berry splitting and powdery fungal webbing."
            },
            {
                "product": "Wettable Sulfur 80 WDG",
                "trade_name": "Sulphotox",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "4 hours dry foliage",
                "phi_days": 5,
                "note": "Multi-site organic contact fungicide."
            }
        ]
    },
    "corn_common_rust": {
        "all": [
            {
                "product": "Propiconazole 25 EC",
                "trade_name": "Tilt 25 EC (Syngenta)",
                "dosage_100l": "50ml per 100L water",
                "dosage_200l": "100ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 21,
                "note": "Eradicates Puccinia sorghi rust pustules on maize leaf blades."
            },
            {
                "product": "Azoxystrobin 23 SC",
                "trade_name": "Amistar (Syngenta)",
                "dosage_100l": "80ml per 100L water",
                "dosage_200l": "160ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Provides stay-green crop canopy effect."
            }
        ]
    },
    "corn_northern_leaf_blight": {
        "all": [
            {
                "product": "Azoxystrobin + Difenoconazole",
                "trade_name": "Amistar Top",
                "dosage_100l": "100ml per 100L water",
                "dosage_200l": "200ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 21,
                "note": "Stops long cigar-shaped Exserohilum necrotic lesions."
            }
        ]
    },
    "squash_powdery_mildew": {
        "all": [
            {
                "product": "Myclobutanil 10 WP",
                "trade_name": "Systhane 10 WP",
                "dosage_100l": "40g per 100L water",
                "dosage_200l": "80g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 3,
                "note": "Controls white powdery mycelia on cucurbit/squash vines."
            },
            {
                "product": "Potassium Bicarbonate / Bio-Sulfur",
                "trade_name": "Armicarb / Sulphotox",
                "dosage_100l": "300g per 100L water",
                "dosage_200l": "600g per 200L drum",
                "rainfastness": "2 hours dry foliage",
                "phi_days": 1,
                "note": "Organic contact curative; alters leaf surface pH to kill spores."
            }
        ]
    },
    "strawberry_leaf_scorch": {
        "all": [
            {
                "product": "Captan 50 WP",
                "trade_name": "Captaf 50 WP",
                "dosage_100l": "200g per 100L water",
                "dosage_200l": "400g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 7,
                "note": "Prevents purple-bordered scorch lesions on strawberry crowns and leaves."
            }
        ]
    },
    # Universal / Any Plant Fungal & Bacterial Diseases
    "anthracnose_leaf_spot": {
        "all": [
            {
                "product": "Tebuconazole 50% + Trifloxystrobin 25% WG",
                "trade_name": "Nativo 75 WG (Bayer)",
                "dosage_100l": "80g per 100L water",
                "dosage_200l": "160g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Leading systemic broad-spectrum curative for Colletotrichum anthracnose rot."
            },
            {
                "product": "Carbendazim 12% + Mancozeb 63% WP",
                "trade_name": "SAAF WP (UPL)",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 14,
                "note": "Dual contact-systemic benchmark fungicide."
            }
        ]
    },
    "botrytis_gray_mold": {
        "all": [
            {
                "product": "Cyprodinil 37.5% + Fludioxonil 25% WG",
                "trade_name": "Switch 62.5 WG (Syngenta)",
                "dosage_100l": "100g per 100L water",
                "dosage_200l": "200g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 7,
                "note": "Targets Botrytis cinerea gray mold and blossom blight."
            },
            {
                "product": "Iprodione 50 WP",
                "trade_name": "Rovral 50 WP (FMC)",
                "dosage_100l": "200g per 100L water",
                "dosage_200l": "400g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 10,
                "note": "Inhibits spore germination and fungal mycelium growth."
            }
        ]
    },
    "downy_mildew_universal": {
        "all": [
            {
                "product": "Metalaxyl 8% + Mancozeb 64% WP",
                "trade_name": "Ridomil Gold MZ 68 WG",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 10,
                "note": "Systemic downy mildew control on cucurbits, brassicas, and grapes."
            },
            {
                "product": "Copper Oxychloride 50 WP",
                "trade_name": "Blitox 50 WP",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "4 hours dry foliage",
                "phi_days": 21,
                "note": "Protective copper barrier."
            }
        ]
    },
    "powdery_mildew_universal": {
        "all": [
            {
                "product": "Hexaconazole 5 EC",
                "trade_name": "Contaf 5 EC",
                "dosage_100l": "50ml per 100L water",
                "dosage_200l": "100ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 14,
                "note": "Broad-spectrum powdery mildew cure across horticultural and cereal crops."
            },
            {
                "product": "Wettable Sulfur 80 WDG",
                "trade_name": "Sulphotox 80 WDG",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "4 hours dry foliage",
                "phi_days": 5,
                "note": "Organic multi-site contact fungicide."
            }
        ]
    },
    "rust_fungus_universal": {
        "all": [
            {
                "product": "Propiconazole 25 EC",
                "trade_name": "Tilt 25 EC",
                "dosage_100l": "50ml per 100L water",
                "dosage_200l": "100ml per 200L drum",
                "rainfastness": "2 hours rainfastness",
                "phi_days": 21,
                "note": "Curative triazole eradicating foliar rust pustules."
            },
            {
                "product": "Mancozeb 75 WP",
                "trade_name": "Indofil M-45",
                "dosage_100l": "250g per 100L water",
                "dosage_200l": "500g per 200L drum",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 21,
                "note": "Protective contact fungicide against fungal rust spores."
            }
        ]
    },
    "bacterial_blight_universal": {
        "all": [
            {
                "product": "Copper Oxychloride 50 WP + Streptomycin Sulphate",
                "trade_name": "Blitox 50 WP (250g) + Streptocycline (6g)",
                "dosage_100l": "250g Blitox + 6g Streptocycline per 100L",
                "dosage_200l": "500g Blitox + 12g Streptocycline per 200L",
                "rainfastness": "3 hours dry foliage",
                "phi_days": 14,
                "note": "Dual bactericidal barrier against bacterial leaf spots, wilts, and blights."
            }
        ]
    }
}

INSECT_PESTS = {
    "woolly_apple_aphid",
    "aphids",
    "codling_moth",
    "apple_maggot",
    "leafroller",
    "european_red_mite",
    "apple_european_red_mite",
    "two_spotted_spider_mite",
    "tomato_spider_mites",
    "tomato_yellow_leaf_curl",
    "scale_insects",
}


def build_advisory(disease: str, growth_stage: str, rain_within_12_hours: bool) -> dict[str, Any]:
    disease = {
        "alternaria_leaf_blotch": "apple_alternaria_blotch",
        "powdery_mildew": "apple_powdery_mildew",
        "cedar_apple_rust": "apple_cedar_rust",
        "black_rot": "apple_black_rot",
    }.get(disease, disease)
    # Look up direct match or fallback to closest matching universal category
    rule = ADVISORIES.get(disease)
    if not rule:
        if "mildew" in disease:
            rule = ADVISORIES["powdery_mildew_universal"]
        elif "rust" in disease:
            rule = ADVISORIES["rust_fungus_universal"]
        elif "blight" in disease:
            rule = ADVISORIES["tomato_early_blight"]
        elif "rot" in disease or "blotch" in disease or "spot" in disease:
            rule = ADVISORIES["anthracnose_leaf_spot"]
        elif "mite" in disease:
            rule = ADVISORIES["apple_european_red_mite"]
        else:
            rule = ADVISORIES["healthy"]

    early_stages = {"Dormant", "Silver Tip", "Green Tip", "Pink Bud"}

    # Full Bloom Honeybee Pollinator Shield: strictly NO chemical insecticides
    if growth_stage == "Full Bloom" and disease in INSECT_PESTS:
        products: list[dict[str, Any]] = []
    else:
        if "all" in rule:
            raw_products = rule["all"]
        elif growth_stage in early_stages and "early" in rule:
            raw_products = rule["early"]
        elif "late" in rule:
            raw_products = rule["late"]
        else:
            raw_products = rule.get("all", [])
        products = raw_products

    guardrails: list[str] = []

    # Rain & weather window
    if rain_within_12_hours:
        guardrails.append("⚠️ POSTPONE APPLICATION: Rain is predicted within 12 hours. Chemical wash-off will occur, wasting spray and reducing efficacy.")
    else:
        guardrails.append("✅ FAVORABLE SPRAY WINDOW: No rain forecast in the next 12 hours. Ensure foliage is dry before spraying.")

    # Pollinator protection
    if growth_stage == "Full Bloom":
        guardrails.append("🐝 POLLINATOR SHIELD: Honeybees and wild pollinators are actively foraging. NO synthetic chemical insecticides are permitted during Full Bloom.")
    else:
        guardrails.append("🐝 BEE-SAFE APPLICATION: Spray only in early morning or late dusk when pollinator flight ceases.")

    # Disease-specific sanitation & boosters
    if "mildew" in disease:
        guardrails.append('✂️ MECHANICAL SANITATION: Prune out and incinerate infected shoots with visible powdery fungal felt before spraying.')
    if "blight" in disease:
        guardrails.append("🔥 SANITATION: Remove and deeply bury heavily blighted foliage; avoid overhead sprinkler irrigation.")
    if "bitter_pit" in disease or growth_stage in {"Fruit Growth", "Fruit Development", "Walnut Stage"}:
        guardrails.append("🧊 CALCIUM BOOSTER: Add Calcium Chloride 77% @ 3–4g/L water (600–800g / 200L drum) to prevent corky fruit cavities.")

    # Worker safety
    guardrails.append("🛡️ OPERATOR PPE: Wear rubber gloves, eye goggles, boots, and an organic vapor face respirator during tank mixing and application.")

    return {
        "recommendations": products,
        "guardrails": guardrails,
        "growth_stage": growth_stage,
    }
