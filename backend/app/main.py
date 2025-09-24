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
from typing import List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
# Get the base directory
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
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Common city names to help with extraction when OpenAI is unavailable
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
    "Tehran", "Baghdad", "Riyadh", "Mecca", "Muscat", "Doha", "Abu Dhabi", "Casablanca"
]

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class WeatherRequest(BaseModel):
    city: str

# Helper function to extract city using simple rule-based approach
def extract_city_rule_based(message: str) -> Tuple[str, float]:
    """
    Extract city name from message using simple rules.
    Returns the city name and a confidence score (0-1).
    """
    # Clean and normalize the message
    message = message.lower()
    
    # Look for common patterns
    patterns = [
        r"weather (?:in|at|for) ([a-zA-Z\s]+)(?:[\?\.,]|$)",
        r"(?:in|at) ([a-zA-Z\s]+) (?:like|now|today)",
        r"(?:how is|how's) (?:the weather in|the weather at|weather in|weather at) ([a-zA-Z\s]+)",
        r"what'?s (?:the weather like in|the weather in) ([a-zA-Z\s]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            city = match.group(1).strip().title()
            return city, 0.8
    
    # If no pattern matched, check for direct city mentions
    for city in COMMON_CITIES:
        if city.lower() in message.lower():
            return city, 0.7
            
    # If the message is very short (1-2 words), it might be just the city name
    words = message.strip().split()
    if len(words) <= 2:
        potential_city = message.strip().title()
        return potential_city, 0.5
    
    return "unknown", 0.0

# Weather API endpoint
@app.get("/api/weather/{city}")
async def get_weather(city: str):
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
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"City {city} not found")
            raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

# Chat with AI endpoint
@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Prepare messages for OpenAI API
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        
        # Extract and return the AI's response
        ai_response = response.choices[0].message.content
        return {"response": ai_response}
    
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with OpenAI: {str(e)}")

# Endpoint to integrate weather info into the chat
@app.post("/api/weather-chat")
async def weather_chat(request: ChatRequest):
    try:
        logger.info("Processing weather-chat request")
        
        # Get the last user message
        last_user_message = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), None)
        logger.info(f"Last user message: {last_user_message}")
        
        if not last_user_message:
            logger.warning("No user message found in the request")
            return {"response": "I couldn't understand your question. Please ask about the weather in a specific city."}
        
        # Variable to hold the extracted city
        city = "unknown"
        openai_worked = False
        
        # First try OpenAI for city extraction
        try:
            # Extract city name using OpenAI
            logger.info("Attempting to extract city using OpenAI")
            system_prompt = "You are a helpful assistant that extracts city names from user queries about weather. Only respond with the city name, nothing else. If no city is mentioned or you're unsure, respond with 'unknown'."
            
            city_extraction = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": last_user_message}
                ],
            )
            
            city = city_extraction.choices[0].message.content.strip()
            logger.info(f"OpenAI extracted city: {city}")
            openai_worked = True
            
        except Exception as e:
            logger.warning(f"OpenAI city extraction failed: {str(e)}")
            logger.info("Falling back to rule-based city extraction")
            
            # Fallback to rule-based extraction
            city, confidence = extract_city_rule_based(last_user_message)
            logger.info(f"Rule-based extracted city: {city} (confidence: {confidence})")
            
            # If confidence is very low, ask for clarification
            if confidence < 0.4:
                return {"response": "I'm not sure which city you're asking about. Could you please specify the city name more clearly?"}
        
        if city.lower() == "unknown":
            return {"response": "I couldn't determine which city you're asking about. Can you specify the city name?"}
        
        try:
            # Get weather data for the extracted city
            api_key = os.environ.get("OPENWEATHER_API_KEY")
            if not api_key:
                logger.error("OpenWeather API key not configured")
                return {"response": "I'm sorry, but I'm not able to fetch weather information at the moment. Please try again later."}
            
            logger.info(f"Fetching weather data for city: {city}")
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    weather_data = response.json()
                    
                    # Format weather information
                    weather_desc = weather_data["weather"][0]["description"]
                    temp = weather_data["main"]["temp"]
                    feels_like = weather_data["main"]["feels_like"]
                    humidity = weather_data["main"]["humidity"]
                    
                    weather_info = f"Weather in {city}: {weather_desc}. Temperature: {temp}°C (feels like {feels_like}°C). Humidity: {humidity}%."
                    logger.info(f"Weather info: {weather_info}")
                    
                except httpx.HTTPError as e:
                    if hasattr(e, 'response') and e.response.status_code == 404:
                        logger.warning(f"City not found: {city}")
                        return {"response": f"I couldn't find weather information for {city}. Please check the city name and try again."}
                    logger.error(f"HTTP error fetching weather: {str(e)}")
                    return {"response": f"I'm having trouble getting weather data right now. Please try again later."}
                except KeyError as e:
                    logger.error(f"Error parsing weather data: {str(e)}")
                    return {"response": "I received weather information but couldn't parse it correctly. Please try again."}
        
        except Exception as e:
            logger.error(f"Error in weather data retrieval: {str(e)}")
            return {"response": "I'm having trouble getting weather information right now. Please try again later."}
        
        try:
            # If OpenAI is working, generate a natural language response
            if openai_worked:
                logger.info("Generating response with OpenAI")
                chat_response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful weather assistant. Use the weather information provided to answer the user's question in a natural, conversational way."},
                        {"role": "user", "content": last_user_message},
                        {"role": "assistant", "content": f"Here's the weather information: {weather_info}"}
                    ],
                )
                
                response_text = chat_response.choices[0].message.content
                logger.info("Generated response successfully")
                return {"response": response_text}
            else:
                # If OpenAI is not available, return formatted weather info directly
                return {"response": f"Here's the weather information: {weather_info}"}
                
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            return {"response": f"I found the weather in {city}: {weather_info}"}
    
    except Exception as e:
        logger.error(f"Unexpected error in weather_chat endpoint: {str(e)}")
        return {"response": "I encountered an unexpected error. Please try again later."}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 