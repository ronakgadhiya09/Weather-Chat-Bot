# Weather Chatbot

A simple chatbot that provides weather information for cities using OpenAI and OpenWeather APIs.

## Features

- Chat interface to ask about weather in any city
- Uses OpenAI to process natural language queries
- Fetches real-time weather data from OpenWeather API
- Simple, responsive UI

## Tech Stack

- **Frontend**: React
- **Backend**: FastAPI
- **APIs**: OpenAI API, OpenWeather API

## Prerequisites

- Node.js and npm
- Python 3.8+ and pip
- OpenAI API Key
- OpenWeather API Key

## Setup

### Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `config.env` file in the backend directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

4. Run the backend server:
   ```
   python run.py
   ```

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the frontend development server:
   ```
   npm start
   ```

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Type a message asking about the weather in a city, for example:
   - "What's the weather like in London?"
   - "Is it raining in Tokyo right now?"
   - "How's the temperature in New York?"

## API Endpoints

- `GET /api/weather/{city}`: Get weather data for a specific city
- `POST /api/chat`: General chat with AI
- `POST /api/weather-chat`: Chat about weather with AI, which will extract city and provide weather data
- `GET /health`: Health check endpoint 