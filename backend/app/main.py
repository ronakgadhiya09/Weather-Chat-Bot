from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import logging
import re
from pathlib import Path
from dotenv import load_dotenv
import json
from pydantic import BaseModel
from openai import OpenAI
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
base_dir = Path(__file__).resolve().parent.parent
env_path = os.path.join(base_dir, "config.env")
load_dotenv(env_path)

# Log environment setup
logger.info(f"Loading environment from: {env_path}")
logger.info(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")
logger.info(f"OpenWeather API Key set: {'Yes' if os.environ.get('OPENWEATHER_API_KEY') else 'No'}")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Activity database with requirements
ACTIVITIES = {
    "cricket": {
        "optimal_temp": (20, 35),
        "max_wind": 15,
        "precipitation_tolerance": 0,
        "humidity_preference": "moderate",
        "time_requirements": ["daylight", "evening_suitable"],
        "outdoor": True,
        "category": "sports"
    },
    "football": {
        "optimal_temp": (15, 30),
        "max_wind": 20,
        "precipitation_tolerance": 5,
        "humidity_preference": "moderate",
        "time_requirements": ["daylight", "evening_suitable"],
        "outdoor": True,
        "category": "sports"
    },
    "running": {
        "optimal_temp": (10, 25),
        "max_wind": 25,
        "precipitation_tolerance": 0,
        "humidity_preference": "low",
        "time_requirements": ["any"],
        "outdoor": True,
        "category": "fitness"
    },
    "cycling": {
        "optimal_temp": (15, 30),
        "max_wind": 20,
        "precipitation_tolerance": 0,
        "humidity_preference": "moderate",
        "time_requirements": ["daylight"],
        "outdoor": True,
        "category": "fitness"
    },
    "walking": {
        "optimal_temp": (10, 35),
        "max_wind": 30,
        "precipitation_tolerance": 10,
        "humidity_preference": "any",
        "time_requirements": ["any"],
        "outdoor": True,
        "category": "leisure"
    },
    "picnic": {
        "optimal_temp": (20, 30),
        "max_wind": 15,
        "precipitation_tolerance": 0,
        "humidity_preference": "low",
        "time_requirements": ["daylight"],
        "outdoor": True,
        "category": "leisure"
    },
    "shopping": {
        "optimal_temp": (-10, 45),
        "max_wind": 100,
        "precipitation_tolerance": 100,
        "humidity_preference": "any",
        "time_requirements": ["any"],
        "outdoor": False,
        "category": "indoor"
    }
}

# Query type classification
QUERY_TYPES = {
    "BASIC_WEATHER": ["weather", "temperature", "temp", "hot", "cold", "raining", "sunny"],
    "ACTIVITY_PLANNING": ["play", "go", "do", "can i", "should i", "good for", "suitable"],
    "CLOTHING_ADVICE": ["wear", "dress", "clothing", "clothes", "outfit"],
    "TRAVEL_PLANNING": ["visit", "travel", "trip", "vacation", "holiday"],
    "COMFORT_ASSESSMENT": ["comfortable", "pleasant", "nice", "good weather", "bad weather"]
}

# Common city names
COMMON_CITIES = [
    "Tokyo", "New York", "London", "Paris", "Sydney", "Berlin", "Rome", "Moscow",
    "Beijing", "Shanghai", "Delhi", "Mumbai", "Cairo", "Rio", "Toronto", "Chicago",
    "Los Angeles", "San Francisco", "Miami", "Seattle", "Boston", "Dubai", "Singapore",
    "Bangkok", "Hong Kong", "Seoul", "Amsterdam", "Madrid", "Barcelona", "Mexico City",
    "Stockholm", "Oslo", "Copenhagen", "Helsinki", "Vienna", "Prague", "Budapest",
    "Warsaw", "Athens", "Istanbul", "Jerusalem", "Nairobi", "Cape Town", "Marrakech",
    "Dublin", "Edinburgh", "Glasgow", "Manchester", "Liverpool", "Birmingham", "Brussels",
    "Zurich", "Geneva", "Milan", "Florence", "Naples", "Venice", "Munich", "Frankfurt",
    "Hamburg", "Cologne", "Dusseldorf", "Lisbon", "Porto", "Sao Paulo", "Buenos Aires",
    "Lima", "Santiago", "Bogota", "Caracas", "Panama City", "Havana", "Montreal", "Vancouver",
    "Calgary", "Ottawa", "Melbourne", "Brisbane", "Perth", "Auckland", "Wellington",
    "Jakarta", "Manila", "Kuala Lumpur", "Hanoi", "Ho Chi Minh City", "Taipei", "Kyoto",
    "Osaka", "Sapporo", "Yokohama", "Hiroshima", "St Petersburg", "Vladivostok", "Kiev",
    "Tehran", "Baghdad", "Riyadh", "Mecca", "Muscat", "Doha", "Abu Dhabi", "Casablanca",
    "Surat", "Ahmedabad", "Pune", "Kolkata", "Chennai", "Bangalore", "Hyderabad", "Jaipur"
]

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class WeatherRequest(BaseModel):
    city: str

class SmartWeatherResponse(BaseModel):
    response_type: str
    text_response: str
    structured_data: Optional[Dict[str, Any]] = None

# Helper functions
def extract_city_and_activity(message: str) -> Tuple[str, str, str]:
    """Extract city, activity, and time from message"""
    message_lower = message.lower()
    
    # Extract city
    city = "unknown"
    for city_name in COMMON_CITIES:
        if city_name.lower() in message_lower:
            city = city_name
            break
    
    # Extract activity
    activity = "unknown"
    for act_name in ACTIVITIES.keys():
        if act_name.lower() in message_lower:
            activity = act_name
            break
    
    # Extract time context
    time_context = "now"
    time_indicators = {
        "morning": ["morning", "am"],
        "afternoon": ["afternoon", "noon"],
        "evening": ["evening", "night", "pm"],
        "tomorrow": ["tomorrow"],
        "today": ["today"],
        "tonight": ["tonight"]
    }
    
    for time_key, indicators in time_indicators.items():
        if any(indicator in message_lower for indicator in indicators):
            time_context = time_key
            break
    
    return city, activity, time_context

def classify_query_intent(message: str) -> str:
    """Classify the type of weather query"""
    message_lower = message.lower()
    
    # Check for activity planning keywords
    if any(keyword in message_lower for keyword in QUERY_TYPES["ACTIVITY_PLANNING"]):
        return "ACTIVITY_PLANNING"
    elif any(keyword in message_lower for keyword in QUERY_TYPES["CLOTHING_ADVICE"]):
        return "CLOTHING_ADVICE"
    elif any(keyword in message_lower for keyword in QUERY_TYPES["TRAVEL_PLANNING"]):
        return "TRAVEL_PLANNING"
    elif any(keyword in message_lower for keyword in QUERY_TYPES["COMFORT_ASSESSMENT"]):
        return "COMFORT_ASSESSMENT"
    else:
        return "BASIC_WEATHER"

async def get_enhanced_weather_data(city: str) -> Dict[str, Any]:
    """Get comprehensive weather data including current and forecast"""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured")
    
    async with httpx.AsyncClient() as client:
        try:
            # Get current weather
            current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            current_response = await client.get(current_url)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            # Get forecast data
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
            forecast_response = await client.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            return {
                "current": current_data,
                "forecast": forecast_data,
                "city_info": {
                    "name": current_data["name"],
                    "country": current_data["sys"]["country"],
                    "timezone": current_data["timezone"]
                }
            }
            
        except httpx.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"City {city} not found")
            raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

def analyze_activity_suitability(weather_data: Dict[str, Any], activity: str, time_context: str) -> Dict[str, Any]:
    """Analyze if weather is suitable for the specified activity"""
    if activity not in ACTIVITIES:
        return {"suitable": False, "reason": "Activity not recognized"}
    
    activity_req = ACTIVITIES[activity]
    current = weather_data["current"]
    
    # Extract weather metrics
    temp = current["main"]["temp"]
    humidity = current["main"]["humidity"]
    wind_speed = current["wind"]["speed"] if "wind" in current else 0
    precipitation = 0
    if "rain" in current:
        precipitation = current["rain"].get("1h", 0)
    elif "snow" in current:
        precipitation = current["snow"].get("1h", 0)
    
    weather_desc = current["weather"][0]["description"]
    
    # Analyze suitability factors
    factors = []
    overall_score = 100
    
    # Temperature check
    temp_min, temp_max = activity_req["optimal_temp"]
    if temp_min <= temp <= temp_max:
        factors.append({"factor": "temperature", "value": f"{temp}°C", "impact": "excellent", "score": 100})
    elif temp < temp_min - 5 or temp > temp_max + 5:
        factors.append({"factor": "temperature", "value": f"{temp}°C", "impact": "poor", "score": 30})
        overall_score -= 40
    else:
        factors.append({"factor": "temperature", "value": f"{temp}°C", "impact": "moderate", "score": 70})
        overall_score -= 15
    
    # Wind check
    if wind_speed <= activity_req["max_wind"]:
        factors.append({"factor": "wind", "value": f"{wind_speed} m/s", "impact": "good", "score": 90})
    else:
        factors.append({"factor": "wind", "value": f"{wind_speed} m/s", "impact": "poor", "score": 40})
        overall_score -= 25
    
    # Precipitation check
    if precipitation <= activity_req["precipitation_tolerance"]:
        factors.append({"factor": "precipitation", "value": f"{precipitation}mm", "impact": "excellent", "score": 100})
    else:
        factors.append({"factor": "precipitation", "value": f"{precipitation}mm", "impact": "poor", "score": 20})
        overall_score -= 50
    
    # Humidity assessment
    humidity_impact = "good"
    if activity_req["humidity_preference"] == "low" and humidity > 70:
        humidity_impact = "moderate"
        overall_score -= 10
    elif activity_req["humidity_preference"] == "moderate" and (humidity > 80 or humidity < 30):
        humidity_impact = "moderate"
        overall_score -= 10
    
    factors.append({"factor": "humidity", "value": f"{humidity}%", "impact": humidity_impact, "score": 85 if humidity_impact == "good" else 70})
    
    # Determine recommendation
    recommendation = "excellent" if overall_score >= 85 else "good" if overall_score >= 70 else "moderate" if overall_score >= 50 else "poor"
    
    return {
        "suitable": overall_score >= 50,
        "recommendation": recommendation,
        "confidence": min(overall_score, 100),
        "factors": factors,
        "overall_score": overall_score,
        "weather_description": weather_desc
    }

def generate_activity_advice(analysis: Dict[str, Any], city: str, activity: str, time_context: str) -> str:
    """Generate human-readable advice based on analysis"""
    recommendation = analysis["recommendation"]
    confidence = analysis["confidence"]
    
    if recommendation == "excellent":
        advice = f"Perfect weather for {activity} in {city}! "
    elif recommendation == "good":
        advice = f"Good conditions for {activity} in {city}. "
    elif recommendation == "moderate":
        advice = f"You can {activity} in {city}, but conditions aren't ideal. "
    else:
        advice = f"Weather in {city} isn't great for {activity} right now. "
    
    # Add specific factor mentions
    poor_factors = [f["factor"] for f in analysis["factors"] if f["impact"] == "poor"]
    if poor_factors:
        if "precipitation" in poor_factors:
            advice += "It's currently raining. "
        if "temperature" in poor_factors:
            temp_val = next(f["value"] for f in analysis["factors"] if f["factor"] == "temperature")
            advice += f"Temperature is {temp_val}, which might be uncomfortable. "
        if "wind" in poor_factors:
            wind_val = next(f["value"] for f in analysis["factors"] if f["factor"] == "wind")
            advice += f"Wind speed is {wind_val}, which could affect your activity. "
    
    # Add timing advice if relevant
    if time_context == "evening" and recommendation in ["excellent", "good"]:
        advice += "Evening timing looks great! "
    
    return advice.strip()

# API Endpoints
@app.get("/api/weather/{city}")
async def get_weather(city: str):
    """Get basic weather data for a city"""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured")
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"City {city} not found")
            raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

@app.get("/api/weather-forecast/{city}")
async def get_weather_forecast(city: str):
    """Get extended forecast data for a city"""
    try:
        weather_data = await get_enhanced_weather_data(city)
        return weather_data["forecast"]
    except Exception as e:
        logger.error(f"Error fetching forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching forecast data: {str(e)}")

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """Basic chat with AI endpoint"""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        
        ai_response = response.choices[0].message.content
        return {"response": ai_response}
    
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with OpenAI: {str(e)}")

@app.post("/api/weather-chat")
async def weather_chat(request: ChatRequest):
    """Basic weather chat - maintained for backward compatibility"""
    try:
        logger.info("Processing weather-chat request")
        
        last_user_message = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), None)
        logger.info(f"Last user message: {last_user_message}")
        
        if not last_user_message:
            return {"response": "I couldn't understand your question. Please ask about the weather in a specific city."}
        
        # Use OpenAI for city extraction
        try:
            system_prompt = "You are a helpful assistant that extracts city names from user queries about weather. Only respond with the city name, nothing else. If no city is mentioned or you're unsure, respond with 'unknown'."
            
            city_extraction = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": last_user_message}
                ],
            )
            
            city = city_extraction.choices[0].message.content.strip()
            logger.info(f"Extracted city: {city}")
            
        except Exception as e:
            logger.warning(f"City extraction failed: {str(e)}")
            return {"response": "I couldn't determine which city you're asking about. Can you specify the city name?"}
        
        if city.lower() == "unknown":
            return {"response": "I couldn't determine which city you're asking about. Can you specify the city name?"}
        
        # Get weather data
        try:
            weather_data = await get_enhanced_weather_data(city)
            current = weather_data["current"]
            
            weather_desc = current["weather"][0]["description"]
            temp = current["main"]["temp"]
            feels_like = current["main"]["feels_like"]
            humidity = current["main"]["humidity"]
            
            weather_info = f"Weather in {city}: {weather_desc}. Temperature: {temp}°C (feels like {feels_like}°C). Humidity: {humidity}%."
            
            # Generate response with OpenAI
            chat_response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful weather assistant. Use the weather information provided to answer the user's question in a natural, conversational way."},
                    {"role": "user", "content": last_user_message},
                    {"role": "assistant", "content": f"Here's the weather information: {weather_info}"}
                ],
            )
            
            response_text = chat_response.choices[0].message.content
            return {"response": response_text}
            
        except Exception as e:
            logger.error(f"Error processing weather data: {str(e)}")
            return {"response": "I'm having trouble getting weather information right now. Please try again later."}
    
    except Exception as e:
        logger.error(f"Unexpected error in weather_chat: {str(e)}")
        return {"response": "I encountered an unexpected error. Please try again later."}

@app.post("/api/smart-weather-chat")
async def smart_weather_chat(request: ChatRequest):
    """Enhanced weather chat with complex query handling"""
    try:
        logger.info("Processing smart weather chat request")
        
        last_user_message = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), None)
        logger.info(f"Last user message: {last_user_message}")
        
        if not last_user_message:
            return {"response": "I couldn't understand your question. Please ask about weather or activities!"}
        
        # Classify query intent
        intent = classify_query_intent(last_user_message)
        logger.info(f"Classified intent: {intent}")
        
        # Extract information from message
        city, activity, time_context = extract_city_and_activity(last_user_message)
        logger.info(f"Extracted - City: {city}, Activity: {activity}, Time: {time_context}")
        
        # If no city detected, use OpenAI for extraction
        if city == "unknown":
            try:
                system_prompt = "Extract the city name from this message. If no city is mentioned, respond with 'unknown'. Only respond with the city name."
                
                city_extraction = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": last_user_message}
                    ],
                )
                
                city = city_extraction.choices[0].message.content.strip()
                logger.info(f"OpenAI extracted city: {city}")
                
            except Exception as e:
                logger.warning(f"OpenAI city extraction failed: {str(e)}")
        
        if city.lower() == "unknown":
            return {"response": "I couldn't determine which city you're asking about. Could you please specify the city name?"}
        
        # Get enhanced weather data
        try:
            weather_data = await get_enhanced_weather_data(city)
            current = weather_data["current"]
            
            # Basic weather info
            weather_desc = current["weather"][0]["description"]
            temp = current["main"]["temp"]
            feels_like = current["main"]["feels_like"]
            humidity = current["main"]["humidity"]
            wind_speed = current["wind"]["speed"] if "wind" in current else 0
            
            # Handle different query types
            if intent == "ACTIVITY_PLANNING" and activity != "unknown":
                # Activity-specific analysis
                analysis = analyze_activity_suitability(weather_data, activity, time_context)
                advice = generate_activity_advice(analysis, city, activity, time_context)
                
                # Create structured response
                structured_data = {
                    "query_type": "activity_planning",
                    "city": city,
                    "activity": activity,
                    "time_context": time_context,
                    "recommendation": analysis["recommendation"],
                    "confidence": analysis["confidence"],
                    "factors": analysis["factors"],
                    "current_weather": {
                        "temperature": f"{temp}°C",
                        "description": weather_desc,
                        "humidity": f"{humidity}%",
                        "wind_speed": f"{wind_speed} m/s"
                    }
                }
                
                return {
                    "response": advice,
                    "response_type": "activity_advice",
                    "structured_data": structured_data
                }
            
            else:
                # Enhanced basic weather response
                weather_info = f"Weather in {city}: {weather_desc}. Temperature: {temp}°C (feels like {feels_like}°C). Humidity: {humidity}%. Wind: {wind_speed} m/s."
                
                # Use OpenAI for natural response
                system_prompt = """You are a helpful weather assistant. Provide detailed, conversational weather information. 
                If the user seems to be asking about activities or planning, offer relevant advice based on the weather conditions."""
                
                chat_response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": last_user_message},
                        {"role": "assistant", "content": f"Current weather data: {weather_info}"}
                    ],
                )
                
                response_text = chat_response.choices[0].message.content
                
                structured_data = {
                    "query_type": "basic_weather",
                    "city": city,
                    "current_weather": {
                        "temperature": f"{temp}°C",
                        "feels_like": f"{feels_like}°C",
                        "description": weather_desc,
                        "humidity": f"{humidity}%",
                        "wind_speed": f"{wind_speed} m/s"
                    }
                }
                
                return {
                    "response": response_text,
                    "response_type": "enhanced_weather",
                    "structured_data": structured_data
                }
                
        except Exception as e:
            logger.error(f"Error processing weather data: {str(e)}")
            return {"response": "I'm having trouble getting weather information right now. Please try again later."}
    
    except Exception as e:
        logger.error(f"Unexpected error in smart_weather_chat: {str(e)}")
        return {"response": "I encountered an unexpected error. Please try again later."}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0", "features": ["smart_weather", "activity_planning"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 