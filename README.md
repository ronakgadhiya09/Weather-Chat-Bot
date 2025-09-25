# WeatherBot 🌤️

A beautiful AI-powered weather chatbot with Japanese language support and voice features.

## Features

- 🤖 **AI Weather Assistant** - Get weather information for any city
- 🗣️ **Voice Support** - Speak your questions and hear responses
- 🌏 **Japanese Language** - Full Japanese interface and voice support
- 🎨 **Beautiful UI** - Modern, responsive design with animations
- 🌙 **Dark/Light Mode** - Toggle between themes

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- API Keys (OpenAI, OpenWeather, Groq)

### 1. Setup Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `backend/env.example` to `backend/config.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_key
OPENWEATHER_API_KEY=your_openweather_key
GROQ_API_KEY=your_groq_key
```

### 3. Setup Frontend

```bash
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Visit http://localhost:3000 to use your WeatherBot!

## Usage

1. **Ask about weather**: "What's the weather like in Tokyo?"
2. **Switch languages**: Click the language toggle (EN/JA)
3. **Use voice**: Click the microphone icon and speak
4. **Toggle theme**: Click the sun/moon icon

## Project Structure

```
WeatherBot/
├── backend/           # Python FastAPI backend
│   ├── app/          # Application code
│   ├── venv/         # Virtual environment
│   └── run.py        # Start script
├── frontend/         # React frontend
│   ├── src/          # Source code
│   └── public/       # Static files
└── README.md         # This file
```

## API Keys Required

- **OpenAI**: For AI chat responses
- **OpenWeather**: For weather data
- **Groq**: Alternative AI model (optional)

Get your keys from:
- [OpenAI](https://platform.openai.com/api-keys)
- [OpenWeather](https://openweathermap.org/api)
- [Groq](https://console.groq.com/keys)

That's it! Enjoy your WeatherBot! 🚀 