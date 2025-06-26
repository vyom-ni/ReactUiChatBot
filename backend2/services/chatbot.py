import json
import google.generativeai as genai
import os
import logging
from typing import List, Dict, Tuple
from logging import basicConfig, INFO,Logger
from services.property_filter import PropertyFilter
from services.preference_extractor import PreferenceExtractor
from services.response_generator import ResponseGenerator
from utils.utils import get_prompt, get_greeting
import logging
from config import GEMINI_API_KEY, GOOGLE_MAPS_API_KEY
from logging import Logger as logger
import requests

class EnhancedPropertyChatbot:
    def __init__(self, properties_file="apartments.json"):
        self.logger = logging.getLogger(__name__)  
        self.properties_file = properties_file
        self.properties_data = self.load_properties()
        
        # Initialize modular components
        self.property_filter = PropertyFilter(self.properties_data)
        self.preference_extractor = PreferenceExtractor(self.properties_data)
        self.response_generator = ResponseGenerator(self.properties_data)
        
        # Initialize conversation state
        self.conversation_context = {
            "user_preferences": {},
            "mentioned_properties": [],
            "search_history": [],
            "current_focus": None
        }
        self.chat_memory = []
        self.logger = logging.getLogger(__name__)
        self.configure_gemini()

    def load_properties(self) -> List[Dict]:
        """Load properties from JSON file"""
        try:
            if os.path.exists(self.properties_file):
                with open(self.properties_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                self.logger.error(f"Properties file '{self.properties_file}' not found!")
                return []
        except Exception as e:
            self.logger(f"Error loading properties: {str(e)}")
            return []
        
    def configure_gemini(self, api_key: str = None):
        """Configure Gemini API"""
        try:
            if not api_key:
                api_key = GEMINI_API_KEY 
            
            if not api_key:
                raise Exception("API key not found. Please set GEMINI_API_KEY in your .env file.")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.logger.info("Gemini API configured successfully!")
            
        except Exception as e:
            self.logger.error(f"Error configuring Gemini API: {str(e)}")
            raise e
    
    def is_greeting(self, user_query: str) -> bool:
        """Check if user query is a greeting"""
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste', 'hola']
        return any(greeting in user_query.lower().strip() for greeting in greetings)
    
    def reset_conversation(self):
        """Reset conversation context and memory"""
        self.conversation_context = {
            "user_preferences": {},
            "mentioned_properties": [],
            "search_history": [],
            "current_focus": None
        }
        self.chat_memory = []
    
    def get_greeting_response(self) -> str:
        """Generate a brief personalized greeting response using utils"""
        total_properties = len(self.properties_data)
        locations = list(set(prop['Location'] for prop in self.properties_data))
        greeting = get_greeting(total_properties, locations)
        return greeting
    
    def generate_enhanced_prompt(self, user_query: str, filtered_properties: List[Dict]) -> str:
        property_context = self.response_generator.create_contextual_property_summary(
            filtered_properties, self.conversation_context
        )
        memory_context = self.response_generator.build_enhanced_memory_context(
            self.chat_memory, self.conversation_context
        )
        
        total_properties = len(self.properties_data)
        locations = list(set(prop['Location'] for prop in self.properties_data))
        
        prompt = get_prompt(user_query, property_context, memory_context, total_properties, locations)
        return prompt
    
    def get_ai_response(self, user_query: str) -> Tuple[str, List[str]]:
        try:
            if self.is_greeting(user_query):
                self.reset_conversation()
                greeting_response = self.get_greeting_response() 
                suggestions = self.response_generator.generate_follow_up_suggestions(
                    user_query, greeting_response, [], self.conversation_context
                )
                return greeting_response, suggestions
            
            self.preference_extractor.extract_user_preferences(
                user_query, self.conversation_context, self.chat_memory
            )
            
            filtered_properties = self.property_filter.smart_property_filter_enhanced(
                user_query, self.conversation_context
            )
            
            prompt = self.generate_enhanced_prompt(user_query, filtered_properties)
            response = self.model.generate_content(prompt)
            formatted_response = response.text
            
            suggestions = self.response_generator.generate_follow_up_suggestions(
                user_query, formatted_response, self.chat_memory, self.conversation_context
            )
            
            self.chat_memory.append({"user": user_query, "assistant": formatted_response})
            
            for prop in filtered_properties:
                prop_name = prop['Building Name']
                if prop_name not in self.conversation_context["mentioned_properties"]:
                    self.conversation_context["mentioned_properties"].append(prop_name)
            
            return formatted_response, suggestions
            
        except Exception as e:
            self.logger.error(f"Error getting AI response: {str(e)}")
            error_response = f"Sorry, I encountered an error: {str(e)}. Please try a simpler question."
            return error_response, []
    
    def get_property_details(self, property_name: str) -> str:
        """Get detailed information about a specific property"""
        return self.response_generator.get_property_details(property_name)
    
    def get_user_preferences_summary(self) -> str:
        """Get a summary of current user preferences"""
        return self.preference_extractor.get_user_preferences_summary(self.conversation_context)
    
    def clear_user_preferences(self):
        """Clear all user preferences"""
        self.preference_extractor.clear_preferences(self.conversation_context)
    
    def update_user_preference(self, preference_key: str, preference_value):
        """Update a specific user preference"""
        self.preference_extractor.update_preference(
            self.conversation_context, preference_key, preference_value
        )
    
    def get_conversation_stats(self) -> Dict[str, any]:
        """Get conversation statistics"""
        return {
            "total_messages": len(self.chat_memory),
            "mentioned_properties": len(self.conversation_context.get("mentioned_properties", [])),
            "user_preferences": self.conversation_context.get("user_preferences", {}),
            "properties_in_database": len(self.properties_data)
        }
    
    def find_nearby_places(self, lat, lng, place_type="school", radius=2000):
        """Find nearby places using Google Places API"""
        google_api_key = GOOGLE_MAPS_API_KEY
        if not google_api_key:
            return {"error": "Google Maps API key not configured"}
        
        # Map common requests to Google Places types
        type_mapping = {
            'school': 'school',
            'hospital': 'hospital',
            'mall': 'shopping_mall',
            'shopping': 'shopping_mall',
            'restaurant': 'restaurant',
            'bank': 'bank',
            'pharmacy': 'pharmacy',
            'gym': 'gym',
            'park': 'park',
            'airport': 'airport',
            'bus': 'bus_station',
            'railway': 'train_station',
            'temple': 'hindu_temple',
            'church': 'church',
            'mosque': 'mosque'
        }
        
        google_type = type_mapping.get(place_type.lower(), place_type)
        
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': google_type,
            'key': google_api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('status') == 'OK':
                places = []
                for place in data.get('results', [])[:8]:  # Limit to 8 results
                    place_info = {
                        'name': place.get('name'),
                        'vicinity': place.get('vicinity'),
                        'rating': place.get('rating'),
                        'types': place.get('types', []),
                        'location': place.get('geometry', {}).get('location', {}),
                        'price_level': place.get('price_level'),
                        'photos': place.get('photos', [])
                    }
                    places.append(place_info)
                
                return {"places": places, "count": len(places)}
            else:
                return {"error": f"Google Places API error: {data.get('status')}"}
        
        except Exception as e:
            return {"error": f"Error calling Google Places API: {str(e)}"}


def smart_property_filter_enhanced(query: str, properties_data: List[Dict]) -> List[Dict]:
    conversation_context = {"user_preferences": {}}
    
    temp_extractor = PreferenceExtractor(properties_data)
    temp_extractor.extract_user_preferences(query, conversation_context)
    
    temp_filter = PropertyFilter(properties_data)
    return temp_filter.smart_property_filter_enhanced(query, conversation_context)