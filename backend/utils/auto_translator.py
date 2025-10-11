"""
Auto Translator - Automatically translate UI text to multiple languages
"""
from deep_translator import GoogleTranslator
from typing import Dict, List
import json
import os
from pathlib import Path
import time

class AutoTranslator:
    def __init__(self, cache_file: str = "translations_cache.json"):
        """
        Initialize auto translator with caching
        Args:
            cache_file: File to cache translations
        """
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
        
        # Target languages for South Africa
        self.target_languages = {
            'zu': 'Zulu',
            'xh': 'Xhosa', 
            'st': 'Sesotho',
            'nso': 'Sepedi',
            'tn': 'Tswana',
            'ts': 'Tsonga',
            've': 'Venda',
            'ss': 'Swati',
            'nr': 'Ndebele',
            'af': 'Afrikaans'
        }
        
        # English base texts (you only write in English!)
        self.base_texts = {
            'ui': {
                'welcome': 'Welcome to AI Detection Tool',
                'upload_video': 'Upload Video',
                'upload_document': 'Upload Document',
                'enter_url': 'Enter URL',
                'analyze': 'Analyze',
                'results': 'Results',
                'ai_detected': 'AI-generated content detected',
                'human_content': 'Likely human-generated content',
                'confidence': 'Confidence',
                'language_detected': 'Language Detected',
                'processing': 'Processing your request...',
                'error': 'An error occurred',
                'supported_formats': 'Supported formats',
                'video_info': 'Video Information',
                'audio_info': 'Audio Information',
                'document_info': 'Document Information',
                'no_audio': 'No audio track found',
                'upload_file': 'Upload a file'
            },
            'detection': {
                'high_confidence_ai': 'This content is very likely AI-generated',
                'medium_confidence_ai': 'This content might be AI-generated',
                'low_confidence_ai': 'Uncertain, but possibly AI-generated',
                'high_confidence_human': 'This content is very likely human-created',
                'medium_confidence_human': 'This content might be human-created',
                'low_confidence_human': 'Uncertain, but possibly human-created',
                'warning': 'Be cautious with AI-generated content',
                'safe': 'This appears to be authentic content'
            },
            'error': {
                'file_too_large': 'File is too large. Maximum size is 100MB',
                'invalid_format': 'Invalid file format',
                'no_text_found': 'No text could be extracted from the document',
                'download_failed': 'Failed to download from URL',
                'analysis_failed': 'Analysis failed. Please try again',
                'network_error': 'Network error occurred',
                'invalid_url': 'Invalid URL provided'
            }
        }
    
    def _load_cache(self) -> Dict:
        """Load cached translations from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    print(f"📦 Loaded translations cache from {self.cache_file}")
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save translations to cache file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved translations cache to {self.cache_file}")
        except Exception as e:
            print(f"⚠️ Could not save cache: {e}")
    
    def _get_cache_key(self, text: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        return f"{target_lang}:{text}"
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'en') -> str:
        """
        Translate single text with caching
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code (default: English)
        Returns:
            Translated text
        """
        # Check cache first
        cache_key = self._get_cache_key(text, target_lang)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Translate using Google Translate
        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated = translator.translate(text)
            
            # Cache the result
            self.cache[cache_key] = translated
            
            return translated
        
        except Exception as e:
            print(f"⚠️ Translation error for '{text}' to {target_lang}: {e}")
            return text  # Return original if translation fails
    
    def translate_category(self, category: str, target_lang: str) -> Dict[str, str]:
        """
        Translate all texts in a category
        Args:
            category: 'ui', 'detection', or 'error'
            target_lang: Target language code
        Returns:
            Dictionary of translated texts
        """
        if category not in self.base_texts:
            raise ValueError(f"Unknown category: {category}")
        
        print(f"🔄 Translating {category} to {self.target_languages.get(target_lang, target_lang)}...")
        
        translations = {}
        base_category = self.base_texts[category]
        
        for key, english_text in base_category.items():
            translated = self.translate_text(english_text, target_lang)
            translations[key] = translated
            time.sleep(0.1)  # Small delay to avoid rate limiting
        
        return translations
    
    def generate_all_translations(self, languages: List[str] = None) -> Dict:
        """
        Generate all translations for specified languages
        Args:
            languages: List of language codes (default: all SA languages)
        Returns:
            Complete translations dictionary
        """
        if languages is None:
            languages = list(self.target_languages.keys())
        
        print(f"🌍 Generating translations for {len(languages)} languages...")
        print("This may take a few minutes...")
        
        all_translations = {
            'en': self.base_texts  # Include English as base
        }
        
        for lang_code in languages:
            print(f"\n📝 Processing {self.target_languages.get(lang_code, lang_code)}...")
            
            lang_translations = {}
            
            for category in ['ui', 'detection', 'error']:
                try:
                    lang_translations[category] = self.translate_category(category, lang_code)
                    print(f"   ✅ {category.capitalize()} complete")
                except Exception as e:
                    print(f"   ❌ Error in {category}: {e}")
                    lang_translations[category] = self.base_texts[category]  # Fallback to English
            
            all_translations[lang_code] = lang_translations
        
        # Save cache after generating
        self._save_cache()
        
        print(f"\n✅ Translation generation complete!")
        print(f"📊 Total translations: {sum(len(self.cache) for _ in [1])}")
        
        return all_translations
    
    def get_translation(self, key: str, language: str, category: str = 'ui') -> str:
        """
        Get a single translation on-demand
        Args:
            key: Translation key
            language: Language code
            category: 'ui', 'detection', or 'error'
        Returns:
            Translated text
        """
        # Get English text
        if category not in self.base_texts:
            return key
        
        english_text = self.base_texts[category].get(key)
        
        if not english_text:
            return key
        
        # Return English if requested
        if language == 'en':
            return english_text
        
        # Translate to target language
        return self.translate_text(english_text, language)
    
    def export_translations(self, output_file: str = "translations_export.json"):
        """
        Export all translations to a JSON file
        """
        translations = self.generate_all_translations()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Exported translations to {output_file}")
        return translations


# Standalone script to generate translations
if __name__ == "__main__":
    print("="*60)
    print("Auto Translation Generator")
    print("="*60)
    
    translator = AutoTranslator()
    
    # Generate all translations
    print("\n🚀 Starting translation generation...")
    translations = translator.generate_all_translations()
    
    # Export to file
    translator.export_translations("translations_generated.json")
    
    # Show sample
    print("\n📋 Sample translations:")
    print("-"*60)
    
    sample_key = 'ai_detected'
    print(f"\nKey: '{sample_key}'")
    print(f"English: {translator.base_texts['ui'][sample_key]}")
    
    for lang_code in ['zu', 'xh', 'af']:
        translated = translator.get_translation(sample_key, lang_code, 'ui')
        lang_name = translator.target_languages.get(lang_code, lang_code)
        print(f"{lang_name}: {translated}")
    
    print("\n✅ Done! Translations are cached and ready to use.")