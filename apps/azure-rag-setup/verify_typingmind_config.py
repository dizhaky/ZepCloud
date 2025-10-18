#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

search_service = os.getenv('AZURE_SEARCH_SERVICE_NAME')
search_key = os.getenv('AZURE_SEARCH_ADMIN_KEY')

print("🔍 VERIFYING TYPINGMIND CONFIGURATION")
print("=====================================")
print("")

print("📋 Your Azure Configuration:")
print(f"   Search Service Name: {search_service}")
print(f"   Index Name: azureblob-index")
print(f"   Query Key: {search_key[:10]}..." if search_key else "   Query Key: NOT SET")
print("   API Version: 2023-11-01")
print("")

print("🔍 TypingMind Settings (from screenshot):")
print("   Search Service Name: typingmind1")
print("   Index Name: ust-info1")
print("   Query Key: (hidden)")
print("   API Version: 2025-09-01")
print("")

if search_service != "typingmind1":
    print("⚠️  CONFIGURATION MISMATCH DETECTED!")
    print("")
    print("❌ Issue: Search Service Name doesn't match")
    print(f"   Expected: {search_service}")
    print("   Current in TypingMind: typingmind1")
    print("")
    
if "ust-info1" != "azureblob-index":
    print("❌ Issue: Index Name doesn't match")
    print("   Expected: azureblob-index")
    print("   Current in TypingMind: ust-info1")
    print("")

print("✅ CORRECT CONFIGURATION:")
print("")
print(f"   Search Service Name: {search_service}")
print("   Index Name: azureblob-index")
print(f"   Query Key: {search_key}")
print("   API Version: 2023-11-01")
print("")
print("📝 Please update TypingMind plugin with these values!")
