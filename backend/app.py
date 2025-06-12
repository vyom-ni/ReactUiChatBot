from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import google.generativeai as genai
import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow React to connect

class IntelligentPropertyChatbot:
    def __init__(self):
        print("🤖 Initializing Intelligent Property Chatbot...")
        self.properties_data = self.load_properties()
        self.chat_memory = []
        self.user_behavior = {
            "interests": [],
            "search_pattern": [],
            "viewed_properties": [],
            "preference_score": {},
            "conversation_stage": "discovery"  # discovery, evaluation, decision
        }
        self.setup_gemini()
    
    def load_properties(self):
        """Load properties from JSON file"""
        try:
            with open("backend\\apartments.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"✅ Loaded {len(data)} properties successfully")
                return data
        except Exception as e:
            print(f"❌ Error loading properties: {e}")
            return []
    
    def setup_gemini(self):
        """Setup Gemini AI"""
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Gemini AI configured successfully")
        else:
            print("❌ Please add GEMINI_API_KEY to your .env file")
    
    def analyze_user_behavior(self, query):
        """Analyze user behavior patterns for intelligent suggestions"""
        query_lower = query.lower()
        
        # Track interests
        interest_keywords = {
            'budget': ['budget', 'price', 'cost', 'lakh', 'affordable', 'expensive'],
            'location': ['location', 'area', 'near', 'close to', 'kadri', 'bejai', 'mangalore'],
            'amenities': ['gym', 'pool', 'swimming', 'parking', 'security', 'clubhouse', 'playground'],
            'size': ['bhk', 'sqft', 'size', 'spacious', 'big', 'small'],
            'connectivity': ['airport', 'railway', 'bus', 'transport', 'commute', 'travel'],
            'investment': ['investment', 'resale', 'appreciation', 'returns', 'future'],
            'family': ['family', 'children', 'kids', 'school', 'education', 'safe'],
            'lifestyle': ['modern', 'luxury', 'premium', 'lifestyle', 'comfort']
        }
        
        for category, keywords in interest_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if category not in self.user_behavior['interests']:
                    self.user_behavior['interests'].append(category)
                
                # Increase preference score
                self.user_behavior['preference_score'][category] = \
                    self.user_behavior['preference_score'].get(category, 0) + 1
        
        # Track search pattern
        self.user_behavior['search_pattern'].append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'interests_detected': [cat for cat, keywords in interest_keywords.items() 
                                 if any(keyword in query_lower for keyword in keywords)]
        })
        
        # Determine conversation stage
        self.update_conversation_stage(query_lower)
    
    def update_conversation_stage(self, query_lower):
        """Update conversation stage based on user queries"""
        if any(word in query_lower for word in ['show', 'tell me about', 'details', 'info']):
            if len(self.user_behavior['viewed_properties']) > 2:
                self.user_behavior['conversation_stage'] = 'evaluation'
            else:
                self.user_behavior['conversation_stage'] = 'discovery'
        
        if any(word in query_lower for word in ['compare', 'vs', 'better', 'difference']):
            self.user_behavior['conversation_stage'] = 'evaluation'
        
        if any(word in query_lower for word in ['contact', 'visit', 'schedule', 'buy', 'book']):
            self.user_behavior['conversation_stage'] = 'decision'
    
    def generate_proactive_suggestions(self):
        """Generate intelligent proactive suggestions based on user behavior"""
        suggestions = []
        stage = self.user_behavior['conversation_stage']
        interests = self.user_behavior['interests']
        preference_scores = self.user_behavior['preference_score']
        
        # Stage-based suggestions
        if stage == 'discovery':
            if 'budget' in interests and 'location' not in interests:
                suggestions.append("🗺️ Which area in Mangalore interests you most?")
            
            if 'location' in interests and 'amenities' not in interests:
                suggestions.append("🏊‍♂️ What amenities are important to you? (gym, pool, etc.)")
            
            if len(interests) >= 2 and 'size' not in interests:
                suggestions.append("🏠 How many bedrooms do you need?")
        
        elif stage == 'evaluation':
            suggestions.append("⚖️ Would you like me to compare your shortlisted properties?")
            suggestions.append("📊 Show me pros and cons of each property")
            
            if 'connectivity' in interests:
                suggestions.append("🚗 Check commute times from these properties")
        
        elif stage == 'decision':
            suggestions.append("📅 Schedule a property visit")
            suggestions.append("💰 Check loan eligibility and EMI calculator")
            suggestions.append("📋 What documents do I need for booking?")
        
        # Interest-based suggestions
        top_interests = sorted(preference_scores.items(), key=lambda x: x[1], reverse=True)[:2]
        
        for interest, score in top_interests:
            if interest == 'family' and score >= 2:
                suggestions.append("🏫 Find nearby schools and hospitals")
            elif interest == 'investment' and score >= 2:
                suggestions.append("📈 Show me properties with best appreciation potential")
            elif interest == 'amenities' and score >= 2:
                suggestions.append("🎯 Filter properties by specific amenities")
        
        # Remove duplicates and limit to 4
        return list(dict.fromkeys(suggestions))[:4]
    
    def find_properties(self, query):
        """Enhanced property search with learning"""
        query_lower = query.lower()
        matched_properties = []
        
        # Analyze user behavior
        self.analyze_user_behavior(query)
        
        for prop in self.properties_data:
            score = 0
            
            # Enhanced scoring based on user behavior
            for interest in self.user_behavior['interests']:
                if interest == 'budget':
                    budget_match = re.search(r'(\d+)\s*lakh', query_lower)
                    if budget_match:
                        budget = int(budget_match.group(1))
                        price_range = prop.get("Price Range (Lakhs)", "")
                        prices = re.findall(r'\d+', price_range)
                        if prices and int(prices[-1]) <= budget:
                            score += 15  # Higher weight for budget match
                
                elif interest == 'location':
                    if prop.get("Location", "").lower() in query_lower:
                        score += 12
                
                elif interest == 'amenities':
                    amenities = ['gym', 'pool', 'swimming', 'parking', 'security', 'clubhouse']
                    for amenity in amenities:
                        if amenity in query_lower and amenity in prop.get("Amenities", "").lower():
                            score += 8
            
            # BHK matching
            bhk_match = re.search(r'(\d+)\s*bhk', query_lower)
            if bhk_match and bhk_match.group(1) in prop.get("Apartment Types", "").lower():
                score += 10
            
            # General keyword matching
            searchable_text = f"{prop.get('Building Name', '')} {prop.get('Location', '')} {prop.get('Apartment Types', '')} {prop.get('Amenities', '')}".lower()
            query_words = [word for word in query_lower.split() if len(word) > 2]
            for word in query_words:
                if word in searchable_text:
                    score += 2
            
            if score > 0:
                matched_properties.append((prop, score))
        
        # Sort by score and return top matches
        matched_properties.sort(key=lambda x: x[1], reverse=True)
        result_properties = [prop[0] for prop in matched_properties[:4]]
        
        # Track viewed properties
        for prop in result_properties:
            prop_name = prop.get('Building Name', '')
            if prop_name not in self.user_behavior['viewed_properties']:
                self.user_behavior['viewed_properties'].append(prop_name)
        
        return result_properties
    
    def find_nearby_places(self, lat, lng, place_type="school", radius=2000):
        """Find nearby places using Google Places API"""
        google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
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
    
    def create_intelligent_response(self, query, properties):
        """Create intelligent AI response with context awareness"""
        if not hasattr(self, 'model'):
            return "⚠️ Gemini AI is not configured. Please check your API key! 😊"
        
        # Get user behavior insights
        behavior_context = f"""
User Behavior Analysis:
- Interests: {', '.join(self.user_behavior['interests'])}
- Conversation Stage: {self.user_behavior['conversation_stage']}
- Properties Viewed: {len(self.user_behavior['viewed_properties'])}
- Top Preferences: {dict(list(sorted(self.user_behavior['preference_score'].items(), key=lambda x: x[1], reverse=True))[:3])}
"""
        
        # Create comprehensive prompt
        properties_text = ""
        if properties:
            for i, prop in enumerate(properties, 1):
                properties_text += f"""
{i}. **{prop.get('Building Name', 'Unknown')}** 🏢
   📍 {prop.get('Location', 'N/A')} • 💰 ₹{prop.get('Price Range (Lakhs)', 'N/A')} lakhs
   🏠 {prop.get('Apartment Types', 'N/A')} • ✅ {prop.get('Availability Status', 'N/A')}
   📞 {prop.get('Builder Contact', 'N/A')}
"""
        
        prompt = f"""
You are an intelligent real estate assistant for Mangalore properties with advanced conversational AI capabilities.

USER QUERY: {query}

{behavior_context}

RELEVANT PROPERTIES:
{properties_text if properties else "No specific properties found for this query."}

INSTRUCTIONS:
- Be conversational, helpful, and use emojis naturally
- Keep responses concise (2-3 sentences max for basic queries)
- Only show essential details unless user asks for more specifics
- For location queries, mention you can find nearby schools/hospitals/malls
- Reference user's interests when relevant but don't overwhelm
- Let users ask for additional details rather than providing everything at once
- Be proactive but not pushy

CONVERSATION GUIDELINES:
- Discovery: Help explore options, ask clarifying questions
- Evaluation: Highlight key differences, suggest comparisons  
- Decision: Guide toward contact/visits

Keep it friendly, concise, and focused on what they actually asked! 🤖✨
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            return f"I found some great properties for you! 😊 {properties_text if properties else 'Let me help you find the perfect property.'}"
    
    def clear_memory(self):
        """Clear all chat memory and user behavior data"""
        self.chat_memory = []
        self.user_behavior = {
            "interests": [],
            "search_pattern": [],
            "viewed_properties": [],
            "preference_score": {},
            "conversation_stage": "discovery"
        }
        print("🧹 Chat memory and user behavior data cleared")
    
    def get_chat_summary(self):
        """Get summary of current chat session"""
        return {
            "total_messages": len(self.chat_memory),
            "properties_viewed": len(self.user_behavior['viewed_properties']),
            "user_interests": self.user_behavior['interests'],
            "conversation_stage": self.user_behavior['conversation_stage'],
            "preference_scores": self.user_behavior['preference_score']
        }

# Create chatbot instance
chatbot = IntelligentPropertyChatbot()

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 Intelligent Property Chatbot API is running!",
        "properties_loaded": len(chatbot.properties_data),
        "features": [
            "Intelligent conversation analysis",
            "Proactive suggestions",
            "Google Maps integration",
            "Nearby places finder",
            "User behavior tracking"
        ]
    })

@app.route('/api/properties', methods=['GET'])
def get_all_properties():
    """Get all properties with coordinates for map display"""
    properties_with_coords = []
    for prop in chatbot.properties_data:
        if prop.get('Latitude') and prop.get('Longitude'):
            properties_with_coords.append({
                'id': len(properties_with_coords) + 1,
                'name': prop.get('Building Name'),
                'location': prop.get('Location'),
                'lat': prop.get('Latitude'),
                'lng': prop.get('Longitude'),
                'price': prop.get('Price Range (Lakhs)'),
                'types': prop.get('Apartment Types'),
                'amenities': prop.get('Amenities'),
                'contact': prop.get('Builder Contact'),
                'builder': prop.get('Builder Name'),
                'status': prop.get('Availability Status')
            })
    
    return jsonify({
        "properties": chatbot.properties_data,
        "map_properties": properties_with_coords,
        "count": len(chatbot.properties_data)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with intelligence"""
    try:
        data = request.get_json()
        user_query = data.get('message', '')
        
        if not user_query:
            return jsonify({"error": "No message provided"}), 400
        
        print(f"💬 User: {user_query}")
        
        # Find relevant properties
        relevant_properties = chatbot.find_properties(user_query)
        
        # Generate intelligent response
        bot_response = chatbot.create_intelligent_response(user_query, relevant_properties)
        
        # Generate proactive suggestions
        proactive_suggestions = chatbot.generate_proactive_suggestions()
        
        # Extract images if user asks for them
        images = []
        if any(word in user_query.lower() for word in ['image', 'photo', 'picture', 'show']):
            for prop in relevant_properties:
                if prop.get("Building Photo URL"):
                    images.append(prop["Building Photo URL"])
        
        # Save to memory
        chatbot.chat_memory.append({
            "user": user_query,
            "bot": bot_response,
            "properties": relevant_properties,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"🤖 Bot: {bot_response[:100]}...")
        
        return jsonify({
            "response": bot_response,
            "properties": relevant_properties,
            "images": images,
            "proactive_suggestions": proactive_suggestions,
            "user_behavior": chatbot.user_behavior,
            "chat_summary": chatbot.get_chat_summary()
        })
        
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        return jsonify({"error": f"Error: {e}"}), 500

@app.route('/api/nearby', methods=['POST'])
def find_nearby():
    """Find nearby places for a property"""
    try:
        data = request.get_json()
        property_name = data.get('property_name', '')
        place_type = data.get('place_type', 'school')
        
        # Find the property
        target_property = None
        for prop in chatbot.properties_data:
            if property_name.lower() in prop.get('Building Name', '').lower():
                target_property = prop
                break
        
        if not target_property:
            return jsonify({"error": "Property not found"}), 404
        
        lat = target_property.get('Latitude')
        lng = target_property.get('Longitude')
        
        if not lat or not lng:
            return jsonify({"error": "Property coordinates not available"}), 400
        
        # Find nearby places
        nearby_result = chatbot.find_nearby_places(lat, lng, place_type)
        
        return jsonify({
            "property": {
                "name": target_property.get('Building Name'),
                "location": target_property.get('Location'),
                "coordinates": {"lat": lat, "lng": lng}
            },
            "place_type": place_type,
            "nearby": nearby_result
        })
        
    except Exception as e:
        print(f"❌ Error finding nearby places: {e}")
        return jsonify({"error": f"Error: {e}"}), 500

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    """Clear chat memory and user behavior"""
    try:
        chatbot.clear_memory()
        return jsonify({
            "message": "🧹 Chat memory cleared successfully!",
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": f"Error clearing chat: {e}"}), 500

@app.route('/api/user-insights', methods=['GET'])
def get_user_insights():
    """Get detailed user behavior insights"""
    return jsonify({
        "behavior": chatbot.user_behavior,
        "chat_summary": chatbot.get_chat_summary(),
        "memory_size": len(chatbot.chat_memory)
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 INTELLIGENT PROPERTY CHATBOT STARTING")
    print("="*60)
    print(f"📊 Properties loaded: {len(chatbot.properties_data)}")
    print(f"🤖 Gemini AI: {'✅ Ready' if hasattr(chatbot, 'model') else '❌ Not configured'}")
    print(f"🗺️ Google Maps: {'✅ Ready' if os.getenv('GOOGLE_MAPS_API_KEY') else '❌ API key needed'}")
    print("\n🌟 New Features:")
    print("   • Intelligent conversation analysis")
    print("   • Proactive suggestions based on user behavior")
    print("   • Google Maps integration for nearby places")
    print("   • Enhanced property search with learning")
    print("   • Clear chat functionality")
    print("\n🌐 API Endpoints:")
    print("   • http://localhost:8000/api/chat (enhanced chat)")
    print("   • http://localhost:8000/api/nearby (find nearby places)")
    print("   • http://localhost:8000/api/clear-chat (clear memory)")
    print("   • http://localhost:8000/api/user-insights (behavior analysis)")
    print("="*60)
    print()
    
    app.run(debug=True, port=8000)