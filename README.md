# Smart WeatherBot 2.0 🌤️⚡

An intelligent weather chatbot that provides comprehensive weather information and smart activity recommendations using AI-powered analysis.

## 🌟 Features

### Core Weather Features
- **Real-time Weather Data**: Current weather conditions for any city worldwide
- **Extended Forecasts**: Hourly and daily weather predictions
- **Interactive Chat Interface**: Natural language conversation with AI
- **Voice Integration**: Speech-to-text input and text-to-speech output
- **Dark/Light Theme**: Toggle between themes for better user experience

### 🚀 NEW: Smart Activity Planning
- **Activity Recommendations**: Get personalized advice for outdoor activities
- **Weather Suitability Analysis**: AI analyzes multiple weather factors
- **Confidence Scoring**: Percentage-based recommendations with reasoning
- **Complex Query Handling**: Ask questions like "Can I play cricket in Mumbai this evening?"

### 🎯 Supported Activities
- **Sports**: Cricket, Football, Tennis, Basketball
- **Fitness**: Running, Cycling, Walking, Hiking
- **Recreation**: Picnics, Outdoor dining, Sightseeing
- **Indoor Alternatives**: Shopping, Movies (when weather is unsuitable)

### 💡 Smart Features
- **Multi-factor Analysis**: Temperature, humidity, wind, precipitation
- **Time-aware Recommendations**: Morning, afternoon, evening contexts
- **Visual Progress Indicators**: Factor-based suitability scores
- **Enhanced UI Cards**: Rich visual feedback for recommendations

## 🔧 Tech Stack

- **Frontend**: React, Framer Motion, React Icons
- **Backend**: FastAPI, Python
- **AI**: OpenAI GPT-3.5-turbo
- **Weather API**: OpenWeatherMap API
- **Styling**: Modern CSS with Glassmorphism effects

## 📋 Prerequisites

- Node.js (v14+) and npm
- Python 3.8+ and pip
- OpenAI API Key
- OpenWeatherMap API Key

## 🛠️ Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment configuration:**
   Create `config.env` file in the backend directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

5. **Run the backend server:**
   ```bash
   python run.py
   ```
   Server will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   App will open on `http://localhost:3000`

## 🎮 Usage Examples

### Basic Weather Queries
- "What's the weather like in London?"
- "How's the temperature in New York?"
- "Is it raining in Tokyo right now?"

### 🆕 Smart Activity Planning
- "Can I play cricket in Mumbai this evening?"
- "Is it good weather for running in Delhi?"
- "Should I go cycling in Bangalore today?"
- "Can I have a picnic in Chennai tomorrow?"
- "Is it suitable for football in Pune right now?"

### Enhanced Queries
- "I'm in Surat, can I go play cricket in the evening?"
- "What should I wear for a morning jog in Paris?"
- "Is it too windy for cycling in Amsterdam?"

## 📡 API Endpoints

### Enhanced Endpoints

- **`POST /api/smart-weather-chat`** - Main endpoint for complex queries
  - Handles activity planning and smart recommendations
  - Returns structured data with confidence scores

- **`GET /api/weather-forecast/{city}`** - Extended forecast data
  - Hourly and daily weather predictions
  - Enhanced weather metrics

### Legacy Endpoints (Maintained for compatibility)

- **`GET /api/weather/{city}`** - Basic weather data
- **`POST /api/weather-chat`** - Simple weather chat
- **`POST /api/chat`** - General AI chat
- **`GET /health`** - Health check with version info

## 🎨 UI Components

### Activity Recommendation Cards
- **Visual Indicators**: Color-coded recommendation badges
- **Progress Bars**: Factor-based suitability analysis
- **Icons**: Activity-specific visual elements
- **Confidence Scores**: Percentage-based recommendations

### Enhanced Weather Cards
- **Animated Icons**: Weather-appropriate visual feedback
- **Comprehensive Data**: Temperature, humidity, wind, description
- **Responsive Design**: Mobile-optimized layouts

### Smart Suggestions
- **Quick Weather**: Popular cities for instant weather
- **Activity Examples**: Pre-built complex queries
- **Interactive Elements**: Hover effects and animations

## 🌈 Activity Analysis System

### Scoring Factors
1. **Temperature Range**: Activity-specific optimal temperatures
2. **Wind Conditions**: Maximum tolerable wind speeds
3. **Precipitation**: Rain/snow tolerance levels
4. **Humidity**: Comfort-based assessments
5. **Time Context**: Daylight and timing requirements

### Recommendation Levels
- **🌟 Excellent (85-100%)**: Perfect conditions
- **✅ Good (70-84%)**: Suitable with minor considerations
- **⚠️ Moderate (50-69%)**: Possible but not ideal
- **❌ Poor (<50%)**: Not recommended

## 🎯 Query Classification

The system automatically classifies queries into:
- **BASIC_WEATHER**: Simple weather information
- **ACTIVITY_PLANNING**: Activity suitability analysis
- **CLOTHING_ADVICE**: What to wear recommendations
- **TRAVEL_PLANNING**: Trip and vacation planning
- **COMFORT_ASSESSMENT**: General weather comfort

## 🔮 Future Enhancements

- **Air Quality Integration**: Pollution data for health-conscious activities
- **UV Index Warnings**: Sun exposure recommendations
- **Seasonal Activity Suggestions**: Context-aware activity recommendations
- **Location-based Services**: GPS integration for current location
- **Weather Alerts**: Push notifications for weather changes
- **Historical Weather Analysis**: Trend-based recommendations

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Check if backend server is running on port 8000
   - Verify API keys are correctly set in config.env

2. **API Key Errors**
   - Ensure OpenAI API key has sufficient credits
   - Check OpenWeatherMap API key validity

3. **City Not Found**
   - Try alternative city spellings
   - Include country name for clarity

4. **Voice Features Not Working**
   - Enable microphone permissions in browser
   - Check browser compatibility (Chrome recommended)

### Development Tips

- Use browser developer tools to monitor API calls
- Check console logs for detailed error messages
- Verify environment variables are loaded correctly

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review API documentation

---

**Made with ❤️ using React, FastAPI, and OpenAI**

*Smart WeatherBot 2.0 - Your intelligent weather companion! 🌤️⚡* 