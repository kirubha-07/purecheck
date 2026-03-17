import re
from typing import Dict, Tuple


class NLPExtractor:
    """
    Extract food adulteration entities from unstructured text.
    Uses keyword matching as fallback (no model required for MVP).
    """
    
    def __init__(self):
        """Initialize keyword dictionaries."""
        self.foods = {
            "milk", "rice", "oil", "ghee", "turmeric", "chilli",
            "paneer", "sweets", "vegetables", "fruits", "water",
            "honey", "dal", "flour", "sugar", "salt", "spices",
            "butter", "cheese", "yogurt", "tea", "coffee"
        }
        
        self.adulterants = {
            "detergent", "starch", "synthetic color", "pesticide",
            "chalk powder", "water", "urea", "vanaspati",
            "metanil yellow", "lead chromate", "calcium carbonate",
            "melamine", "plastic", "sand", "fillers", "microbial"
        }
        
        self.cities = {
            "trichy", "coimbatore", "chennai", "madurai", "salem",
            "bangalore", "delhi", "mumbai", "kolkata", "pune",
            "hyderabad", "ahmedabad", "jaipur", "lucknow", "chandigarh"
        }
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extract city, food_item, adulterant, severity from raw text.
        
        Args:
            text: Raw text to extract from
        
        Returns:
            Dict with keys: city, food_item, adulterant, severity
        """
        text_lower = text.lower()
        
        # Extract city
        city = self._extract_city(text_lower)
        
        # Extract food item
        food_item = self._extract_food(text_lower)
        
        # Extract adulterant
        adulterant = self._extract_adulterant(text_lower)
        
        # Estimate severity (0-5)
        severity = self._estimate_severity(text_lower)
        
        return {
            'city': city or 'Unknown',
            'food_item': food_item or 'Unknown',
            'adulterant': adulterant or 'Unknown',
            'severity': severity
        }
    
    def _extract_city(self, text: str) -> str:
        """Extract city name from text."""
        for city in self.cities:
            if city in text:
                return city.title()
        return None
    
    def _extract_food(self, text: str) -> str:
        """Extract food item from text."""
        for food in self.foods:
            if food in text:
                return food.title()
        return None
    
    def _extract_adulterant(self, text: str) -> str:
        """Extract adulterant from text."""
        for adulterant in self.adulterants:
            if adulterant in text:
                return adulterant.title()
        return None
    
    def _estimate_severity(self, text: str) -> int:
        """
        Estimate severity level (1-5) based on keywords.
        5 = highly toxic (lead, melamine, pesticide)
        4 = moderate (detergent, starch)
        3 = low (fillers, water)
        """
        severity_high = {"lead", "melamine", "pesticide", "toxic", "poison", "dangerous"}
        severity_medium = {"detergent", "starch", "synthetic", "fillers"}
        severity_low = {"water", "sand", "chalk"}
        
        if any(word in text for word in severity_high):
            return 5
        elif any(word in text for word in severity_medium):
            return 4
        elif any(word in text for word in severity_low):
            return 3
        else:
            return 2  # Default moderate


def extract_entities(text: str) -> Dict:
    """Helper function to extract entities from text."""
    extractor = NLPExtractor()
    return extractor.extract_entities(text)
