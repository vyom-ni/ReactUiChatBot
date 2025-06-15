import React, { useState, useEffect, useRef } from 'react';

const EnhancedPropertyChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [properties, setProperties] = useState([]);
  const [mapProperties, setMapProperties] = useState([]);
  const [showMap, setShowMap] = useState(true);
  const [userBehavior, setUserBehavior] = useState({});
  const [proactiveSuggestions, setProactiveSuggestions] = useState([]);
  const [nearbyPlaces, setNearbyPlaces] = useState([]);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [lastMentionedProperty, setLastMentionedProperty] = useState(null); // Track last property discussed
  const [sessionID, setSessionID] = useState(null);
  const messagesEndRef = useRef(null);
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // Load properties and initialize
  useEffect(() => {
    create_session();
    loadProperties();
    initializeWelcomeMessage();
  }, []);

  // Initialize Google Maps when properties are loaded or map is shown
  useEffect(() => {
    if (mapProperties.length > 0 && showMap) {
      if (window.google && window.google.maps) {
        setTimeout(() => {
          initializeGoogleMap();
        }, 300);
      } else {
        const checkGoogleMaps = setInterval(() => {
          if (window.google && window.google.maps) {
            clearInterval(checkGoogleMaps);
            setTimeout(() => {
              initializeGoogleMap();
            }, 300);
          }
        }, 100);
        
        setTimeout(() => clearInterval(checkGoogleMaps), 10000);
      }
    }
  }, [mapProperties, showMap]);

  const initializeWelcomeMessage = () => {
    setMessages([{
      id: 1,
      type: 'bot',
      content: `🏠 Welcome to Mangalore's Smartest Property Assistant! 

I'm an AI that learns from our conversation to help you find the perfect property. Here's what makes me special:

🤖 **Intelligent Suggestions** - I analyze your preferences and proactively suggest what you might need next
🗺️ **Location Intelligence** - I can show nearby schools, hospitals, malls around any property
📊 **Smart Filtering** - I learn what matters most to you and prioritize accordingly

**Quick Start:**
• "2BHK under 100 lakhs in Kadri"
• "Properties with swimming pool and gym"
• "Show me family-friendly properties"
• "Find schools near NorthernSky City"

What kind of property are you looking for? 😊`,
      timestamp: new Date().toLocaleTimeString(),
      proactive_suggestions: [
        "Show all available properties 🏠",
        "I'm looking for a family home 👨‍👩‍👧‍👦", 
        "Investment properties under ₹1 Cr 💰",
        "Properties near tech parks 💻"
      ]
    }]);
  };

  const loadProperties = async () => {
    try {
      const response = await fetch('http://localhost:8001/properties/list_properties');
      const data = await response.json();
      console.log('Properties loaded:', data);
      setProperties(data.properties || []);
      setMapProperties(data.map_properties || []);
      console.log('Loaded properties for map:', data.map_properties?.length || 0);
    } catch (error) {
      console.error('Error loading properties:', error);
    }
  };

  const create_session = async () => {
    try {
      const response = await fetch('http://localhost:8001/chat/create_session');
      if (response.ok) {
        const data = await response.json();
        setSessionID(data.session_id);
        console.log('New session created:', data);
        return data.session_id;
      } else {
        console.error('Error creating session:', response.statusText);
      }
    } catch (error) {
      console.error('Error creating session:', error);
    }
  }

  const initializeGoogleMap = () => {
    if (!window.google || !window.google.maps || !mapRef.current || !showMap) return;

    // Clear any existing map instance
    if (mapInstanceRef.current) {
      mapInstanceRef.current = null;
    }

    try {
      // Create map centered on Mangalore
      const map = new window.google.maps.Map(mapRef.current, {
        center: { lat: 12.9141, lng: 74.8560 },
        zoom: 12,
        styles: [
          {
            featureType: "poi",
            elementType: "labels",
            stylers: [{ visibility: "off" }]
          },
          {
            featureType: "water",
            stylers: [{ color: "#4285f4" }]
          }
        ]
      });

      mapInstanceRef.current = map;

      // Add markers for all properties
      mapProperties.forEach((property, index) => {
        if (property.lat && property.lng) {
          const marker = new window.google.maps.Marker({
            position: { lat: property.lat, lng: property.lng },
            map: map,
            title: property.name,
            icon: {
              url: `data:image/svg+xml,${encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30">
                  <path fill="#1976d2" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                  <circle cx="12" cy="9" r="2.5" fill="white"/>
                  <text x="12" y="9" text-anchor="middle" dy=".3em" font-size="8" fill="#1976d2" font-weight="bold">${index + 1}</text>
                </svg>
              `)}`,
              scaledSize: new window.google.maps.Size(30, 30)
            }
          });

          const infoWindow = new window.google.maps.InfoWindow({
            content: `
              <div style="padding: 12px; max-width: 250px; font-family: Arial;">
                <h3 style="margin: 0 0 8px 0; color: #1976d2; font-size: 16px;">${property.name}</h3>
                <p style="margin: 0 0 4px 0; color: #666; font-size: 14px;">📍 ${property.location}</p>
                <p style="margin: 0 0 4px 0; color: #059669; font-weight: bold;">💰 ₹${property.price} lakhs</p>
                <p style="margin: 0 0 8px 0; color: #666; font-size: 12px;">🏠 ${property.types}</p>
                <div style="display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap;">
                  <button onclick="window.askAboutProperty('${property.name}')" 
                    style="padding: 4px 8px; background: #1976d2; color: white; border: none; border-radius: 4px; font-size: 11px; cursor: pointer;">
                    Ask AI
                  </button>
                  <button onclick="window.findNearbyPlaces('${property.name}', 'school')" 
                    style="padding: 4px 8px; background: #059669; color: white; border: none; border-radius: 4px; font-size: 11px; cursor: pointer;">
                    Schools
                  </button>
                  <button onclick="window.findNearbyPlaces('${property.name}', 'hospital')" 
                    style="padding: 4px 8px; background: #dc2626; color: white; border: none; border-radius: 4px; font-size: 11px; cursor: pointer;">
                    Hospitals
                  </button>
                  <button onclick="window.findNearbyPlaces('${property.name}', 'mall')" 
                    style="padding: 4px 8px; background: #f59e0b; color: white; border: none; border-radius: 4px; font-size: 11px; cursor: pointer;">
                    Malls
                  </button>
                </div>
              </div>
            `
          });

          marker.addListener('click', () => {
            infoWindow.open(map, marker);
            setSelectedProperty(property);
          });
        }
      });

      // Global functions for info window buttons
      window.askAboutProperty = (propertyName) => {
        setInputValue(`Tell me about ${propertyName}`);
        setTimeout(() => sendMessage(`Tell me about ${propertyName}`), 100);
      };

      window.findNearbyPlaces = (propertyName, type) => {
        setInputValue(`Find ${type}s near ${propertyName}`);
        setTimeout(() => sendMessage(`Find ${type}s near ${propertyName}`), 100);
      };

    } catch (error) {
      console.error('Error initializing Google Maps:', error);
    }
  };

  const sendMessage = async (messageText = null) => {
    const message = messageText || inputValue;
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Track which property is being discussed
    const propertyMentioned = properties.find(prop => 
      message.toLowerCase().includes(prop["Building Name"].toLowerCase())
    );
    
    if (propertyMentioned) {
      setLastMentionedProperty(propertyMentioned["Building Name"]);
    }

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          session_id: sessionID,
        })
      });

      const data = await response.json();
      console.log('Response from server:', data);

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response,
        timestamp: new Date().toLocaleTimeString(),
        properties: data.properties || [],
        images: data.images || [],
        proactive_suggestions: data.proactive_suggestions || []
      };

      setMessages(prev => [...prev, botMessage]);
      setUserBehavior(data.user_behavior || {});
      setProactiveSuggestions(data.proactive_suggestions || []);

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: '😔 Sorry, I couldn\'t connect to the server. Make sure the backend is running!',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
    setInputValue('');
  };

  const clearChat = async () => {
    try {
      const currentSessionId = sessionID || null;
      const response = await fetch(`http://localhost:8001/chat/session/${currentSessionId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      console.log("Deleted Chat :", data);

      const newSessionId = await create_session();
      console.log('New session created:', newSessionId);
      
      setMessages([]);
      setUserBehavior({});
      setProactiveSuggestions([]);
      setNearbyPlaces([]);
      setSelectedProperty(null);
      setLastMentionedProperty(null); // Clear memory
      
      // Reinitialize welcome message
      setTimeout(() => initializeWelcomeMessage(), 500);
      
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const findNearbyPlaces = async (propertyName, placeType) => {
    try {
      // Set the property as last mentioned for context
      setLastMentionedProperty(propertyName);
      
      const response = await fetch('http://localhost:8001/properties/nearby', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          property_name: propertyName,
          place_type: placeType
        })
      });

      const data = await response.json();
      
      if (data.nearby && data.nearby.places) {
        const limitedPlaces = data.nearby.places.slice(0, 3); // Limit to 3 places
        const nearbyMessage = {
          id: Date.now(),
          type: 'bot',
          content: `🗺️ Found ${limitedPlaces.length} ${placeType}s near **${propertyName}**:\n\n${
            limitedPlaces.map((place, index) => 
              `${index + 1}. **${place.name}**\n   📍 ${place.vicinity}\n   ${place.rating ? `⭐ ${place.rating}` : ''}\n`
            ).join('\n')
          }\n💡 Need more details? Just ask me!`,
          timestamp: new Date().toLocaleTimeString(),
          proactive_suggestions: [`Find hospitals near ${propertyName}`, `Find malls near ${propertyName}`, `Tell me about commute times`]
        };
        
        setMessages(prev => [...prev, nearbyMessage]);
        setNearbyPlaces(limitedPlaces);
      }
    } catch (error) {
      console.error('Error finding nearby places:', error);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion.replace(/[🏠💰🛏️🎥🏊‍♂️🗺️🚗📅🏦📞💸😔🔍📸📍💬🤔👨‍👩‍👧‍👦💻]/g, '').trim());
    setTimeout(() => sendMessage(), 100);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Function to convert **text** to bold HTML
  const formatText = (text) => {
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  };

  const ConversationStageIndicator = () => {
    const stage = userBehavior.conversation_stage;
    const stageInfo = {
      discovery: { color: '#3b82f6', text: 'Exploring Options', icon: '🔍' },
      evaluation: { color: '#f59e0b', text: 'Comparing Properties', icon: '⚖️' },
      decision: { color: '#10b981', text: 'Ready to Decide', icon: '✅' }
    };
    
    const current = stageInfo[stage] || stageInfo.discovery;
    
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 8px',
        backgroundColor: current.color + '20',
        border: `1px solid ${current.color}40`,
        borderRadius: '12px',
        fontSize: '10px',
        color: current.color,
        fontWeight: 'bold'
      }}>
        <span>{current.icon}</span>
        <span>{current.text}</span>
      </div>
    );
  };

  const UserInsights = () => {
    if (!userBehavior.interests || userBehavior.interests.length === 0) return null;
    
    return (
      <div style={{
        backgroundColor: '#f8f9fa',
        padding: '8px 12px',
        borderRadius: '8px',
        marginBottom: '12px',
        border: '1px solid #e1e5e9'
      }}>
        <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '6px', color: '#666' }}>
          🧠 Learning about you:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
          {userBehavior.interests.slice(0, 4).map((interest, index) => (
            <span key={index} style={{
              backgroundColor: '#667eea',
              color: 'white',
              padding: '2px 6px',
              borderRadius: '10px',
              fontSize: '10px',
              textTransform: 'capitalize'
            }}>
              {interest}
            </span>
          ))}
          {userBehavior.interests.length > 4 && (
            <span style={{
              backgroundColor: '#ccc',
              color: '#666',
              padding: '2px 6px',
              borderRadius: '10px',
              fontSize: '10px'
            }}>
              +{userBehavior.interests.length - 4} more
            </span>
          )}
        </div>
        {lastMentionedProperty && (
          <div style={{ marginTop: '6px', fontSize: '10px', color: '#666' }}>
            💬 Last discussed: <strong>{lastMentionedProperty}</strong>
          </div>
        )}
      </div>
    );
  };

  const MessageComponent = ({ message }) => (
    <div style={{
      display: 'flex',
      justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
      marginBottom: '16px'
    }}>
      <div style={{
        maxWidth: '75%',
        padding: '12px 16px',
        borderRadius: '18px',
        backgroundColor: message.type === 'user' ? '#667eea' : 'white',
        color: message.type === 'user' ? 'white' : '#333',
        boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
        border: message.type === 'bot' ? '1px solid #e1e5e9' : 'none'
      }}>
        <div style={{ 
          fontSize: '11px', 
          opacity: 0.7, 
          marginBottom: '6px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{message.timestamp}</span>
          {message.type === 'bot' && userBehavior.conversation_stage && (
            <ConversationStageIndicator />
          )}
        </div>
        
        <div style={{ 
          whiteSpace: 'pre-wrap', 
          lineHeight: '1.5',
          fontSize: '14px'
        }}
        dangerouslySetInnerHTML={{ 
          __html: formatText(message.content)
        }}
        />
        
        {/* Property Images */}
        {message.images && message.images.length > 0 && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
            gap: '8px', 
            marginTop: '12px' 
          }}>
            {message.images.map((image, index) => (
              <div key={index} style={{ position: 'relative', borderRadius: '8px', overflow: 'hidden' }}>
                <img 
                  src={image} 
                  alt={`Property ${index + 1}`}
                  style={{
                    width: '100%',
                    height: '100px',
                    objectFit: 'cover',
                    cursor: 'pointer',
                    transition: 'transform 0.2s'
                  }}
                  onClick={() => window.open(image, '_blank')}
                  onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                  onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                />
                <div style={{
                  position: 'absolute',
                  top: '4px',
                  right: '4px',
                  backgroundColor: 'rgba(0,0,0,0.7)',
                  color: 'white',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  fontSize: '10px'
                }}>
                  {index + 1}/{message.images.length}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Property Cards */}
        {message.properties && message.properties.length > 0 && (
          <div style={{ marginTop: '12px' }}>
            {message.properties.slice(0, 2).map((property, index) => (
              <div key={index} style={{
                backgroundColor: message.type === 'user' ? 'rgba(255,255,255,0.1)' : '#f8f9fa',
                padding: '10px',
                borderRadius: '8px',
                marginBottom: '6px',
                border: '1px solid rgba(0,0,0,0.1)'
              }}>
                <div style={{ 
                  fontWeight: 'bold', 
                  color: message.type === 'user' ? 'white' : '#667eea', 
                  marginBottom: '4px',
                  fontSize: '13px'
                }}>
                  🏢 {property["Building Name"]}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: message.type === 'user' ? 'rgba(255,255,255,0.8)' : '#666',
                  marginBottom: '6px'
                }}>
                  📍 {property.Location} • 💰 ₹{property["Price Range (Lakhs)"]} lakhs • 🏠 {property["Apartment Types"]}
                </div>
                <div style={{ 
                  display: 'flex', 
                  gap: '6px', 
                  marginTop: '6px',
                  flexWrap: 'wrap'
                }}>
                  <button
                    onClick={() => {
                      setLastMentionedProperty(property["Building Name"]);
                      findNearbyPlaces(property["Building Name"], 'school');
                    }}
                    style={{
                      padding: '3px 6px',
                      fontSize: '9px',
                      backgroundColor: message.type === 'user' ? 'rgba(255,255,255,0.2)' : '#e3f2fd',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      color: message.type === 'user' ? 'white' : '#1976d2'
                    }}
                  >
                    🏫 Schools
                  </button>
                  <button
                    onClick={() => {
                      setLastMentionedProperty(property["Building Name"]);
                      findNearbyPlaces(property["Building Name"], 'hospital');
                    }}
                    style={{
                      padding: '3px 6px',
                      fontSize: '9px',
                      backgroundColor: message.type === 'user' ? 'rgba(255,255,255,0.2)' : '#e8f5e9',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      color: message.type === 'user' ? 'white' : '#388e3c'
                    }}
                  >
                    🏥 Hospitals
                  </button>
                  <button
                    onClick={() => {
                      setLastMentionedProperty(property["Building Name"]);
                      findNearbyPlaces(property["Building Name"], 'mall');
                    }}
                    style={{
                      padding: '3px 6px',
                      fontSize: '9px',
                      backgroundColor: message.type === 'user' ? 'rgba(255,255,255,0.2)' : '#fff3e0',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      color: message.type === 'user' ? 'white' : '#f57c00'
                    }}
                  >
                    🛒 Malls
                  </button>
                  <button
                    onClick={() => {
                      setLastMentionedProperty(property["Building Name"]);
                      setInputValue(`Tell me more details about ${property["Building Name"]}`);
                      setTimeout(() => sendMessage(), 100);
                    }}
                    style={{
                      padding: '3px 6px',
                      fontSize: '9px',
                      backgroundColor: message.type === 'user' ? 'rgba(255,255,255,0.2)' : '#f3e8ff',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      color: message.type === 'user' ? 'white' : '#7c3aed'
                    }}
                  >
                    ℹ️ Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Suggestions */}
        {(message.proactive_suggestions || proactiveSuggestions).length > 0 && (
          <div style={{ marginTop: '12px' }}>
            <div style={{ 
              fontSize: '11px', 
              marginBottom: '8px',
              color: message.type === 'user' ? 'rgba(255,255,255,0.8)' : '#666',
              fontWeight: 'bold'
            }}>
              💡 Suggestions for you:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {(message.proactive_suggestions || proactiveSuggestions).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  style={{
                    padding: '6px 10px',
                    fontSize: '11px',
                    backgroundColor: message.type === 'user' ? 'rgba(255,255,255,0.2)' : '#f0f0f0',
                    border: message.type === 'user' ? '1px solid rgba(255,255,255,0.3)' : '1px solid #ddd',
                    borderRadius: '15px',
                    cursor: 'pointer',
                    color: message.type === 'user' ? 'white' : '#333',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = message.type === 'user' ? 'rgba(255,255,255,0.3)' : '#667eea';
                    e.target.style.color = 'white';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = message.type === 'user' ? 'rgba(255,255,255,0.2)' : '#f0f0f0';
                    e.target.style.color = message.type === 'user' ? 'white' : '#333';
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div style={{ 
      height: '100%', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      padding: '20px',
      gap: '20px',
      overflow: 'hidden'
    }}>
      {/* Main Chat Container */}
      <div style={{
        flex: showMap ? '1' : '1',
        maxWidth: showMap ? '60%' : '100%',
        backgroundColor: 'white',
        borderRadius: '20px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        height: 'calc(100vh - 40px)'
      }}>
        
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '16px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexShrink: 0
        }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '20px' }}>🤖 Intelligent Real Estate AI</h1>
            <p style={{ margin: '4px 0 0 0', opacity: 0.9, fontSize: '13px' }}>
              {properties.length} properties • Learning from your preferences
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setShowMap(!showMap)}
              style={{
                padding: '6px 12px',
                backgroundColor: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
                borderRadius: '16px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '11px'
              }}
            >
              {showMap ? '🗺️ Hide Map' : '🗺️ Show Map'}
            </button>
            <button
              onClick={clearChat}
              style={{
                padding: '6px 12px',
                backgroundColor: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
                borderRadius: '16px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '11px'
              }}
            >
              🧹 New Chat
            </button>
          </div>
        </div>

        {/* User Insights */}
        <div style={{ padding: '12px 20px 0 20px', flexShrink: 0 }}>
          <UserInsights />
        </div>

        {/* Messages */}
        <div style={{
          flex: 1,
          padding: '0 20px',
          overflowY: 'auto',
          backgroundColor: '#f8f9fa',
          minHeight: 0
        }}>
          {messages.map((message) => (
            <MessageComponent key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
              <div style={{
                padding: '12px 16px',
                borderRadius: '18px',
                backgroundColor: 'white',
                boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
                border: '1px solid #e1e5e9'
              }}>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <div style={{ display: 'flex', gap: '3px' }}>
                    {[0, 0.2, 0.4].map((delay, i) => (
                      <div
                        key={i}
                        style={{
                          width: '8px',
                          height: '8px',
                          backgroundColor: '#667eea',
                          borderRadius: '50%',
                          animation: `bounce 1.4s infinite ${delay}s`
                        }}
                      />
                    ))}
                  </div>
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: '#666' }}>
                    AI is thinking...
                  </span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{
          padding: '16px 20px',
          backgroundColor: 'white',
          borderTop: '1px solid #e1e5e9',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about properties, locations, amenities... I learn from every question! 💬"
              style={{
                flex: 1,
                padding: '10px 14px',
                border: '2px solid #e1e5e9',
                borderRadius: '18px',
                outline: 'none',
                fontSize: '13px',
                resize: 'none',
                minHeight: '38px',
                maxHeight: '100px',
                fontFamily: 'inherit'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
              rows="1"
            />
            <button
              onClick={() => sendMessage()}
              disabled={!inputValue.trim() || isLoading}
              style={{
                padding: '10px 16px',
                backgroundColor: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '18px',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 'bold',
                opacity: (!inputValue.trim() || isLoading) ? 0.5 : 1,
                minWidth: '70px'
              }}
            >
              {isLoading ? '⏳' : 'Send 🚀'}
            </button>
          </div>
        </div>
      </div>

      {/* Google Maps Panel */}
      {showMap && (
        <div style={{
          width: '40%',
          backgroundColor: 'white',
          borderRadius: '20px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          height: 'calc(100vh - 40px)'
        }}>
          <div style={{
            padding: '14px 16px',
            borderBottom: '1px solid #e1e5e9',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: 'white',
            flexShrink: 0
          }}>
            <h3 style={{ margin: 0, fontSize: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🗺️ Property Locations
            </h3>
            <p style={{ margin: '3px 0 0 0', opacity: 0.9, fontSize: '11px' }}>
              {mapProperties.length} properties mapped • Click markers for details
            </p>
          </div>
          
          <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
            <div 
              ref={mapRef}
              style={{ width: '100%', height: '100%' }}
            />
            
            {!window.google && (
              <div style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#f8f9fa',
                flexDirection: 'column',
                gap: '12px'
              }}>
                <div style={{ fontSize: '48px' }}>🗺️</div>
                <div style={{ textAlign: 'center', color: '#666' }}>
                  <div style={{ fontWeight: 'bold' }}>Loading Google Maps...</div>
                  <div style={{ fontSize: '12px', marginTop: '4px' }}>
                    Make sure to add Google Maps API key to your HTML
                  </div>
                </div>
              </div>
            )}

            {selectedProperty && (
              <div style={{
                position: 'absolute',
                bottom: '12px',
                left: '12px',
                right: '12px',
                backgroundColor: 'white',
                padding: '10px',
                borderRadius: '10px',
                boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
                border: '1px solid #e1e5e9'
              }}>
                <h4 style={{ margin: '0 0 4px 0', color: '#333', fontSize: '13px' }}>
                  {selectedProperty.name}
                </h4>
                <p style={{ margin: '0 0 6px 0', fontSize: '11px', color: '#666' }}>
                  📍 {selectedProperty.location} • 💰 ₹{selectedProperty.price} lakhs
                </p>
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => {
                      setLastMentionedProperty(selectedProperty.name);
                      handleSuggestionClick(`Tell me about ${selectedProperty.name}`);
                    }}
                    style={{
                      flex: 1,
                      padding: '4px',
                      backgroundColor: '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      fontSize: '10px',
                      cursor: 'pointer'
                    }}
                  >
                    Ask AI
                  </button>
                  <button
                    onClick={() => {
                      setLastMentionedProperty(selectedProperty.name);
                      findNearbyPlaces(selectedProperty.name, 'school');
                    }}
                    style={{
                      flex: 1,
                      padding: '4px',
                      backgroundColor: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      fontSize: '10px',
                      cursor: 'pointer'
                    }}
                  >
                    Schools
                  </button>
                  <button
                    onClick={() => {
                      setLastMentionedProperty(selectedProperty.name);
                      findNearbyPlaces(selectedProperty.name, 'hospital');
                    }}
                    style={{
                      flex: 1,
                      padding: '4px',
                      backgroundColor: '#dc2626',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      fontSize: '10px',
                      cursor: 'pointer'
                    }}
                  >
                    Hospitals
                  </button>
                  <button
                    onClick={() => {
                      setLastMentionedProperty(selectedProperty.name);
                      findNearbyPlaces(selectedProperty.name, 'mall');
                    }}
                    style={{
                      flex: 1,
                      padding: '4px',
                      backgroundColor: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      fontSize: '10px',
                      cursor: 'pointer'
                    }}
                  >
                    Malls
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-8px); }
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
          width: 6px;
        }
        
        ::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb {
          background: #c1c1c1;
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: #a8a8a8;
        }
      `}</style>
    </div>
  );
};

export default EnhancedPropertyChatbot;