"""
Language Handler - Multilingual support and translation
"""
from langdetect import detect, detect_langs
from deep_translator import GoogleTranslator
from typing import Dict, List, Optional
import re

class LanguageHandler:
    def __init__(self):
        """
        Initialize language handler with South African languages
        """
        # South African official languages
        self.sa_languages = {
            'zu': 'isiZulu',
            'xh': 'isiXhosa',
            'st': 'Sesotho',
            'nso': 'Sepedi',
            'tn': 'Setswana',
            'ts': 'Xitsonga',
            've': 'Tshivenda',
            'ss': 'siSwati',
            'nr': 'isiNdebele',
            'af': 'Afrikaans',
            'en': 'English'
        }
        
        # Language codes supported by Google Translate
        self.supported_languages = {
            'af': 'Afrikaans',
            'en': 'English',
            'zu': 'Zulu',
            'xh': 'Xhosa',
            'st': 'Sesotho',
            'nso': 'Sepedi',
            'tn': 'Tswana',
            'ts': 'Tsonga',
            've': 'Venda',
            'ss': 'Swati',
            'nr': 'Ndebele',
            'fr': 'French',
            'pt': 'Portuguese',
            'es': 'Spanish',
            'de': 'German',
            'it': 'Italian',
            'ar': 'Arabic',
            'zh-CN': 'Chinese (Simplified)',
            'hi': 'Hindi',
            'sw': 'Swahili'
        }
        
        # Common phrases for UI in different languages
        self.ui_translations = {
            'en': {
                'ai_detected': 'AI-generated content detected',
                'human_content': 'Likely human-generated content',
                'confidence': 'Confidence',
                'analysis_complete': 'Analysis complete',
                'no_audio': 'No audio track found',
                'processing': 'Processing...',
                'error': 'Error occurred',
                'upload_file': 'Upload a file',
                'enter_url': 'Enter URL'
            },
            'zu': {
                'ai_detected': 'Okudalwe yi-AI kutholiwe',
                'human_content': 'Cishe okudalwe umuntu',
                'confidence': 'Ukwethemba',
                'analysis_complete': 'Ukuhlaziya kuqediwe',
                'no_audio': 'Ayikho i-audio track',
                'processing': 'Iyacubungula...',
                'error': 'Kukhona iphutha',
                'upload_file': 'Layisha ifayela',
                'enter_url': 'Faka i-URL'
            },
            'xh': {
                'ai_detected': 'Umxholo oveliswe yi-AI ufunyenwe',
                'human_content': 'Mhlawumbi umxholo oveliswe ngumntu',
                'confidence': 'Ukuzithemba',
                'analysis_complete': 'Uhlalutyo lugqityiwe',
                'no_audio': 'Akukho audio track',
                'processing': 'Iyaqhubeka...',
                'error': 'Impazamo yenzekile',
                'upload_file': 'Faka ifayile',
                'enter_url': 'Ngenisa i-URL'
            },
            'st': {
                'ai_detected': 'Diteng tse hlahisitsweng ke AI di fumanwe',
                'human_content': 'Mohlomong ke diteng tse hlahisitsweng ke motho',
                'confidence': 'Tshepo',
                'analysis_complete': 'Manollo e phethilwe',
                'no_audio': 'Ha ho audio track',
                'processing': 'E ntse e sebetsa...',
                'error': 'Phoso e etsahetse',
                'upload_file': 'Kenya faele',
                'enter_url': 'Kenya URL'
            },
            'af': {
                'ai_detected': 'KI-gegenereerde inhoud opgespoor',
                'human_content': 'Waarskynlik mens-gegenereerde inhoud',
                'confidence': 'Vertroue',
                'analysis_complete': 'Analise voltooi',
                'no_audio': 'Geen oudiobaan gevind nie',
                'processing': 'Verwerk...',
                'error': 'Fout het voorgekom',
                'upload_file': 'Laai lêer op',
                'enter_url': 'Voer URL in'
            }
        }
    
    def detect_language(self, text: str) -> Dict:
        """
        Detect the language of given text
        Args:
            text: Text to analyze
        Returns:
            Dictionary with language info
        """
        try:
            # Detect primary language
            lang_code = detect(text)
            
            # Get all detected languages with probabilities
            lang_probs = detect_langs(text)
            
            # Get language name
            lang_name = self.supported_languages.get(lang_code, 'Unknown')
            
            # Check if it's a South African language
            is_sa_language = lang_code in self.sa_languages
            
            print(f"🌍 Detected language: {lang_name} ({lang_code})")
            
            return {
                'code': lang_code,
                'name': lang_name,
                'is_sa_language': is_sa_language,
                'confidence': float(str(lang_probs[0]).split(':')[1]) if lang_probs else 1.0,
                'all_detected': [{'code': str(lp).split(':')[0], 'prob': float(str(lp).split(':')[1])} for lp in lang_probs]
            }
        
        except Exception as e:
            print(f"⚠️ Language detection error: {e}")
            return {
                'code': 'en',
                'name': 'English',
                'is_sa_language': False,
                'confidence': 0.5,
                'error': str(e)
            }
    
    def translate_text(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> Dict:
        """
        Translate text between languages
        Args:
            text: Text to translate
            source_lang: Source language code (default: auto-detect)
            target_lang: Target language code
        Returns:
            Dictionary with translation result
        """
        try:
            if not text or len(text.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Empty text provided'
                }
            
            print(f"🔄 Translating from {source_lang} to {target_lang}")
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Handle long text by splitting into chunks
            max_chunk_size = 4900  # Google Translate limit is 5000
            if len(text) > max_chunk_size:
                chunks = self._split_text(text, max_chunk_size)
                translated_chunks = []
                
                for chunk in chunks:
                    translated = translator.translate(chunk)
                    translated_chunks.append(translated)
                
                translated_text = ' '.join(translated_chunks)
            else:
                translated_text = translator.translate(text)
            
            print(f"✅ Translation complete")
            
            return {
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
        
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_text': text
            }
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """
        Split text into chunks at sentence boundaries
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_ui_text(self, key: str, language: str = 'en') -> str:
        """
        Get UI text in specified language
        Args:
            key: Translation key
            language: Language code
        Returns:
            Translated UI text
        """
        lang_dict = self.ui_translations.get(language, self.ui_translations['en'])
        return lang_dict.get(key, self.ui_translations['en'].get(key, key))
    
    def format_detection_result(self, result: Dict, language: str = 'en') -> Dict:
        """
        Format detection result with translations
        Args:
            result: Detection result dictionary
            language: Target language for messages
        Returns:
            Formatted result with translated messages
        """
        is_ai = result.get('is_ai_generated', False)
        confidence = result.get('confidence_score', 0)
        
        # Get appropriate message
        if is_ai:
            message_key = 'ai_detected'
        else:
            message_key = 'human_content'
        
        message = self.get_ui_text(message_key, language)
        confidence_label = self.get_ui_text('confidence', language)
        
        return {
            **result,
            'message': message,
            'confidence_label': confidence_label,
            'language': language
        }
    
    def analyze_multilingual_text(self, text: str, detect_ai_func) -> Dict:
        """
        Analyze text in any language for AI detection
        Args:
            text: Text to analyze
            detect_ai_func: Function to call for AI detection
        Returns:
            Analysis result with language info
        """
        # Detect original language
        lang_info = self.detect_language(text)
        original_lang = lang_info['code']
        
        # If not English, translate to English for AI detection
        if original_lang != 'en':
            print(f"🔄 Non-English text detected, translating for analysis...")
            translation_result = self.translate_text(text, source_lang=original_lang, target_lang='en')
            
            if translation_result['success']:
                text_to_analyze = translation_result['translated_text']
            else:
                # If translation fails, try with original text
                print("⚠️ Translation failed, analyzing original text")
                text_to_analyze = text
        else:
            text_to_analyze = text
        
        # Run AI detection
        detection_result = detect_ai_func(text_to_analyze)
        
        # Add language information
        detection_result['language_info'] = lang_info
        detection_result['original_language'] = original_lang
        detection_result['analyzed_in_english'] = original_lang != 'en'
        
        return detection_result


# Test function
if __name__ == "__main__":
    handler = LanguageHandler()
    
    # Test language detection
    test_texts = {
        'en': "This is a test in English",
        'zu': "Sawubona, kunjani?",
        'xh': "Molo, kunjani?",
        'af': "Hallo, hoe gaan dit?"
    }
    
    print("Testing Language Detection\n" + "="*50)
    
    for expected_lang, text in test_texts.items():
        print(f"\n📝 Text: {text}")
        result = handler.detect_language(text)
        print(f"   Detected: {result['name']} ({result['code']})")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Is SA Language: {result['is_sa_language']}")
    
    # Test UI translations
    print("\n\nTesting UI Translations\n" + "="*50)
    for lang_code in ['en', 'zu', 'xh', 'st', 'af']:
        message = handler.get_ui_text('ai_detected', lang_code)
        print(f"{handler.supported_languages.get(lang_code, lang_code)}: {message}")