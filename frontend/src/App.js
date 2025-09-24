import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';
import { 
  WiDaySunny, 
  WiCloudy, 
  WiRain, 
  WiSnow, 
  WiThunderstorm, 
  WiFog,
  WiNightClear,
  WiNightAltCloudy,
  WiNightAltRain,
  WiWindy,
  WiHumidity,
  WiStrongWind
} from 'react-icons/wi';
import { 
  IoSend, 
  IoMoon, 
  IoSunny, 
  IoCloudOffline,
  IoWarning,
  IoCheckmarkCircle,
  IoMicOutline,
  IoMicOffOutline,
  IoVolumeHighOutline,
  IoVolumeMuteOutline,
  IoStopOutline,
  IoCheckmark,
  IoClose,
  IoTime,
  IoThermometer,
  IoEye
} from 'react-icons/io5';
import { 
  MdSportsBaseball, 
  MdDirectionsRun, 
  MdDirectionsWalk,
  MdDirectionsBike,
  MdOutdoorGrill,
  MdSportsSoccer 
} from 'react-icons/md';
import { BsRobot } from 'react-icons/bs';
import { FaUser } from 'react-icons/fa';
import QuickSuggestions from './QuickSuggestions';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: 'Hello! I\'m your enhanced AI weather assistant. Ask me about weather in any city, or get smart recommendations for activities! Try asking: "Can I play cricket in Mumbai this evening?" 🌤️⚡',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [showSuggestions, setShowSuggestions] = useState(true);
  
  // Voice feature states
  const [isListening, setIsListening] = useState(false);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(() => {
    const saved = localStorage.getItem('voiceEnabled');
    return saved ? JSON.parse(saved) : true;
  });
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [supportsSpeech, setSupportsSpeech] = useState(false);
  
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  // Test backend connection on load
  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        setConnectionStatus('checking');
        console.log("Testing connection to backend...");
        const response = await axios.get('http://localhost:8000/health', { timeout: 5000 });
        console.log("Backend health check:", response.data);
        setConnectionStatus('connected');
      } catch (error) {
        console.error("Error connecting to backend:", error);
        setConnectionStatus('disconnected');
      }
    };
    
    checkBackendConnection();
  }, []);

  // Initialize speech recognition and synthesis
  useEffect(() => {
    // Check for speech recognition support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      const recognition = recognitionRef.current;
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setIsListening(true);
        console.log('Speech recognition started');
      };
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Speech recognition result:', transcript);
        setInput(transcript);
        setIsListening(false);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
        console.log('Speech recognition ended');
      };
      
      setSupportsSpeech(true);
    }
    
    // Check for speech synthesis support
    if ('speechSynthesis' in window) {
      synthesisRef.current = window.speechSynthesis;
    }
    
    // Save voice preference
    localStorage.setItem('voiceEnabled', JSON.stringify(isVoiceEnabled));
  }, [isVoiceEnabled]);

  // Speech synthesis function
  const speakText = useCallback((text) => {
    if (!isVoiceEnabled || !synthesisRef.current) return;
    
    // Cancel any ongoing speech
    synthesisRef.current.cancel();
    
    // Clean text for better speech (remove emojis and special characters)
    const cleanText = text
      .replace(/[🌤️⚡🌟✅⚠️❌🔥💧🌡️]/g, '')
      .replace(/°C/g, ' degrees Celsius')
      .replace(/°F/g, ' degrees Fahrenheit')
      .replace(/m\/s/g, ' meters per second')
      .replace(/%/g, ' percent')
      .replace(/\s+/g, ' ')
      .trim();
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    
    synthesisRef.current.speak(utterance);
  }, [isVoiceEnabled]);

  const stopSpeech = () => {
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const toggleVoice = () => {
    setIsVoiceEnabled(!isVoiceEnabled);
    if (isSpeaking) {
      stopSpeech();
    }
  };

  const getWeatherIcon = (description) => {
    const desc = description.toLowerCase();
    const isNight = new Date().getHours() > 18 || new Date().getHours() < 6;
    
    if (desc.includes('clear')) {
      return isNight ? <WiNightClear /> : <WiDaySunny />;
    } else if (desc.includes('cloud')) {
      return isNight ? <WiNightAltCloudy /> : <WiCloudy />;
    } else if (desc.includes('rain') || desc.includes('drizzle')) {
      return isNight ? <WiNightAltRain /> : <WiRain />;
    } else if (desc.includes('snow')) {
      return <WiSnow />;
    } else if (desc.includes('thunder')) {
      return <WiThunderstorm />;
    } else if (desc.includes('mist') || desc.includes('fog') || desc.includes('haze')) {
      return <WiFog />;
    } else if (desc.includes('wind')) {
      return <WiWindy />;
    }
    return <WiDaySunny />;
  };

  const getActivityIcon = (activity) => {
    switch (activity?.toLowerCase()) {
      case 'cricket':
        return <MdSportsBaseball />;
      case 'football':
        return <MdSportsSoccer />;
      case 'running':
        return <MdDirectionsRun />;
      case 'walking':
        return <MdDirectionsWalk />;
      case 'cycling':
        return <MdDirectionsBike />;
      case 'picnic':
        return <MdOutdoorGrill />;
      default:
        return <MdSportsBaseball />;
    }
  };

  const getRecommendationIcon = (recommendation) => {
    switch (recommendation) {
      case 'excellent':
      case 'good':
        return <IoCheckmark className="rec-icon excellent" />;
      case 'moderate':
        return <IoWarning className="rec-icon moderate" />;
      case 'poor':
        return <IoClose className="rec-icon poor" />;
      default:
        return <IoEye className="rec-icon" />;
    }
  };

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'excellent':
        return '#10b981'; // green
      case 'good':
        return '#22c55e'; // light green
      case 'moderate':
        return '#f59e0b'; // yellow
      case 'poor':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  const renderActivityAdvice = (data) => {
    const { structured_data } = data;
    const { activity, city, recommendation, confidence, factors, current_weather } = structured_data;
    
    return (
      <div className="activity-advice-card">
        <div className="activity-header">
          <div className="activity-info">
            <span className="activity-icon">{getActivityIcon(activity)}</span>
            <div className="activity-details">
              <h3 className="activity-name">{activity.charAt(0).toUpperCase() + activity.slice(1)} in {city}</h3>
              <div className="recommendation-badge" style={{ background: getRecommendationColor(recommendation) }}>
                {getRecommendationIcon(recommendation)}
                <span>{recommendation.charAt(0).toUpperCase() + recommendation.slice(1)}</span>
                <span className="confidence">({confidence}%)</span>
              </div>
            </div>
          </div>
          <div className="current-temp">
            <IoThermometer />
            <span>{current_weather.temperature}</span>
          </div>
        </div>
        
        <div className="weather-factors">
          {factors.map((factor, index) => (
            <div key={index} className={`factor ${factor.impact}`}>
              <div className="factor-header">
                <span className="factor-name">{factor.factor.charAt(0).toUpperCase() + factor.factor.slice(1)}</span>
                <span className="factor-value">{factor.value}</span>
              </div>
              <div className="factor-bar">
                <div 
                  className="factor-progress" 
                  style={{ 
                    width: `${factor.score}%`,
                    background: factor.impact === 'excellent' ? '#10b981' : 
                               factor.impact === 'good' ? '#22c55e' :
                               factor.impact === 'moderate' ? '#f59e0b' : '#ef4444'
                  }}
                />
              </div>
            </div>
          ))}
        </div>
        
        <div className="weather-summary">
          <div className="weather-item">
            <WiHumidity />
            <span>{current_weather.humidity}</span>
          </div>
          <div className="weather-item">
            <WiStrongWind />
            <span>{current_weather.wind_speed}</span>
          </div>
          <div className="weather-item">
            <span className="weather-desc">{current_weather.description}</span>
          </div>
        </div>
      </div>
    );
  };

  const renderEnhancedWeather = (data) => {
    const { structured_data } = data;
    const { city, current_weather } = structured_data;
    const icon = getWeatherIcon(current_weather.description);
    
    return (
      <div className="enhanced-weather-card">
        <div className="weather-header">
          <span className="weather-icon">{icon}</span>
          <span className="city-name">{city}</span>
        </div>
        <div className="weather-details">
          <div className="temperature">{current_weather.temperature}</div>
          <div className="description">{current_weather.description}</div>
        </div>
        <div className="additional-info">
          <div className="info-item">
            <span>Feels like {current_weather.feels_like}</span>
          </div>
          <div className="info-item">
            <WiHumidity />
            <span>{current_weather.humidity}</span>
          </div>
          <div className="info-item">
            <WiStrongWind />
            <span>{current_weather.wind_speed}</span>
          </div>
        </div>
      </div>
    );
  };

  const parseResponse = (content, responseData = null) => {
    // Check if this is a structured response from the new API
    if (responseData && responseData.response_type) {
      switch (responseData.response_type) {
        case 'activity_advice':
          return renderActivityAdvice(responseData);
        case 'enhanced_weather':
          return renderEnhancedWeather(responseData);
        default:
          break;
      }
    }
    
    // Fallback to original weather parsing for backward compatibility
    const weatherPattern = /Weather in ([^:]+): ([^.]+)\. Temperature: ([^°]+)°C/;
    const match = content.match(weatherPattern);
    
    if (match) {
      const [, city, description, temp] = match;
      const icon = getWeatherIcon(description);
      return (
        <div className="weather-response">
          <div className="weather-header">
            <span className="weather-icon">{icon}</span>
            <span className="city-name">{city}</span>
          </div>
          <div className="weather-details">
            <div className="temperature">{temp}°C</div>
            <div className="description">{description}</div>
          </div>
          {content.includes('feels like') && (
            <div className="additional-info">
              {content.match(/feels like ([^°]+)°C/)?.[0]}
              {content.includes('Humidity') && (
                <span> • {content.match(/Humidity: (\d+%)/)?.[0]}</span>
              )}
            </div>
          )}
        </div>
      );
    }
    
    return content;
  };

  const handleSuggestionClick = (suggestionText) => {
    setInput(suggestionText);
    setShowSuggestions(false);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    setShowSuggestions(false);
    
    // Add user message to chat
    const userMessage = { 
      role: 'user', 
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInput('');
    
    try {
      console.log("Sending request to enhanced backend with messages:", [...messages, userMessage]);
      
      // Use the new smart weather chat endpoint
      const response = await axios.post('http://localhost:8000/api/smart-weather-chat', {
        messages: [...messages, userMessage]
      }, { timeout: 20000 }); // Increased timeout for complex processing
      
      console.log("Received enhanced response:", response.data);
      
      // Add AI response to chat with enhanced data
      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.response,
        timestamp: new Date(),
        responseData: response.data // Store the full response for enhanced rendering
      };
      
      setMessages(prevMessages => [
        ...prevMessages, 
        assistantMessage
      ]);
      
      // Speak the AI response if voice is enabled
      if (isVoiceEnabled && response.data.response) {
        // Small delay to ensure message is rendered before speaking
        setTimeout(() => {
          speakText(response.data.response);
        }, 500);
      }
      
      setConnectionStatus('connected');
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Enhanced error handling
      let errorMessage = "I'm having trouble connecting to the weather service. ";
      if (error.code === 'ECONNABORTED') {
        errorMessage += "The request timed out. Please try again.";
      } else if (error.response?.status === 404) {
        errorMessage += "I couldn't find information for that location.";
      } else if (error.response?.status >= 500) {
        errorMessage += "There's an issue with the weather service. Please try again later.";
      } else {
        errorMessage += "Please check your connection and try again.";
      }
      
      const errorMsg = { 
        role: 'assistant', 
        content: errorMessage,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prevMessages => [...prevMessages, errorMsg]);
      setConnectionStatus('disconnected');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <motion.header 
        className="header"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="header-content">
          <div className="header-left">
            <motion.span 
              className="header-icon"
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            >
              🌤️
            </motion.span>
            <h1>Smart WeatherBot</h1>
            <motion.span 
              className={`status-icon ${connectionStatus}`}
              animate={connectionStatus === 'checking' ? { scale: [1, 1.2, 1] } : {}}
              transition={{ duration: 1, repeat: Infinity }}
            >
              {connectionStatus === 'connected' && <IoCheckmarkCircle />}
              {connectionStatus === 'disconnected' && <IoCloudOffline />}
              {connectionStatus === 'checking' && <IoWarning />}
            </motion.span>
          </div>
          <div className="header-controls">
            {supportsSpeech && (
              <div className="voice-controls">
                <button 
                  onClick={toggleVoice}
                  className={`voice-toggle ${isVoiceEnabled ? 'enabled' : 'disabled'}`}
                  title={isVoiceEnabled ? 'Disable voice' : 'Enable voice'}
                >
                  {isVoiceEnabled ? <IoVolumeHighOutline /> : <IoVolumeMuteOutline />}
                </button>
                {isSpeaking && (
                  <button 
                    onClick={stopSpeech}
                    className="stop-speech"
                    title="Stop speaking"
                  >
                    <IoStopOutline />
                  </button>
                )}
              </div>
            )}
            <button onClick={toggleTheme} className="theme-toggle">
              {isDarkMode ? <IoSunny /> : <IoMoon />}
            </button>
          </div>
        </div>
      </motion.header>
      
      <div className="chat-container">
        <div className="messages">
          <QuickSuggestions 
            onSuggestionClick={handleSuggestionClick}
            isVisible={showSuggestions && messages.length === 1}
          />
          <AnimatePresence>
            {messages.map((msg, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20, scale: 0.9 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.9 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}
              >
                <div className="message-avatar">
                  {msg.role === 'user' ? <FaUser /> : <BsRobot />}
                </div>
                <div className="message-bubble">
                  <div className="message-content">
                    {msg.role === 'assistant' && !msg.isError 
                      ? parseResponse(msg.content, msg.responseData) 
                      : msg.content
                    }
                  </div>
                  <div className="message-timestamp">
                    {format(msg.timestamp, 'HH:mm')}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="message assistant typing"
            >
              <div className="message-avatar">
                <BsRobot />
              </div>
              <div className="message-bubble">
                <div className="typing-indicator">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="typing-text">Smart WeatherBot is analyzing...</span>
                </div>
              </div>
            </motion.div>
          )}
          
          {isSpeaking && !isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="message assistant speaking"
            >
              <div className="message-avatar">
                <BsRobot />
              </div>
              <div className="message-bubble">
                <div className="speaking-indicator">
                  <div className="sound-waves">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="speaking-text">Smart WeatherBot is speaking...</span>
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <motion.form 
          onSubmit={sendMessage} 
          className="input-form"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isListening ? "Listening..." : "Ask about weather or activities... e.g., 'Can I play cricket in Surat this evening?'"}
              disabled={isLoading || isListening}
              className="message-input"
            />
            {supportsSpeech && (
              <motion.button 
                type="button"
                onClick={isListening ? stopListening : startListening}
                disabled={isLoading}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`mic-button ${isListening ? 'listening' : ''}`}
                title={isListening ? 'Stop listening' : 'Start voice input'}
              >
                {isListening ? <IoMicOffOutline /> : <IoMicOutline />}
              </motion.button>
            )}
            <motion.button 
              type="submit" 
              disabled={isLoading || !input.trim() || isListening}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="send-button"
            >
              <IoSend />
            </motion.button>
          </div>
        </motion.form>
      </div>
    </div>
  );
}

export default App;
