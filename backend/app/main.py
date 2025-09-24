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
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.groq import Groq
from agno.tools.openweather import OpenWeatherTools
from weather_tools_fixed import FixedWeatherTools

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

class WeatherAssistant:
    """Weather Assistant using Agno framework with memory"""
    
    def __init__(self):
        """Initialize the Weather Assistant"""
        # Initialize session state for simple memory
        self.session_state = {
            "last_location": None,
            "conversation_count": 0,
            "conversation_history": []
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
                "MEMORY & CONTEXT RULES:",
                "- Check session_state['last_location'] for the user's previously mentioned city",
                "- For follow-up questions like 'tomorrow?', 'cycling?', 'what about...', use last_location",
                "- If user asks about activities/weather without location, use last_location from session_state",
                "- If no location in session_state and none mentioned, ask for their city",
                "- Session state contains: last_location and conversation_count",
                "- NEVER treat words like 'tomorrow', 'what about', 'cycling' as locations",
                "TOOL USAGE RULES:",
                "- For current weather: use get_current_weather(location='City')",
                "- For forecasts: use get_forecast(location='City', days=1) where days is ALWAYS a number",
                "- For air quality: use get_air_pollution(location='City')",
                "- If tool calls fail, use get_current_weather instead and explain limitation"
            ],
            markdown=False,  # Disable markdown for cleaner responses
            # Enable memory and session management
            session_id="weather_chat",
            session_state=self.session_state,
            add_session_state_to_context=True,
            add_history_to_context=True,
            num_history_runs=3  # Remember last 3 exchanges for context
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
    
    def process_message(self, message: str) -> str:
        """Process a single message through the agentic assistant"""
        try:
            # Update conversation count
            self.session_state["conversation_count"] += 1
            
            # Extract location if mentioned and update session state
            extracted_location = self.extract_location_from_message(message)
            if extracted_location:
                self.session_state["last_location"] = extracted_location
                logger.info(f"💭 Extracted and remembered location: {extracted_location}")
            elif self.session_state["last_location"]:
                logger.info(f"💭 Using remembered location: {self.session_state['last_location']}")
            
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
    
    def process_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Process a conversation with context from previous messages"""
        try:
            # Add conversation history to session state for context
            self.session_state["conversation_history"] = messages[-5:]  # Keep last 5 messages
            
            # Get the latest user message
            last_user_message = None
            for message in reversed(messages):
                if message["role"] == "user":
                    last_user_message = message["content"]
                    break
            
            if not last_user_message:
                return "I didn't receive a message. Please ask me about the weather!"
            
            return self.process_message(last_user_message)
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return f"I apologize, but I encountered an error while processing your conversation. Please try again."

# Global weather assistant instance
weather_assistant = None

@app.on_event("startup")
async def startup_event():
    """Initialize the weather assistant on startup"""
    global weather_assistant
    try:
        weather_assistant = WeatherAssistant()
        logger.info("Weather Assistant initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Weather Assistant: {e}")
        weather_assistant = None

# Weather-chat endpoint (main endpoint used by frontend)
@app.post("/api/weather-chat")
async def weather_chat(request: ChatRequest):
    """
    Main endpoint for weather chat - integrates weather info into the conversation
    """
    try:
        if weather_assistant is None:
            raise HTTPException(status_code=500, detail="Weather Assistant not initialized")
        
        logger.info("Processing weather-chat request")
        
        # Convert messages to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Process the conversation through the agentic assistant
        response = weather_assistant.process_conversation(messages)
        
        return {"response": response}
    
    except Exception as e:
        logger.error(f"Error in weather_chat endpoint: {str(e)}")
        return {"response": "I encountered an unexpected error. Please try again later."}

# Legacy endpoints for backward compatibility
@app.get("/api/weather/{city}")
async def get_weather(city: str):
    """Legacy endpoint for direct weather queries"""
    try:
        if weather_assistant is None:
            raise HTTPException(status_code=500, detail="Weather Assistant not initialized")
        
        response = weather_assistant.process_message(f"What's the current weather in {city}?")
        
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
    return {
        "status": "ok",
        "weather_assistant": "initialized" if weather_assistant else "not initialized"
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