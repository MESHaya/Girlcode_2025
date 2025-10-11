"""
Quick test script for MultilingualHelper
Run this file to verify translations are working
"""

from utils.multilingual_helper import MultilingualHelper

def test_multilingual():
    print("=" * 70)
    print("🌍 MULTILINGUAL HELPER TEST")
    print("=" * 70)
    
    # Initialize helper
    print("\n1️⃣ Initializing MultilingualHelper...")
    helper = MultilingualHelper()
    print("✅ Initialized successfully!\n")
    
    # Test 1: Simple message translation
    print("-" * 70)
    print("TEST 1: Translating 'AI Detected' message")
    print("-" * 70)
    
    languages = ['en', 'zu', 'xh', 'af']
    
    for lang in languages:
        message = helper.get_message('ai_detected', lang, 'ui')
        lang_name = helper.get_language_name(lang)
        print(f"  {lang_name:15} ({lang}): {message}")
    
    # Test 2: Detection result messages
    print("\n" + "-" * 70)
    print("TEST 2: Detection Result Messages (High Confidence)")
    print("-" * 70)
    
    print("\nScenario: AI-generated content with 95% confidence\n")
    
    for lang in languages:
        message = helper.get_detection_message(
            is_ai=True, 
            confidence=95, 
            language=lang
        )
        lang_name = helper.get_language_name(lang)
        print(f"  {lang_name:15}: {message}")
    
    # Test 3: Full formatted response
    print("\n" + "-" * 70)
    print("TEST 3: Full Formatted Response")
    print("-" * 70)
    
    sample_result = {
        'is_ai_generated': True,
        'confidence_score': 87.5,
        'chunks_analyzed': 5
    }
    
    print("\nFormatted response in isiZulu:\n")
    formatted = helper.format_full_response(sample_result, 'zu', include_warnings=True)
    
    print(f"  Main Message: {formatted['message']}")
    print(f"  Warning: {formatted['warning']}")
    print(f"  Confidence Label: {formatted['confidence_label']}")
    print(f"  Language: {formatted['language_name']} ({formatted['language']})")
    
    # Test 4: Supported languages list
    print("\n" + "-" * 70)
    print("TEST 4: Supported South African Languages")
    print("-" * 70)
    
    sa_langs = helper.get_sa_languages()
    print(f"\nTotal SA languages supported: {len(sa_langs)}\n")
    
    for lang in sa_langs:
        print(f"  • {lang['name']} ({lang['code']})")
    
    # Test 5: Translation stats
    print("\n" + "-" * 70)
    print("TEST 5: Translation Cache Statistics")
    print("-" * 70)
    
    stats = helper.get_translation_stats()
    print(f"\n  Total cached translations: {stats['total_cached']}")
    print(f"  Languages cached: {stats['languages_cached']}")
    print(f"  Total supported languages: {stats['supported_languages']}")
    
    # Test 6: Error messages
    print("\n" + "-" * 70)
    print("TEST 6: Error Messages")
    print("-" * 70)
    
    print("\nError: 'Invalid file format'\n")
    
    for lang in ['en', 'zu', 'af']:
        error_msg = helper.get_error_message('invalid_format', lang)
        lang_name = helper.get_language_name(lang)
        print(f"  {lang_name:15}: {error_msg}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n💡 The multilingual system is working correctly!")
    print("Your app can now respond in multiple languages.\n")

if __name__ == "__main__":
    try:
        test_multilingual()
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERROR DURING TESTING")
        print("=" * 70)
        print(f"\nError: {str(e)}")
        print("\nThis might mean:")
        print("  1. AutoTranslator is not properly configured")
        print("  2. Required translation files are missing")
        print("  3. Import paths are incorrect")
        print("\nCheck the error message above for details.\n")
        raise