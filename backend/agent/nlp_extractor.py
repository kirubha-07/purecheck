import re
import warnings
from typing import Dict, Tuple
warnings.filterwarnings('ignore')

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Global flag to prevent repeated failed BERT initialization attempts
_BERT_INIT_ATTEMPTED = False
_BERT_AVAILABLE = False

class NLPExtractor:
    """
    Extract food adulteration entities from unstructured text using BERT.
    Uses zero-shot classification, NER, and sentiment analysis.
    Falls back to keyword matching if transformers unavailable.
    """
    
    def __init__(self):
        """Initialize BERT pipelines and keyword dictionaries."""
        # Food and adulterant lists (used as candidate labels for zero-shot classification)
        self.foods = [
            "milk", "rice", "oil", "ghee", "turmeric", "chilli",
            "paneer", "sweets", "vegetables", "fruits", "water",
            "honey", "dal", "flour", "sugar", "salt", "spices",
            "butter", "cheese", "yogurt", "tea", "coffee", "wheat",
            "corn", "mustard oil", "coconut oil", "groundnut oil"
        ]
        
        self.adulterants = [
            "detergent", "starch", "synthetic color", "pesticide",
            "chalk powder", "water", "urea", "vanaspati",
            "metanil yellow", "lead chromate", "calcium carbonate",
            "melamine", "plastic", "sand", "fillers", "microbial",
            "fungus", "bacteria", "mold", "lead", "arsenic",
            "heavy metals", "chemical", "toxic dye", "mineral oil"
        ]
        
        self.cities = {
            "trichy", "tiruchirapalli", "coimbatore", "chennai", "madurai", "salem",
            "bangalore", "delhi", "mumbai", "pune", "hyderabad", "ahmedabad",
            "jaipur", "lucknow", "kolkata", "chandigarh", "bhopal"
        }
        
        self.bert_pipelines = {}
        
        # Only attempt BERT initialization once globally
        global _BERT_INIT_ATTEMPTED, _BERT_AVAILABLE
        if not _BERT_INIT_ATTEMPTED:
            _BERT_INIT_ATTEMPTED = True
            _BERT_AVAILABLE = self._initialize_bert()
        else:
            # Skip BERT if already attempted and failed
            pass
    
    def _initialize_bert(self) -> bool:
        """Initialize BERT pipelines if available. Returns True if successful."""
        if not TRANSFORMERS_AVAILABLE:
            return False
        
        try:
            # Use lightweight DistilBERT instead of BART (much faster, less memory)
            # Note: Requires internet for first download, then caches locally
            self.bert_pipelines['zero_shot'] = pipeline(
                "zero-shot-classification",
                model="distilbert-base-multilingual-uncased",  # Multilingual, ~300MB
                device=-1  # CPU only for compatibility
            )
            
            # Sentiment analysis for severity estimation
            self.bert_pipelines['sentiment'] = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1
            )
            
            print("[NLPExtractor] [OK] BERT pipelines initialized successfully")
            return True
        except Exception as e:
            print(f"[NLPExtractor] Warning: Could not initialize BERT: {e}")
            print("[NLPExtractor] Falling back to keyword-based extraction")
            return False
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extract city, food_item, adulterant, severity from raw text using BERT.
        
        Args:
            text: Raw text to extract from
        
        Returns:
            Dict with keys: city, food_item, adulterant, severity, confidence
        """
        text_lower = text.lower()
        
        # Extract city (using regex/keyword matching - more reliable)
        city = self._extract_city(text_lower)
        
        # Extract food item using BERT if available
        if 'zero_shot' in self.bert_pipelines:
            food_item, food_confidence = self._extract_food_bert(text)
        else:
            food_item = self._extract_food_keyword(text_lower)
            food_confidence = 0.5
        
        # Extract adulterant using BERT if available
        if 'zero_shot' in self.bert_pipelines:
            adulterant, adulterant_confidence = self._extract_adulterant_bert(text)
        else:
            adulterant = self._extract_adulterant_keyword(text_lower)
            adulterant_confidence = 0.5
        
        # Estimate severity using sentiment analysis if BERT available
        if 'sentiment' in self.bert_pipelines:
            severity = self._estimate_severity_bert(text)
        else:
            severity = self._estimate_severity_keyword(text_lower)
        
        # Average confidence score
        confidence = (food_confidence + adulterant_confidence) / 2 if (food_confidence + adulterant_confidence) > 0 else 0.3
        
        return {
            'city': city or 'Unknown',
            'food_item': food_item or 'Unknown',
            'adulterant': adulterant or 'Unknown',
            'severity': severity,
            'confidence': min(0.99, confidence)
        }
    
    def _extract_city(self, text: str) -> str:
        """Extract city name using keyword matching (most reliable)."""
        for city in self.cities:
            # Match city in word boundaries to avoid "salem" matching "salem" in "salem pink"
            pattern = r'\b' + re.escape(city) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                return city.title()
        return None
    
    def _extract_food_bert(self, text: str) -> Tuple[str, float]:
        """Extract food item using BERT zero-shot classification."""
        try:
            result = self.bert_pipelines['zero_shot'](
                text[:512],  # Limit to 512 tokens
                self.foods,
                multi_class=False
            )
            
            if result and result['scores'][0] > 0.3:
                return result['labels'][0].title(), float(result['scores'][0])
            else:
                # Fallback to keyword
                return self._extract_food_keyword(text.lower()), 0.3
        except Exception as e:
            print(f"[NLPExtractor] BERT error in food extraction: {e}")
            return self._extract_food_keyword(text.lower()), 0.3
    
    def _extract_food_keyword(self, text: str) -> str:
        """Extract food item using keyword matching (fallback)."""
        for food in self.foods:
            if food in text:
                return food.title()
        return None
    
    def _extract_adulterant_bert(self, text: str) -> Tuple[str, float]:
        """Extract adulterant using BERT zero-shot classification."""
        try:
            result = self.bert_pipelines['zero_shot'](
                text[:512],
                self.adulterants,
                multi_class=False
            )
            
            if result and result['scores'][0] > 0.3:
                return result['labels'][0].title(), float(result['scores'][0])
            else:
                # Fallback to keyword
                return self._extract_adulterant_keyword(text.lower()), 0.3
        except Exception as e:
            print(f"[NLPExtractor] BERT error in adulterant extraction: {e}")
            return self._extract_adulterant_keyword(text.lower()), 0.3
    
    def _extract_adulterant_keyword(self, text: str) -> str:
        """Extract adulterant using keyword matching (fallback)."""
        for adulterant in self.adulterants:
            if adulterant in text:
                return adulterant.title()
        return None
    
    def _estimate_severity_bert(self, text: str) -> int:
        """
        Estimate severity (1-5) using sentiment analysis + keyword weights.
        Uses BERT sentiment + explicit severity keywords.
        """
        try:
            # Get sentiment score
            sentiment = self.bert_pipelines['sentiment'](text[:512])[0]
            sentiment_score = sentiment['score']  # 0-1, higher = more negative/toxic
            
            # Combine sentiment with keyword severity
            keyword_severity = self._estimate_severity_keyword(text.lower())
            
            # Weight: 60% keyword, 40% sentiment
            if sentiment_score > 0.8:
                bert_severity = 5
            elif sentiment_score > 0.6:
                bert_severity = 4
            elif sentiment_score > 0.4:
                bert_severity = 3
            else:
                bert_severity = 2
            
            combined_severity = int(0.6 * keyword_severity + 0.4 * bert_severity)
            return max(1, min(5, combined_severity))
        
        except Exception as e:
            print(f"[NLPExtractor] BERT error in severity estimation: {e}")
            return self._estimate_severity_keyword(text.lower())
    
    def _estimate_severity_keyword(self, text: str) -> int:
        """
        Estimate severity level (1-5) based on keywords.
        5 = highly toxic (lead, melamine, pesticide, arsenic)
        4 = moderate (detergent, starch, synthetic)
        3 = low (fillers, water, sand)
        2 = default
        """
        severity_high = {
            "lead", "melamine", "pesticide", "toxic", "poison",
            "dangerous", "arsenic", "cyanide", "rat poison"
        }
        severity_medium = {
            "detergent", "starch", "synthetic", "fillers",
            "chemical", "dye", "coloring", "preservative"
        }
        severity_low = {"water", "sand", "chalk", "fillers"}
        
        if any(word in text for word in severity_high):
            return 5
        elif any(word in text for word in severity_medium):
            return 4
        elif any(word in text for word in severity_low):
            return 3
        else:
            return 2  # Default moderate


def extract_entities(text: str) -> Dict:
    """Helper function to extract entities from text using BERT."""
    extractor = NLPExtractor()
    result = extractor.extract_entities(text)
    
    # Return in legacy format with just severity (no confidence at module level)
    return {
        'city': result['city'],
        'food_item': result['food_item'],
        'adulterant': result['adulterant'],
        'severity': result['severity'],
        'nlp_confidence': result['confidence']  # For storing in database
    }
