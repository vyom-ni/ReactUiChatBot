import re
from typing import List, Dict, Any

class PropertyFilter:
    """Enhanced property filtering with context awareness"""
    
    def __init__(self, properties_data: List[Dict]):
        self.properties_data = properties_data
    
    def smart_property_filter_enhanced(self, query: str, conversation_context: Dict[str, Any]) -> List[Dict]:
        """Enhanced property filtering with context awareness"""
        query_lower = query.lower()
        filtered_properties = []
        scoring = {}
        
        for i, prop in enumerate(self.properties_data):
            score = self._calculate_property_score(prop, query_lower, conversation_context)
            
            if score > 0:
                scoring[i] = score
                filtered_properties.append(prop)
        
        if scoring:
            sorted_props = sorted(
                filtered_properties, 
                key=lambda x: scoring[self.properties_data.index(x)], 
                reverse=True
            )
            return sorted_props[:4]
        
        return filtered_properties[:4]
    
    def _calculate_property_score(self, prop: Dict, query_lower: str, conversation_context: Dict[str, Any]) -> int:
        """Calculate relevance score for a property"""
        score = 0
        user_preferences = conversation_context.get("user_preferences", {})
        
        if user_preferences.get("preferred_location"):
            pref_loc = user_preferences["preferred_location"]
            if pref_loc.lower() in prop.get("Location", "").lower():
                score += 10
        
        if user_preferences.get("bhk"):
            pref_bhk = user_preferences["bhk"]
            if f"{pref_bhk}bhk" in prop.get("Apartment Types", "").lower():
                score += 8
        
        score += self._calculate_budget_score(prop, user_preferences)
        
        if user_preferences.get("amenities"):
            pref_amenities = user_preferences["amenities"]
            prop_amenities = prop.get("Amenities", "").lower()
            for amenity in pref_amenities:
                if amenity in prop_amenities:
                    score += 3
        
        if user_preferences.get("near"):
            near_what = user_preferences["near"]
            commute_times = prop.get("Commute Times", "").lower()
            nearby_locations = prop.get("Nearby Locations", "").lower()
            
            if near_what in commute_times or near_what in nearby_locations:
                score += 12
        
        score += self._calculate_text_match_score(prop, query_lower)
        
        return score
    
    def _calculate_budget_score(self, prop: Dict, user_preferences: Dict[str, Any]) -> int:
        """Calculate budget-based score for a property"""
        score = 0
        prop_price_range = prop.get("Price Range (Lakhs)", "")
        
        if not prop_price_range:
            return score
        
        if user_preferences.get("max_budget"):
            max_budget = user_preferences["max_budget"]
            price_numbers = re.findall(r'\d+', str(prop_price_range))
            if price_numbers:
                prop_max_price = max([int(p) for p in price_numbers])
                if prop_max_price <= max_budget:
                    score += 6
        
        if user_preferences.get("budget_range"):
            budget_range = user_preferences["budget_range"]
            price_numbers = re.findall(r'\d+', str(prop_price_range))
            if price_numbers:
                prop_min_price = min([int(p) for p in price_numbers])
                prop_max_price = max([int(p) for p in price_numbers])
                
                if (prop_min_price <= budget_range["max"] and prop_max_price >= budget_range["min"]):
                    score += 6
        
        return score
    
    def _calculate_text_match_score(self, prop: Dict, query_lower: str) -> int:
        score = 0
        searchable_text = f"{prop.get('Building Name', '')} {prop.get('Location', '')} {prop.get('Apartment Types', '')} {prop.get('Amenities', '')}".lower()
        
        query_words = [word for word in query_lower.split() if len(word) > 2]
        for word in query_words:
            if word in searchable_text:
                score += 1
        
        return score