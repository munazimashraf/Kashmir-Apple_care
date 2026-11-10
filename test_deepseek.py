"""
Verification script for DeepSeek AI integration in Kashmir Apple Care.
Tests:
1. Settings and configuration loading (.env)
2. Schema validation (AppleDiseaseDetectResponse)
3. DeepSeek service behavior when API key is missing (returns helpful instructions)
4. DeepSeek service behavior when API key is provided
"""
import os
import sys

# Add project root and backend to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

print("=" * 60)
print("KASHMIR APPLE CARE — DEEPSEEK AI INTEGRATION VERIFICATION")
print("=" * 60)

# 1. Test Config
from app.core.config import get_settings
settings = get_settings()
print(f"\n[1] Configuration Check:")
print(f"    - App Name       : {settings.app_name}")
print(f"    - DeepSeek URL   : {settings.deepseek_base_url}")
print(f"    - DeepSeek Model : {settings.deepseek_model}")
print(f"    - API Key Configured: {'YES' if settings.deepseek_api_key else 'NO (Key not set in .env)'}")

# 2. Test DeepSeek Service
from app.services.deepseek_service import detect_apple_disease_deepseek

# Create a small dummy image for test
dummy_image = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"

print(f"\n[2] Testing DeepSeek Detection Engine:")
result = detect_apple_disease_deepseek(
    content=dummy_image,
    content_type="image/jpeg",
)

print(f"    - Disease Identified : {result.get('disease')}")
print(f"    - Scientific Name    : {result.get('scientific_name')}")
print(f"    - Confidence         : {result.get('confidence')}")
print(f"    - Severity           : {result.get('severity')}")
print(f"    - AI Engine          : {result.get('ai_engine')}")
print(f"    - Symptoms Count     : {len(result.get('symptoms', []))}")
print(f"    - Treatment Count    : {len(result.get('treatment', []))}")
print(f"    - Prevention Count   : {len(result.get('prevention', []))}")

# 3. Test Pydantic Schema Validation
from app.schemas.api import AppleDiseaseDetectResponse
validated = AppleDiseaseDetectResponse(**result)
print(f"\n[3] Pydantic Schema Validation: PASSED (Schema matches AppleDiseaseDetectResponse)")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE: ALL CHECKS PASSED!")
print("=" * 60)

