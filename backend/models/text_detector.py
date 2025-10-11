"""
Text AI Detector - Detect if text content is AI-generated (Multilingual)
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List
import numpy as np

class TextAIDetector:
    def __init__(self, model_name: str = "roberta-base"):
        """
        Initialize text AI detection model with multilingual support
        """
        print("Loading multilingual text AI detection model...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        try:
            # Use multilingual model
            self.tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "xlm-roberta-base", 
                num_labels=2
            )
            self.model.to(self.device)
            self.model.eval()
            
            print("Multilingual text detection model loaded!")
        except Exception as e:
            print(f" Using base model: {e}")
            self.tokenizer = AutoTokenizer.from_pretrained("roberta-base")
            self.model = AutoModelForSequenceClassification.from_pretrained("roberta-base", num_labels=2)
            self.model.to(self.device)
            self.model.eval()
        
        # Supported languages
        self.supported_languages = [
            'en', 'zu', 'xh', 'st', 'af', 'nso', 'tn', 'ts', 've', 'ss', 'nr',
            'fr', 'es', 'pt', 'de', 'it', 'ar', 'zh', 'hi', 'sw'
        ]
    
    def detect_text_chunk(self, text: str, language: str = 'en') -> Dict[str, float]:
        """
        Detect if a text chunk is AI-generated (works with multiple languages)
        Args:
            text: Text to analyze
            language: Language code (for logging)
        Returns:
            Dictionary with probabilities
        """
        # Tokenize (xlm-roberta handles multiple languages)
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        probs = probabilities[0].cpu().numpy()
        
        return {
            "human_probability": float(probs[0]),
            "ai_probability": float(probs[1]),
            "language": language
        }
    
    def analyze_document(self, text_chunks: List[str], language: str = 'en') -> Dict:
        """
        Analyze multiple text chunks and aggregate results
        Args:
            text_chunks: List of text chunks to analyze
            language: Language of the text
        Returns:
            Overall detection result
        """
        if not text_chunks:
            raise ValueError("No text chunks provided")
        
        print(f"🔍 Analyzing {len(text_chunks)} text chunk(s) in {language}...")
        
        results = []
        for i, chunk in enumerate(text_chunks[:10]):  # Limit to first 10 chunks
            if len(chunk.strip()) < 10:  # Skip very short chunks
                continue
            
            result = self.detect_text_chunk(chunk, language)
            results.append(result)
            print(f"   Chunk {i+1}: AI={result['ai_probability']:.2%}")
        
        if not results:
            raise ValueError("No valid text chunks to analyze")
        
        # Aggregate results
        avg_ai_prob = np.mean([r['ai_probability'] for r in results])
        avg_human_prob = np.mean([r['human_probability'] for r in results])
        
        is_ai_generated = avg_ai_prob > 0.5
        confidence_score = max(avg_ai_prob, avg_human_prob) * 100
        
        return {
            "is_ai_generated": bool(is_ai_generated),
            "confidence_score": round(confidence_score, 2),
            "avg_ai_probability": round(avg_ai_prob, 4),
            "avg_human_probability": round(avg_human_prob, 4),
            "chunks_analyzed": len(results),
            "language": language
        }