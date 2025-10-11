"""
Multilingual Helper - Dynamic translation support with auto-translation
"""
from typing import Dict, List, Optional
from utils.auto_translator import AutoTranslator

class MultilingualHelper:
    def __init__(self, use_cache: bool = True):
        """
        Initialize multilingual helper with auto-translation
        Args:
            use_cache: Use cached translations (faster)
        """
        self.translator = AutoTranslator()
        self.default_language = 'en'
        
        # Language names in their native script
        self.language_names = {
            'en': 'English',
            'zu': 'isiZulu',
            'xh': 'isiXhosa',
            'st': 'Sesotho',
            'af': 'Afrikaans',
            'nso': 'Sepedi',
            'tn': 'Setswana',
            'ts': 'Xitsonga',
            've': 'Tshivenda',
            'ss': 'siSwati',
            'nr': 'isiNdebele',
            'fr': 'Français',
            'pt': 'Português',
            'es': 'Español',
            'de': 'Deutsch',
            'it': 'Italiano',
            'ar': 'العربية',
            'zh-CN': '中文',
            'hi': 'हिन्दी',
            'sw': 'Kiswahili'
        }
        
        # South African official languages
        self.sa_languages = ['en', 'zu', 'xh', 'st', 'af', 'nso', 'tn', 'ts', 've', 'ss', 'nr']
    
    def get_message(self, key: str, language: str = 'en', category: str = 'ui') -> str:
        """
        Get translated message (auto-translates on demand)
        Args:
            key: Message key
            language: Language code
            category: 'ui', 'detection', or 'error'
        Returns:
            Translated message
        """
        try:
            return self.translator.get_translation(key, language, category)
        except Exception as e:
            print(f"⚠️ Translation error for key '{key}' in {language}: {e}")
            # Fallback to English
            if language != 'en':
                return self.translator.get_translation(key, 'en', category)
            return key
    
    def get_detection_message(self, is_ai: bool, confidence: float, language: str = 'en') -> str:
        """
        Get appropriate detection message based on result
        Args:
            is_ai: Whether content is AI-generated
            confidence: Confidence score (0-100)
            language: Language code
        Returns:
            Appropriate message in specified language
        """
        # Determine confidence level
        if confidence >= 80:
            level = 'high'
        elif confidence >= 60:
            level = 'medium'
        else:
            level = 'low'
        
        # Determine content type
        content_type = 'ai' if is_ai else 'human'
        
        # Build message key
        key = f"{level}_confidence_{content_type}"
        
        return self.get_message(key, language, 'detection')
    
    def get_warning_message(self, is_ai: bool, language: str = 'en') -> str:
        """
        Get warning or safe message
        Args:
            is_ai: Whether content is AI-generated
            language: Language code
        Returns:
            Warning or safe message
        """
        key = 'warning' if is_ai else 'safe'
        return self.get_message(key, language, 'detection')
    
    def format_full_response(
        self, 
        detection_result: Dict, 
        language: str = 'en',
        include_warnings: bool = True
    ) -> Dict:
        """
        Format complete response with multilingual messages
        Args:
            detection_result: Raw detection result
            language: Target language
            include_warnings: Include warning messages
        Returns:
            Formatted response with translations
        """
        is_ai = detection_result.get('is_ai_generated', False)
        confidence = detection_result.get('confidence_score', 0)
        
        # Get main message (auto-translated)
        main_message = self.get_detection_message(is_ai, confidence, language)
        
        # Prepare formatted result
        formatted = {
            **detection_result,
            'message': main_message,
            'language': language,
            'language_name': self.language_names.get(language, language)
        }
        
        # Add warning if requested (auto-translated)
        if include_warnings:
            formatted['warning'] = self.get_warning_message(is_ai, language)
        
        # Add confidence label (auto-translated)
        formatted['confidence_label'] = self.get_message('confidence', language, 'ui')
        
        return formatted
    
    def get_all_translations(self, language: str = 'en') -> Dict:
        """
        Get all translations for a specific language
        Args:
            language: Language code
        Returns:
            Dictionary with all translations
        """
        translations = {}
        
        # Get translations for each category
        for category in ['ui', 'detection', 'error']:
            category_translations = {}
            
            # Get all keys from base texts
            base_texts = self.translator.base_texts.get(category, {})
            
            for key in base_texts.keys():
                category_translations[key] = self.get_message(key, language, category)
            
            translations[category] = category_translations
        
        # Add language metadata
        translations['language_name'] = self.language_names.get(language, language)
        translations['language_code'] = language
        translations['is_sa_language'] = language in self.sa_languages
        
        return translations
    
    def get_supported_languages(self) -> List[Dict]:
        """
        Get list of all supported languages
        Returns:
            List of language dictionaries
        """
        languages = []
        for code, name in self.language_names.items():
            languages.append({
                'code': code,
                'name': name,
                'native_name': name,
                'is_sa_language': code in self.sa_languages,
                'has_full_support': True  # All languages now have full support via auto-translation!
            })
        
        return languages
    
    def get_sa_languages(self) -> List[Dict]:
        """
        Get list of South African languages only
        Returns:
            List of SA language dictionaries
        """
        languages = []
        for code in self.sa_languages:
            name = self.language_names.get(code, code)
            languages.append({
                'code': code,
                'name': name,
                'native_name': name
            })
        
        return languages
    
    def validate_language_code(self, language: str) -> bool:
        """
        Check if language code is supported
        Args:
            language: Language code to validate
        Returns:
            True if supported, False otherwise
        """
        return language in self.language_names
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get the name of a language from its code
        Args:
            language_code: Language code
        Returns:
            Language name in native script
        """
        return self.language_names.get(language_code, language_code)
    
    def is_sa_language(self, language_code: str) -> bool:
        """
        Check if language is a South African official language
        Args:
            language_code: Language code to check
        Returns:
            True if it's an SA language
        """
        return language_code in self.sa_languages
    
    def get_ui_labels(self, language: str = 'en') -> Dict[str, str]:
        """
        Get common UI labels in specified language
        Args:
            language: Language code
        Returns:
            Dictionary of translated UI labels
        """
        common_labels = [
            'welcome', 'upload_video', 'upload_document', 'enter_url',
            'analyze', 'results', 'confidence', 'processing',
            'video_info', 'audio_info', 'document_info'
        ]
        
        labels = {}
        for label in common_labels:
            labels[label] = self.get_message(label, language, 'ui')
        
        return labels
    
    def get_error_message(self, error_key: str, language: str = 'en') -> str:
        """
        Get error message in specified language
        Args:
            error_key: Error message key
            language: Language code
        Returns:
            Translated error message
        """
        return self.get_message(error_key, language, 'error')
    
    def translate_detection_result(
        self,
        is_ai: bool,
        confidence: float,
        source_language: str,
        target_language: str
    ) -> Dict:
        """
        Get detection result messages in multiple languages
        Args:
            is_ai: Whether content is AI-generated
            confidence: Confidence score
            source_language: Original language of content
            target_language: Language for result messages
        Returns:
            Dictionary with translated messages
        """
        return {
            'is_ai_generated': is_ai,
            'confidence_score': confidence,
            'message': self.get_detection_message(is_ai, confidence, target_language),
            'warning': self.get_warning_message(is_ai, target_language),
            'confidence_label': self.get_message('confidence', target_language, 'ui'),
            'source_language': {
                'code': source_language,
                'name': self.get_language_name(source_language)
            },
            'result_language': {
                'code': target_language,
                'name': self.get_language_name(target_language)
            }
        }
    
    def pre_generate_translations(self, languages: List[str] = None):
        """
        Pre-generate translations for faster runtime
        Call this during startup or as a background task
        Args:
            languages: List of language codes (default: all SA languages)
        """
        if languages is None:
            languages = self.sa_languages
        
        print(f"🌍 Pre-generating translations for {len(languages)} languages...")
        
        try:
            self.translator.generate_all_translations(languages)
            print("✅ Translations ready and cached!")
        except Exception as e:
            print(f"⚠️ Error during translation generation: {e}")
            print("Translations will be generated on-demand instead")
    
    def get_translation_stats(self) -> Dict:
        """
        Get statistics about cached translations
        Returns:
            Dictionary with translation statistics
        """
        cache = self.translator.cache
        
        # Count translations per language
        lang_counts = {}
        for cache_key in cache.keys():
            if ':' in cache_key:
                lang_code = cache_key.split(':')[0]
                lang_counts[lang_code] = lang_counts.get(lang_code, 0) + 1
        
        return {
            'total_cached': len(cache),
            'languages_cached': len(lang_counts),
            'per_language': lang_counts,
            'supported_languages': len(self.language_names),
            'sa_languages': len(self.sa_languages)
        }
    
    def format_multilingual_error(self, error_key: str, language: str = 'en', **kwargs) -> Dict:
        """
        Format error response with multilingual message
        Args:
            error_key: Error message key
            language: Target language
            **kwargs: Additional error details
        Returns:
            Formatted error response
        """
        error_message = self.get_error_message(error_key, language)
        
        return {
            'success': False,
            'error': error_message,
            'error_key': error_key,
            'language': language,
            **kwargs
        }


# Test function
if __name__ == "__main__":
    print("="*70)
    print("Testing Multilingual Helper with Auto-Translation")
    print("="*70)
    
    helper = MultilingualHelper()
    
    # Test 1: Get message in different languages
    print("\n📝 Test 1: Auto-translating UI messages")
    print("-"*70)
    
    test_key = 'ai_detected'
    test_langs = ['en', 'zu', 'xh', 'af', 'st']
    
    print(f"\nTranslating '{test_key}' to multiple languages:\n")
    
    for lang in test_langs:
        message = helper.get_message(test_key, lang, 'ui')
        lang_name = helper.get_language_name(lang)
        print(f"  {lang_name:15} ({lang}): {message}")
    
    # Test 2: Detection messages
    print("\n\n Test 2: Detection messages with different confidence levels")
    print("-"*70)
    
    test_cases = [
        {'is_ai': True, 'confidence': 95, 'lang': 'en'},
        {'is_ai': True, 'confidence': 95, 'lang': 'zu'},
        {'is_ai': False, 'confidence': 88, 'lang': 'xh'},
    ]
    
    for case in test_cases:
        message = helper.get_detection_message(
            case['is_ai'],
            case['confidence'],
            case['lang']
        )
        lang_name = helper.get_language_name(case['lang'])
        result_type = "AI" if case['is_ai'] else "Human"
        
        print(f"\n  {lang_name} ({result_type}, {case['confidence']}% confidence):")
        print(f"    {message}")
    
    # Test 3: Full response formatting
    print("\n\n🎨 Test 3: Full response formatting")
    print("-"*70)
    
    sample_result = {
        'is_ai_generated': True,
        'confidence_score': 87.5,
        'chunks_analyzed': 5
    }
    
    formatted = helper.format_full_response(sample_result, 'zu', include_warnings=True)
    
    print(f"\nFormatted response in isiZulu:")
    print(f"  Message: {formatted['message']}")
    print(f"  Warning: {formatted['warning']}")
    print(f"  Confidence Label: {formatted['confidence_label']}")
    
    # Test 4: Supported languages
    print("\n\n🌍 Test 4: Supported languages")
    print("-"*70)
    
    sa_langs = helper.get_sa_languages()
    print(f"\nSouth African Languages ({len(sa_langs)}):")
    for lang in sa_langs:
        print(f"  • {lang['name']} ({lang['code']})")
    
    # Test 5: Translation statistics
    print("\n\n Test 5: Translation cache statistics")
    print("-"*70)
    
    stats = helper.get_translation_stats()
    print(f"\n  Total cached translations: {stats['total_cached']}")
    print(f"  Languages with cached translations: {stats['languages_cached']}")
    print(f"  Total supported languages: {stats['supported_languages']}")
    print(f"  South African languages: {stats['sa_languages']}")
    
    if stats['per_language']:
        print("\n  Translations per language:")
        for lang_code, count in list(stats['per_language'].items())[:5]:
            lang_name = helper.get_language_name(lang_code)
            print(f"    {lang_name} ({lang_code}): {count} translations")
    
    # Test 6: Error messages
    print("\n\n Test 6: Error messages in different languages")
    print("-"*70)
    
    error_test_langs = ['en', 'zu', 'af']
    error_key = 'invalid_format'
    
    print(f"\nError: '{error_key}'\n")
    
    for lang in error_test_langs:
        error_msg = helper.get_error_message(error_key, lang)
        lang_name = helper.get_language_name(lang)
        print(f"  {lang_name}: {error_msg}")
    
    print("\n" + "="*70)
    print(" All tests complete!")
    print("="*70)
    print("\n💡 Tip: Run 'python generate_translations.py' to pre-cache all translations")