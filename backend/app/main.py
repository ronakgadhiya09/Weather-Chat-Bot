from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import logging
import json
import traceback
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

# LangChain imports
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
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

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class WeatherRequest(BaseModel):
    city: str

# LangChain Tools
class WeatherTool(BaseTool):
    name: str = "get_current_weather"
    description: str = """Get current weather information for a specific city. 
    Use this tool when users ask about current weather conditions, temperature, humidity, wind speed, etc.
    Input should be a city name."""

    def _run(self, city: str) -> str:
        """Get current weather for a city"""
        try:
            api_key = os.environ.get("OPENWEATHER_API_KEY")
            if not api_key:
                return "Weather API key not configured"
            
            # Use synchronous requests instead of async
            import requests
            
            current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
            weather_data = response.json()
            
            current = weather_data
            temp = current["main"]["temp"]
            feels_like = current["main"]["feels_like"]
            humidity = current["main"]["humidity"]
            wind_speed = current["wind"]["speed"] if "wind" in current else 0
            description = current["weather"][0]["description"]
            city_name = current["name"]
            country = current["sys"]["country"]
            
            return f"""Current weather in {city_name}, {country}:
Temperature: {temp}°C (feels like {feels_like}°C)
Description: {description}
Humidity: {humidity}%
Wind Speed: {wind_speed} m/s"""
            
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            return f"Sorry, I couldn't get weather information for {city}. Please check the city name."

class WeatherForecastTool(BaseTool):
    name: str = "get_weather_forecast"
    description: str = """Get weather forecast for a specific city. 
    Use this tool when users ask about future weather, tomorrow's weather, or planning activities for later.
    Input should be a city name."""

    def _run(self, city: str) -> str:
        """Get weather forecast for a city"""
        try:
            api_key = os.environ.get("OPENWEATHER_API_KEY")
            if not api_key:
                return "Weather API key not configured"
            
            # Use synchronous requests instead of async
            import requests
            
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
            response = requests.get(forecast_url, timeout=10)
            response.raise_for_status()
            forecast_data = response.json()
            
            # Get next 24 hours forecast (8 entries of 3-hour intervals)
            forecasts = forecast_data["list"][:8]
            city_name = forecast_data["city"]["name"]
            country = forecast_data["city"]["country"]
            
            forecast_text = f"Weather forecast for {city_name}, {country}:\n"
            
            for i, forecast in enumerate(forecasts):
                dt = datetime.fromtimestamp(forecast["dt"])
                temp = forecast["main"]["temp"]
                description = forecast["weather"][0]["description"]
                time_str = dt.strftime("%Y-%m-%d %H:%M")
                
                forecast_text += f"\n{time_str}: {temp}°C, {description}"
                
                # Only show first 4 entries to keep response manageable
                if i >= 3:
                    break
            
            return forecast_text
            
        except Exception as e:
            logger.error(f"Error fetching forecast: {str(e)}")
            return f"Sorry, I couldn't get forecast information for {city}. Please check the city name."

class ActivityAdviceTool(BaseTool):
    name: str = "get_activity_advice"
    description: str = """Provide advice on whether specific activities are suitable based on current weather.
    Use this tool when users ask about outdoor activities like cricket, football, running, cycling, picnics, etc.
    Input should be in format: 'city_name|activity_name' (e.g., 'Mumbai|cricket')"""

    def _run(self, query: str) -> str:
        """Provide activity advice based on weather"""
        try:
            if "|" not in query:
                return "Please specify both city and activity. Format: 'city|activity'"
            
            city, activity = query.split("|", 1)
            city = city.strip()
            activity = activity.strip().lower()
            
            # First get current weather
            weather_tool = WeatherTool()
            weather_info = weather_tool._run(city)
            
            if "Sorry" in weather_info:
                return weather_info
            
            # Activity-specific advice logic
            activity_requirements = {
                "cricket": {
                    "ideal_temp": (20, 35),
                    "max_wind": 15,
                    "rain_tolerance": "none",
                    "description": "Cricket requires dry conditions with moderate temperatures and low wind."
                },
                "football": {
                    "ideal_temp": (15, 30),
                    "max_wind": 20,
                    "rain_tolerance": "light",
                    "description": "Football can be played in various conditions but avoid heavy rain."
                },
                "running": {
                    "ideal_temp": (10, 25),
                    "max_wind": 25,
                    "rain_tolerance": "light",
                    "description": "Running is great in cooler temperatures. Light rain is usually fine."
                },
                "cycling": {
                    "ideal_temp": (15, 28),
                    "max_wind": 20,
                    "rain_tolerance": "none",
                    "description": "Cycling requires good visibility and dry roads for safety."
                },
                "picnic": {
                    "ideal_temp": (18, 30),
                    "max_wind": 15,
                    "rain_tolerance": "none",
                    "description": "Picnics need pleasant, dry weather with gentle breezes."
                }
            }
            
            if activity not in activity_requirements:
                return f"I can provide advice for these activities: {', '.join(activity_requirements.keys())}. The current weather in {city} is:\n{weather_info}"
            
            req = activity_requirements[activity]
            
            # Parse weather info to extract conditions
            # This is a simplified analysis - in a real implementation you'd parse the actual data
            advice = f"Activity Advice for {activity.title()} in {city}:\n\n"
            advice += f"{req['description']}\n\n"
            advice += f"Current conditions:\n{weather_info}\n\n"
            
            # General advice based on weather description
            if "rain" in weather_info.lower():
                if req["rain_tolerance"] == "none":
                    advice += "❌ NOT RECOMMENDED: Current rainy conditions are not suitable for this activity."
                else:
                    advice += "⚠️ CAUTION: Light rain detected. Consider indoor alternatives or wait for conditions to improve."
            elif "clear" in weather_info.lower() or "sunny" in weather_info.lower():
                advice += "✅ EXCELLENT: Clear weather conditions are perfect for this activity!"
            elif "cloud" in weather_info.lower():
                advice += "✅ GOOD: Cloudy conditions are generally suitable for this activity."
            else:
                advice += "ℹ️ Check current conditions and dress appropriately for the weather."
            
            return advice
            
        except Exception as e:
            logger.error(f"Error providing activity advice: {str(e)}")
            return f"Sorry, I couldn't analyze activity conditions. Error: {str(e)}"

# Initialize components
try:
    logger.info("Initializing components...")
    
    # Initialize OpenAI for intelligent routing
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    logger.info("LLM initialized successfully")

    # Create tools
    weather_tool = WeatherTool()
    forecast_tool = WeatherForecastTool()
    activity_tool = ActivityAdviceTool()
    
    logger.info("Tools initialized successfully")
    
except Exception as e:
    logger.error(f"Error initializing components: {str(e)}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    raise

def extract_city_from_message(message: str) -> str:
    """Extract city name from user message using simple patterns and OpenAI"""
    try:
        # First, try simple regex patterns for common cities
        common_cities = [
            "mumbai", "delhi", "bangalore", "chennai", "kolkata", "hyderabad", "pune", "ahmedabad", "surat", "jaipur",
            "new york", "london", "paris", "tokyo", "sydney", "berlin", "rome", "moscow", "beijing", "shanghai",
            "los angeles", "chicago", "miami", "toronto", "dubai", "singapore", "bangkok", "hong kong"
        ]
        
        message_lower = message.lower()
        for city in common_cities:
            if city in message_lower:
                return city.title()
        
        # If no common city found, use OpenAI to extract
        try:
            response = llm.invoke([
                {"role": "system", "content": "Extract the city name from the user's message. Reply with only the city name, nothing else. If no city is mentioned, reply 'unknown'."},
                {"role": "user", "content": message}
            ])
            city = response.content.strip()
            return city if city.lower() != "unknown" else None
        except Exception as e:
            logger.warning(f"OpenAI city extraction failed: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting city: {str(e)}")
        return None

def classify_intent(message: str) -> str:
    """Classify user intent"""
    message_lower = message.lower()
    
    # Activity keywords
    activity_keywords = ["play", "can i", "should i", "good for", "suitable", "advice", "activity"]
    forecast_keywords = ["tomorrow", "later", "forecast", "future", "planning", "next", "will be"]
    
    if any(keyword in message_lower for keyword in activity_keywords):
        return "activity"
    elif any(keyword in message_lower for keyword in forecast_keywords):
        return "forecast"
    else:
        return "current_weather"

def extract_activity_from_message(message: str) -> str:
    """Extract activity from message"""
    activities = ["cricket", "football", "running", "cycling", "picnic", "walking"]
    message_lower = message.lower()
    
    for activity in activities:
        if activity in message_lower:
            return activity
    return None

def smart_weather_assistant(user_message: str) -> tuple:
    """Intelligent weather assistant using tools - returns (response_text, structured_data)"""
    try:
        logger.info(f"Processing message: {user_message}")
        
        # Extract city
        city = extract_city_from_message(user_message)
        if not city:
            return "I couldn't determine which city you're asking about. Could you please specify the city name?", None
        
        logger.info(f"Extracted city: {city}")
        
        # Classify intent
        intent = classify_intent(user_message)
        logger.info(f"Classified intent: {intent}")
        
        # Get current weather data for structured response
        weather_info = weather_tool._run(city)
        
        if intent == "activity":
            # Extract activity
            activity = extract_activity_from_message(user_message)
            if activity:
                logger.info(f"Extracted activity: {activity}")
                result = activity_tool._run(f"{city}|{activity}")
                
                # Parse weather info to create structured data
                structured_data = create_activity_structured_data(weather_info, city, activity, result)
                
                # Use OpenAI for conversational response if available
                try:
                    final_response = llm.invoke([
                        {"role": "system", "content": "You are a friendly weather assistant. Take the weather information provided and present it in a natural, conversational way. Keep the technical details but make it engaging and easy to understand."},
                        {"role": "user", "content": f"User asked: {user_message}"},
                        {"role": "assistant", "content": f"Weather data: {result}"}
                    ])
                    return final_response.content, structured_data
                except Exception as e:
                    logger.warning(f"OpenAI formatting failed: {str(e)}")
                    return result, structured_data
            else:
                # Get current weather and provide general activity advice
                result = f"Here's the current weather in {city}:\n\n{weather_info}\n\nWhat specific activity are you planning? I can provide advice for cricket, football, running, cycling, or picnics."
                structured_data = create_weather_structured_data(weather_info, city)
                return result, structured_data
        
        elif intent == "forecast":
            result = forecast_tool._run(city)
            structured_data = create_weather_structured_data(weather_info, city)
        
        else:  # current_weather
            result = weather_info
            structured_data = create_weather_structured_data(weather_info, city)
        
        # Use OpenAI to make the response more conversational
        try:
            final_response = llm.invoke([
                {"role": "system", "content": "You are a friendly weather assistant. Take the weather information provided and present it in a natural, conversational way. Keep the technical details but make it engaging and easy to understand."},
                {"role": "user", "content": f"User asked: {user_message}"},
                {"role": "assistant", "content": f"Weather data: {result}"}
            ])
            return final_response.content, structured_data
        except Exception as e:
            logger.warning(f"OpenAI formatting failed: {str(e)}")
            return result, structured_data
            
    except Exception as e:
        logger.error(f"Error in smart_weather_assistant: {str(e)}")
        return "I'm having trouble processing your request. Please try again.", None

def parse_weather_data(weather_info: str) -> dict:
    """Parse weather information string into structured data"""
    try:
        # Extract temperature
        temp_match = re.search(r'Temperature: ([\d.]+)°C', weather_info)
        feels_like_match = re.search(r'feels like ([\d.]+)°C', weather_info)
        humidity_match = re.search(r'Humidity: (\d+)%', weather_info)
        wind_match = re.search(r'Wind Speed: ([\d.]+) m/s', weather_info)
        desc_match = re.search(r'Description: ([^\n]+)', weather_info)
        
        return {
            "temperature": f"{temp_match.group(1)}°C" if temp_match else "N/A",
            "feels_like": f"{feels_like_match.group(1)}°C" if feels_like_match else "N/A",
            "humidity": f"{humidity_match.group(1)}%" if humidity_match else "N/A",
            "wind_speed": f"{wind_match.group(1)} m/s" if wind_match else "N/A",
            "description": desc_match.group(1) if desc_match else "N/A"
        }
    except Exception as e:
        logger.warning(f"Error parsing weather data: {str(e)}")
        return {
            "temperature": "N/A",
            "feels_like": "N/A",
            "humidity": "N/A", 
            "wind_speed": "N/A",
            "description": "N/A"
        }

def create_weather_structured_data(weather_info: str, city: str) -> dict:
    """Create structured data for basic weather response"""
    current_weather = parse_weather_data(weather_info)
    return {
        "query_type": "basic_weather",
        "city": city,
        "current_weather": current_weather
    }

def create_activity_structured_data(weather_info: str, city: str, activity: str, advice_result: str) -> dict:
    """Create structured data for activity advice response"""
    current_weather = parse_weather_data(weather_info)
    
    # Determine recommendation based on advice result
    recommendation = "moderate"
    confidence = 75
    
    if "EXCELLENT" in advice_result or "✅" in advice_result:
        recommendation = "excellent"
        confidence = 90
    elif "GOOD" in advice_result:
        recommendation = "good"
        confidence = 85
    elif "NOT RECOMMENDED" in advice_result or "❌" in advice_result:
        recommendation = "poor"
        confidence = 95
    elif "CAUTION" in advice_result or "⚠️" in advice_result:
        recommendation = "moderate"
        confidence = 70
    
    # Create mock factors for frontend compatibility
    factors = [
        {
            "factor": "temperature",
            "value": current_weather["temperature"],
            "impact": "good" if recommendation in ["excellent", "good"] else "moderate",
            "score": 85 if recommendation in ["excellent", "good"] else 60
        },
        {
            "factor": "humidity",
            "value": current_weather["humidity"],
            "impact": "good" if recommendation in ["excellent", "good"] else "moderate", 
            "score": 80 if recommendation in ["excellent", "good"] else 55
        },
        {
            "factor": "wind",
            "value": current_weather["wind_speed"],
            "impact": "good" if recommendation in ["excellent", "good"] else "moderate",
            "score": 75 if recommendation in ["excellent", "good"] else 50
        }
    ]
    
    return {
        "query_type": "activity_planning",
        "city": city,
        "activity": activity,
        "time_context": "now",
        "recommendation": recommendation,
        "confidence": confidence,
        "factors": factors,
        "current_weather": current_weather
    }

# API Endpoints
@app.post("/api/smart-weather-chat")
async def smart_weather_chat(request: ChatRequest):
    """Enhanced weather chat using intelligent tool routing"""
    try:
        logger.info("Processing smart weather chat request")
        
        # Get the last user message
        last_user_message = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), None)
        logger.info(f"Last user message: {last_user_message}")
        
        if not last_user_message:
            return {"response": "I couldn't understand your question. Please ask about weather or activities!"}
        
        # Process with smart assistant
        response_text, structured_data = smart_weather_assistant(last_user_message)
        
        # Determine response type based on structured data or message content
        if structured_data and structured_data.get("query_type") == "activity_planning":
            response_type = "activity_advice"
        else:
            response_type = "enhanced_weather"
        
        # Ensure structured_data has the right format
        if not structured_data:
            structured_data = {
                "query_type": "smart_assistant",
                "response_type": response_type,
                "tools_used": True
            }
        
        return {
            "response": response_text,
            "response_type": response_type,
            "structured_data": structured_data
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in smart_weather_chat: {str(e)}")
        return {
            "response": "I encountered an unexpected error. Please try again later.",
            "response_type": "error"
        }

@app.get("/api/weather/{city}")
async def get_weather(city: str):
    """Simple weather endpoint for direct city queries"""
    try:
        weather_info = weather_tool._run(city)
        return {"response": weather_info}
    except Exception as e:
        logger.error(f"Error in weather endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "version": "3.0-smart-tools", 
        "features": ["smart_assistant", "weather_tools", "activity_planning", "intelligent_routing"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 