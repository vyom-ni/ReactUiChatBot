import logging
import os
import json
import requests
import google.generativeai as genai

from typing import List, Dict, Tuple

# Assuming these imports exist and work as intended in your project
from utils.prompt import get_prompt, get_greeting
from core.config import GEMINI_API_KEY, GOOGLE_MAPS_API_KEY

class Chatbot_Service:
    def __init__(self, properties_file="apartments.json"):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        self.properties_file = properties_file
        self.properties_data = self.load_properties()

        self.configure_gemini()

        # Initialize chat_memory as a list of dictionaries, each with 'role' and 'parts'
        self.chat_memory: List[Dict[str, str]] = []
        self.init_history()

        # Create a chat session with the model for continuous conversation
        # The history will be managed manually before sending messages to ensure the 4-turn limit
        self.chat_session = self.model.start_chat(history=self.chat_memory)


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
            self.logger.error(f"Error loading properties: {str(e)}")
            return []

    def configure_gemini(self, api_key: str = None):
        """Configure Gemini API and register tools (if any)"""
        try:
            if not api_key:
                api_key = GEMINI_API_KEY

            if not api_key:
                raise Exception("API key not found. Please set GEMINI_API_KEY in your .env file.")

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")

            self.logger.info("Gemini API configured successfully (without tools)!")

        except Exception as e:
            self.logger.error(f"Error configuring Gemini API: {str(e)}")
            raise e
        
    def init_history(self):
        """Initializes the chat history with the system prompt, not added to chat_memory directly."""
        prompt = self.get_enhanced_prompt()
        self._initial_system_prompt = {"role": "user", "parts": [prompt]}
        self._initial_model_response = {"role": "model", "parts": ["Ok. I am your property bot, ask me questions."]}

    def get_ai_response(self, user_query: str) -> Tuple[str, List[str]]:
        """
        Gets an AI response, maintaining conversation history with a limit of 4 turns.
        The initial greeting is not counted in the 4 turns.
        """
        try:
            self.chat_memory.append({"role": "user", "parts": [user_query]})

            print(len(self.chat_memory))
            if len(self.chat_memory) > 8: 
                self.chat_memory = self.chat_memory[-8:]

            current_history = [self._initial_system_prompt, self._initial_model_response] + self.chat_memory
            self.chat_session.history = current_history
            
            response = self.chat_session.send_message(user_query)
            ai_response = response.text.strip()

            if "GREETING" in ai_response:
                total_properties = len(self.properties_data)
                locations = list(set(prop['Location'] for prop in self.properties_data))
                return get_greeting(total_properties, locations), []

            self.chat_memory.append({"role": "model", "parts": [ai_response]})
            return ai_response, []
        except Exception as e:
            self.logger.error(f"Error getting AI response: {str(e)}")
            error_response = f"Sorry, I encountered an error: {str(e)}. Please try a simpler question."
            return error_response, []

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
    
    def get_enhanced_prompt(self) -> str:        
        prompt = get_prompt(self.properties_data)
        return prompt