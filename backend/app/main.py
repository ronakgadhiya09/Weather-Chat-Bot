#!/usr/bin/env python3
"""
Weather Assistant Bot API

A smart weather assistant built with the Agno framework that provides:
- Current weather information
- Weather forecasts
- Outdoor activity recommendations
- Air quality information
- Location-based weather insights

FastAPI endpoints for frontend integration.
"""

import os
import sys
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add parent directory to path for local development
if __name__ == "__main__" or "app" not in sys.modules:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.groq import Groq
from agno.tools.openweather import OpenWeatherTools

# Try absolute import first (for Vercel), fallback to relative import (for local dev)
try:
    from app.weather_tools_fixed import FixedWeatherTools
except ImportError:
    from weather_tools_fixed import FixedWeatherTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
base_dir = Path(__file__).resolve().parent.parent
env_path = os.path.join(base_dir, "config.env")
# Try to load from config.env, but don't fail if it doesn't exist (for Vercel deployment)
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # For Vercel deployment, environment variables are set via vercel.json
    load_dotenv()  # Load from .env or environment

# Log environment setup
logger.info(f"Loading environment from: {env_path}")
logger.info(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")
logger.info(f"OpenWeather API Key set: {'Yes' if os.environ.get('OPENWEATHER_API_KEY') else 'No'}")
logger.info(f"Groq API Key set: {'Yes' if os.environ.get('GROQ_API_KEY') else 'No'}")

app = FastAPI(title="WeatherBot API", description="Agentic Weather Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
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
    language: Optional[str] = 'en'  # Default to English

class WeatherAssistant:
    """Weather Assistant using Agno framework with memory"""
    
    def __init__(self):
        """Initialize the Weather Assistant"""
        # Initialize session state for simple memory
        self.session_state = {
            "last_location": None,
            "conversation_count": 0,
            "conversation_history": [],
            "language": "en"
        }
        
        # Check for OpenWeather API key
        openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        if not openweather_api_key:
            logger.error("OpenWeather API key not found!")
            raise ValueError("OpenWeather API key required")
        
        # Initialize model (using more stable models to avoid corrupted responses)
        try:
            # Try Groq with a more stable model first
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key:
                # Use llama-3.3-70b-versatile which is currently supported
                model = Groq(
                    id="llama-3.3-70b-versatile",
                    max_tokens=800,  # Limit response length to prevent rambling
                    temperature=0.2   # Lower temperature for more focused responses
                )
                logger.info("🚀 Using Groq Llama 3.3 70B model")
            else:
                # Fallback to OpenAI
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if openai_api_key:
                    model = OpenAIChat(
                        id="gpt-3.5-turbo",
                        max_tokens=1000,
                        temperature=0.1
                    )
                    logger.info("🤖 Using OpenAI GPT-3.5-turbo model")
                else:
                    logger.error("No AI model API key found!")
                    raise ValueError("Either GROQ_API_KEY or OPENAI_API_KEY required")
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise
        
        # Initialize tools (using original OpenWeatherTools with better instructions)
        try:
            weather_tools = OpenWeatherTools(
                api_key=openweather_api_key,
                units="metric",
                enable_current_weather=True,
                enable_forecast=True,
                enable_air_pollution=True,
                enable_geocoding=False  # Disable geocoding to reduce complexity
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenWeatherTools: {e}, falling back to FixedWeatherTools")
            weather_tools = FixedWeatherTools(
                api_key=openweather_api_key,
                units="metric"
            )
        
        # Create the weather assistant agent with memory and context
        self.agent = Agent(
            name="WeatherBot",
            model=model,
            tools=[weather_tools],  # Only weather tools, no web search
            instructions=[
                "You are WeatherBot, a helpful weather assistant with memory.",
                "Give concise weather information under 150 words.",
                "Include temperature, conditions, humidity, and wind.",
                "Provide practical activity and clothing recommendations.",
                "Use simple language and minimal emojis.",
                "LANGUAGE SUPPORT:",
                "- Check session_state['language'] to determine response language",
                "- If language is 'ja' (Japanese), respond entirely in Japanese",
                "- If language is 'en' (English), respond in English",
                "- Always maintain the requested language throughout your response",
                "- Japanese responses should use natural, polite Japanese (です/ます form)",
                "CONVERSATION FLOW RULES:",
                "- Recognize when user is saying thank you, goodbye, or general acknowledgments",
                "- For thank you messages ('thank you', 'thanks', 'ありがとう', 'ありがとうございます'), respond politely and offer help with other weather questions",
                "- For greetings ('hello', 'hi', 'こんにちは'), respond warmly and ask how you can help with weather",
                "- For goodbyes ('bye', 'goodbye', 'さようなら'), wish them well and mention you're available for weather questions",
                "- DO NOT repeat previous weather information unless specifically asked about it again",
                "- Only provide weather data when explicitly requested or when answering weather-specific questions",
                "MEMORY & CONTEXT RULES:",
                "- Check session_state['last_location'] for the user's previously mentioned city",
                "- For follow-up questions like 'tomorrow?', 'cycling?', 'what about...', use last_location ONLY if it's weather-related",
                "- If user asks about activities/weather without location, use last_location from session_state",
                "- If no location in session_state and none mentioned, ask for their city",
                "- Session state contains: last_location, conversation_count, and language",
                "- NEVER treat words like 'tomorrow', 'what about', 'cycling' as locations",
                "- For non-weather conversations (greetings, thanks, general chat), do NOT reference last_location",
                "- Keep location context separate from general conversation context",
                "TOOL USAGE RULES:",
                "- For current weather: use get_current_weather(location='City')",
                "- For forecasts: use get_forecast(location='City', days=1) where days is ALWAYS a number",
                "- For air quality: use get_air_pollution(location='City')",
                "- If tool calls fail, use get_current_weather instead and explain limitation",
                "- DO NOT call weather tools for non-weather conversations (greetings, thanks, etc.)"
            ],
            markdown=False,  # Disable markdown for cleaner responses
            # Enable memory and session management
            session_id="weather_chat",
            session_state=self.session_state,
            add_session_state_to_context=True,
            add_history_to_context=True,
            num_history_runs=2  # Remember last 2 exchanges for context (reduced to prevent loops)
        )
        
        logger.info("🌤️  Weather Assistant initialized successfully!")
    
    def extract_location_from_message(self, message: str) -> Optional[str]:
        """Extract location from user message using enhanced patterns"""
        # Known cities for validation (small sample)
        known_cities = {'tokyo', 'london', 'paris', 'new york', 'delhi', 'mumbai', 'bangalore', 
                       'chicago', 'los angeles', 'miami', 'boston', 'seattle', 'sydney', 'melbourne',
                       'berlin', 'madrid', 'rome', 'moscow', 'beijing', 'shanghai', 'singapore',
                       'dubai', 'toronto', 'vancouver', 'montreal', 'cairo', 'jodhpur', 'pune', 'chennai'}
        
        location_patterns = [
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in Tokyo", "in New York"
            r'\bweather\s+(?:in\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "weather in Tokyo"
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:weather|forecast|today|tomorrow)',  # "Tokyo weather"
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[?\s]*$',  # Just city name like "Tokyo?"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message)
            if match:
                location = match.group(1).strip().title()
                # Validate against known cities or reasonable length
                if (location.lower() in known_cities or 
                    (len(location) > 2 and len(location) < 20 and not any(word in location.lower() for word in ['what', 'about', 'when', 'how', 'where', 'can', 'should']))):
                    return location
        
        return None
    
    def is_weather_related_query(self, message: str) -> bool:
        """Check if the message is actually asking about weather"""
        weather_keywords = ['weather', 'temperature', 'rain', 'snow', 'sunny', 'cloudy', 'forecast', 'humid', 'wind',
                           '天気', '気温', '雨', '雪', '晴れ', '曇り', '予報', '湿度', '風', '気候', '寒い', '暑い']
        
        # Check for explicit weather questions
        weather_questions = ['how is', 'what is', 'what\'s', 'how\'s', 'tell me about', 'どう', 'どんな', '教えて']
        
        message_lower = message.lower()
        
        # Check for thank you, greetings, or non-weather messages
        non_weather = ['thank', 'thanks', 'bye', 'goodbye', 'hello', 'hi', 'good morning', 'good evening',
                      'ありがとう', 'ありがとうございます', 'さようなら', 'こんにちは', 'こんばんは', 'おはよう']
        
        # If it's clearly a non-weather message, return False
        for phrase in non_weather:
            if phrase in message_lower:
                return False
        
        # If it contains weather keywords, likely weather-related
        for keyword in weather_keywords:
            if keyword in message_lower:
                return True
                
        # If it's a question about weather (contains question + weather keyword)
        for question in weather_questions:
            if question in message_lower:
                for keyword in weather_keywords:
                    if keyword in message_lower:
                        return True
        
        return False

    def process_message(self, message: str) -> str:
        """Process a single message through the agentic assistant"""
        try:
            # Update conversation count
            self.session_state["conversation_count"] += 1
            
            # Only extract location for weather-related queries
            if self.is_weather_related_query(message):
                extracted_location = self.extract_location_from_message(message)
                if extracted_location:
                    self.session_state["last_location"] = extracted_location
                    logger.info(f"💭 Extracted and remembered location: {extracted_location}")
                elif self.session_state["last_location"]:
                    logger.info(f"💭 Using remembered location: {self.session_state['last_location']}")
            else:
                logger.info(f"💭 Non-weather query detected, not extracting location")
            
            # Get response from the agent
            response = self.agent.run(
                message,
                session_state=self.session_state
            )
            
            # Extract the response content
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I apologize, but I encountered an error while processing your request. Please try again. Error: {str(e)}"
    
    def process_conversation(self, messages: List[Dict[str, str]], language: str = 'en') -> str:
        """Process a conversation with context from previous messages"""
        try:
            # Update language in session state
            self.session_state["language"] = language
            
            # Add conversation history to session state for context
            self.session_state["conversation_history"] = messages[-5:]  # Keep last 5 messages
            
            # Get the latest user message
            last_user_message = None
            for message in reversed(messages):
                if message["role"] == "user":
                    last_user_message = message["content"]
                    break
            
            if not last_user_message:
                if language == 'ja':
                    return "メッセージが受信されませんでした。天気について聞いてください！"
                else:
                    return "I didn't receive a message. Please ask me about the weather!"
            
            return self.process_message(last_user_message)
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            if language == 'ja':
                return f"申し訳ございませんが、会話の処理中にエラーが発生しました。もう一度お試しください。"
            else:
                return f"I apologize, but I encountered an error while processing your conversation. Please try again."

# Global weather assistant instance
weather_assistant = None

def get_weather_assistant():
    """Get or initialize the weather assistant (lazy loading for serverless)"""
    global weather_assistant
    if weather_assistant is None:
        try:
            weather_assistant = WeatherAssistant()
            logger.info("Weather Assistant initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Weather Assistant: {e}")
            weather_assistant = None
    return weather_assistant

@app.on_event("startup")
async def startup_event():
    """Initialize the weather assistant on startup"""
    # For serverless, we'll do lazy initialization instead
    logger.info("WeatherBot API starting up...")

# Weather-chat endpoint (main endpoint used by frontend)
@app.post("/api/weather-chat")
async def weather_chat(request: ChatRequest):
    """
    Main endpoint for weather chat - integrates weather info into the conversation
    """
    try:
        assistant = get_weather_assistant()
        if assistant is None:
            raise HTTPException(status_code=500, detail="Weather Assistant not initialized")
        
        logger.info("Processing weather-chat request")
        
        # Convert messages to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Process the conversation through the agentic assistant with language support
        response = assistant.process_conversation(messages, request.language)
        
        return {"response": response}
    
    except Exception as e:
        logger.error(f"Error in weather_chat endpoint: {str(e)}")
        return {"response": "I encountered an unexpected error. Please try again later."}

# Legacy endpoints for backward compatibility
@app.get("/api/weather/{city}")
async def get_weather(city: str):
    """Legacy endpoint for direct weather queries"""
    try:
        assistant = get_weather_assistant()
        if assistant is None:
            raise HTTPException(status_code=500, detail="Weather Assistant not initialized")
        
        response = assistant.process_message(f"What's the current weather in {city}?")
        
        # Try to return in expected format, but fallback to text response
        return {"description": response, "city": city}
    
    except Exception as e:
        logger.error(f"Error in get_weather endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """Legacy chat endpoint - redirects to weather-chat"""
    return await weather_chat(request)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    assistant = get_weather_assistant()
    return {
        "status": "ok",
        "weather_assistant": "initialized" if assistant else "not initialized"
    }

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "WeatherBot Agentic API",
        "version": "2.0.0",
        "endpoints": {
            "weather_chat": "/api/weather-chat",
            "weather": "/api/weather/{city}",
            "chat": "/api/chat",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 