import re
from typing import Dict, List, Any

class PreferenceExtractor:
    """Extract and manage user preferences from queries and chat history"""
    
    def __init__(self, properties_data: List[Dict]):
        self.properties_data = properties_data
        self._setup_location_keywords()
    
    def _setup_location_keywords(self):
        """Setup location-based keywords mapping"""
        self.location_keywords = {
            'airport': ['airport', 'mangalore airport'],
            'school': ['school', 'schools', 'education'],
            'hospital': ['hospital', 'medical', 'healthcare'],
            'mall': ['mall', 'shopping', 'market'],
            'beach': ['beach', 'seaside', 'coast'],
            'railway': ['railway', 'train', 'station'],
            'college': ['college', 'university']
        }
        
        self.amenity_keywords = [
            'gym', 'pool', 'swimming', 'parking', 'garden', 
            'playground', 'security', 'elevator', 'lift'
        ]
    
    def extract_user_preferences(self, query: str, conversation_context: Dict[str, Any], 
                               chat_history: List = None) -> Dict[str, Any]:
        """Extract and update user preferences from query and chat history"""
        query_lower = query.lower()
        user_preferences = conversation_context.get("user_preferences", {})
        self._extract_bhk_preference(query_lower, user_preferences)
        self._extract_budget_preferences(query_lower, user_preferences)
        self._extract_location_preferences(query_lower, user_preferences)
        self._extract_proximity_preferences(query_lower, user_preferences)
        self._extract_amenity_preferences(query_lower, user_preferences)
        
        conversation_context["user_preferences"] = user_preferences
        return user_preferences
    
    def _extract_bhk_preference(self, query_lower: str, user_preferences: Dict[str, Any]):
        """Extract BHK preference from query"""
        bhk_match = re.search(r'(\d+)\s*bhk', query_lower)
        if bhk_match:
            user_preferences["bhk"] = bhk_match.group(1)
    
    def _extract_budget_preferences(self, query_lower: str, user_preferences: Dict[str, Any]):
        """Extract budget preferences from query"""
        budget_match = re.search(r'(?:under|below|within|max|maximum)\s*(\d+)\s*(?:lakh|lakhs|l)', query_lower)
        if budget_match:
            user_preferences["max_budget"] = int(budget_match.group(1))
        budget_range = re.search(r'(\d+)[-\s]*(?:to|-)?\s*(\d+)\s*(?:lakh|lakhs|l)', query_lower)
        if budget_range:
            user_preferences["budget_range"] = {
                "min": int(budget_range.group(1)),
                "max": int(budget_range.group(2))
            }
        
        single_budget = re.search(r'(?:budget|price).*?(\d+)\s*(?:lakh|lakhs|l)', query_lower)
        if single_budget and not user_preferences.get("max_budget") and not user_preferences.get("budget_range"):
            user_preferences["max_budget"] = int(single_budget.group(1))
    
    def _extract_location_preferences(self, query_lower: str, user_preferences: Dict[str, Any]):
        """Extract location preferences from query"""
        locations = [prop['Location'] for prop in self.properties_data]
        for location in locations:
            if location.lower() in query_lower:
                user_preferences["preferred_location"] = location
                break
    
    def _extract_proximity_preferences(self, query_lower: str, user_preferences: Dict[str, Any]):
        for key, keywords in self.location_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                user_preferences["near"] = key
                break
    
    def _extract_amenity_preferences(self, query_lower: str, user_preferences: Dict[str, Any]):
        """Extract amenity preferences from query"""
        preferred_amenities = [amenity for amenity in self.amenity_keywords if amenity in query_lower]
        if preferred_amenities:
            existing_amenities = user_preferences.get("amenities", [])
            all_amenities = list(set(existing_amenities + preferred_amenities))
            user_preferences["amenities"] = all_amenities
    
    def get_user_preferences_summary(self, conversation_context: Dict[str, Any]) -> str:
        """Generate a readable summary of user preferences"""
        user_prefs = conversation_context.get("user_preferences", {})
        if not user_prefs:
            return "No specific preferences identified yet."
        
        summary_parts = []
        
        if user_prefs.get("bhk"):
            summary_parts.append(f"Looking for {user_prefs['bhk']}BHK")
        
        if user_prefs.get("max_budget"):
            summary_parts.append(f"Budget under ₹{user_prefs['max_budget']} lakhs")
        
        if user_prefs.get("budget_range"):
            br = user_prefs["budget_range"]
            summary_parts.append(f"Budget ₹{br['min']}-{br['max']} lakhs")
        
        if user_prefs.get("preferred_location"):
            summary_parts.append(f"Preferred location: {user_prefs['preferred_location']}")
        
        if user_prefs.get("near"):
            summary_parts.append(f"Near {user_prefs['near']}")
        
        if user_prefs.get("amenities"):
            amenities_str = ", ".join(user_prefs["amenities"])
            summary_parts.append(f"Important amenities: {amenities_str}")
        
        return "; ".join(summary_parts)
    
    def clear_preferences(self, conversation_context: Dict[str, Any]):
        """Clear all user preferences"""
        conversation_context["user_preferences"] = {}
    
    def update_preference(self, conversation_context: Dict[str, Any], 
                         preference_key: str, preference_value: Any):
        """Update a specific preference"""
        if "user_preferences" not in conversation_context:
            conversation_context["user_preferences"] = {}
        
        conversation_context["user_preferences"][preference_key] = preference_value 