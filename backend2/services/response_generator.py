import json
from typing import List, Dict, Any
from utils import get_greeting

class ResponseGenerator:
    """Generate contextual responses and follow-up suggestions"""
    
    def __init__(self, properties_data: List[Dict]):
        self.properties_data = properties_data
    
    def create_contextual_property_summary(self, filtered_properties: List[Dict], 
                                         conversation_context: Dict[str, Any]) -> str:
        """Create a contextual summary of filtered properties"""
        if not filtered_properties:
            return "No matching properties found."
        
        context_props = []
        user_prefs = conversation_context.get("user_preferences", {})
        
        for prop in filtered_properties:
            minimal_prop = self._create_minimal_property(prop, user_prefs)
            context_props.append(minimal_prop)
        
        return json.dumps(context_props, indent=1)
    
    def _create_minimal_property(self, prop: Dict, user_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Create a minimal property representation based on user preferences"""
        minimal_prop = {
            "name": prop.get("Building Name", ""),
            "location": prop.get("Location", ""),
            "types": prop.get("Apartment Types", ""),
            "price": prop.get("Price Range (Lakhs)", ""),
            "status": prop.get("Availability Status", ""),
            "builder": prop.get("Builder Name", ""),
            "contact": prop.get("Builder Contact", "")
        }
        
        # Add contextual information based on user preferences
        if user_prefs.get("near"):
            minimal_prop["commute_times"] = prop.get("Commute Times", "")
            minimal_prop["nearby_locations"] = prop.get("Nearby Locations", "")
        
        if user_prefs.get("amenities"):
            amenities = prop.get("Amenities", "")
            if len(amenities) > 150:
                minimal_prop["amenities"] = amenities[:150] + "..."
            else:
                minimal_prop["amenities"] = amenities
        
        return minimal_prop
    
    def generate_follow_up_suggestions(self, user_query: str, bot_response: str, 
                                     chat_history: List, conversation_context: Dict[str, Any]) -> List[str]:
        """Generate intelligent follow-up questions based on conversation context"""
        suggestions = []
        query_lower = user_query.lower()
        user_prefs = conversation_context.get("user_preferences", {})
        
        # Context-based suggestions
        suggestions.extend(self._get_context_based_suggestions(query_lower, user_prefs))
        
        # Preference-based suggestions
        suggestions.extend(self._get_preference_based_suggestions(user_prefs))
        
        # Response-based suggestions
        suggestions.extend(self._get_response_based_suggestions(query_lower, bot_response))
        
        # Add base suggestions if needed
        base_suggestions = self._get_base_suggestions()
        
        # Combine and limit suggestions
        final_suggestions = suggestions[:3]
        if len(final_suggestions) < 3:
            final_suggestions.extend(base_suggestions[:3-len(final_suggestions)])
        
        return list(dict.fromkeys(final_suggestions))[:3]  # Remove duplicates and limit to 3
    
    def _get_context_based_suggestions(self, query_lower: str, user_prefs: Dict[str, Any]) -> List[str]:
        """Get suggestions based on query context"""
        suggestions = []
        
        if 'bhk' in query_lower and not user_prefs.get("max_budget"):
            suggestions.append("What's your budget range?")
        
        if any(word in query_lower for word in ['budget', 'price', 'cost']) and not user_prefs.get("bhk"):
            suggestions.append("How many bedrooms do you need?")
        
        if 'near' in query_lower or 'close to' in query_lower:
            suggestions.extend(["Tell me about commute times", "What amenities are important to you?"])
        
        if any(word in query_lower for word in ['amenities', 'facilities', 'gym', 'pool']):
            suggestions.extend(["Compare these properties", "Show builder information"])
        
        if 'compare' in query_lower:
            suggestions.extend(["Which property has better connectivity?", "Show detailed floor plans"])
        
        return suggestions
    
    def _get_preference_based_suggestions(self, user_prefs: Dict[str, Any]) -> List[str]:
        """Get suggestions based on user preferences"""
        suggestions = []
        
        if user_prefs.get("preferred_location"):
            location = user_prefs["preferred_location"]
            suggestions.extend([
                f"Show all properties in {location}",
                f"What's special about {location} area?"
            ])
        
        if user_prefs.get("bhk"):
            bhk = user_prefs["bhk"]
            suggestions.append(f"Compare all {bhk}BHK options")
        
        return suggestions
    
    def _get_response_based_suggestions(self, query_lower: str, bot_response: str) -> List[str]:
        """Get suggestions based on bot response content"""
        suggestions = []
        
        # Check if multiple properties are mentioned in response
        property_count = len([p for p in self.properties_data if p['Building Name'] in bot_response])
        if property_count > 1:
            suggestions.extend(["Which property has better connectivity?", "Show detailed floor plans"])
        
        return suggestions
    
    def _get_base_suggestions(self) -> List[str]:
        """Get base suggestions that are always relevant"""
        return [
            "Tell me about RERA approval status",
            "What are the maintenance charges?",
            "Show virtual tour links",
            "Explain loan eligibility",
            "What documents do I need?"
        ]
    
    def build_enhanced_memory_context(self, chat_memory: List[Dict], 
                                    conversation_context: Dict[str, Any]) -> str:
        """Build memory context for AI prompt"""
        if not chat_memory:
            return ""
        
        context = "CONVERSATION MEMORY:\n"
        
        # Add user preferences if available
        if conversation_context.get("user_preferences"):
            context += "User Preferences: "
            prefs = []
            for key, value in conversation_context["user_preferences"].items():
                if isinstance(value, list):
                    prefs.append(f"{key}: {', '.join(value)}")
                elif isinstance(value, dict):
                    prefs.append(f"{key}: {value}")
                else:
                    prefs.append(f"{key}: {value}")
            context += "; ".join(prefs) + "\n\n"
        
        # Add recent chat history (last 3 exchanges)
        recent_history = chat_memory[-3:]
        for exchange in recent_history:
            context += f"User: {exchange['user']}\n"
            assistant_response = exchange['assistant']
            if len(assistant_response) > 200:
                assistant_response = assistant_response[:200] + "..."
            context += f"Assistant: {assistant_response}\n\n"
        
        return context
    
    def get_property_details(self, property_name: str) -> str:
        """Get detailed information about a specific property"""
        for prop in self.properties_data:
            if property_name.lower() in prop.get("Building Name", "").lower():
                details = f"""
{prop['Building Name']}

📍 Location: {prop['Location']}, {prop['Street Name']}
🏢 Types: {prop['Apartment Types']}
📐 Sizes: {prop['Apartment Sizes']}
💰 Price: ₹{prop['Price Range (Lakhs)']} lakhs
🎯 Status: {prop['Availability Status']}
🏗️ Builder: {prop['Builder Name']}
📞 Contact: {prop['Builder Contact']}

🏊 Amenities:
{prop.get('Amenities', 'Not specified')}

🗺️ Nearby Locations:
{prop.get('Nearby Locations', 'Not specified')}

🚗 Commute Times:
{prop.get('Commute Times', 'Not specified')}
"""
                return details.strip()

        return f"No detailed information found for '{property_name}'"
    
    def generate_greeting_response(self, total_properties: int, locations: List[str]) -> str:
        """Generate a personalized greeting response using utils function"""
        return get_greeting(total_properties, locations)