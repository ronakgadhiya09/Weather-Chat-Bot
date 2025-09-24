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
  WiWindy
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
  IoStopOutline
} from 'react-icons/io5';
import { BsRobot } from 'react-icons/bs';
import { FaUser } from 'react-icons/fa';
import QuickSuggestions from './QuickSuggestions';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: 'Hello! I\'m your AI weather assistant. Ask me about the weather in any city around the world! 🌤️',
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
      .replace(/[🌤️⛅☀️🌧️❄️⛈️🌪️🌫️]/g, '') // Remove weather emojis
      .replace(/°C/g, ' degrees Celsius')
      .replace(/°F/g, ' degrees Fahrenheit')
      .replace(/\([^)]*\)/g, '') // Remove parentheses content
      .trim();
    
    if (!cleanText) return;
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;
    
    utterance.onstart = () => {
      setIsSpeaking(true);
    };
    
    utterance.onend = () => {
      setIsSpeaking(false);
    };
    
    utterance.onerror = () => {
      setIsSpeaking(false);
      console.error('Speech synthesis error');
    };
    
    synthesisRef.current.speak(utterance);
  }, [isVoiceEnabled]);

  // Stop speech synthesis
  const stopSpeech = useCallback(() => {
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
      setIsSpeaking(false);
    }
  }, []);

  // Start voice recognition
  const startListening = useCallback(() => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
      }
    }
  }, [isListening]);

  // Stop voice recognition
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  }, [isListening]);

  // Toggle voice features
  const toggleVoice = () => {
    setIsVoiceEnabled(prev => !prev);
    if (isVoiceEnabled) {
      stopSpeech();
    }
  };

  const getWeatherIcon = (description) => {
    const desc = description.toLowerCase();
    const isNight = new Date().getHours() >= 18 || new Date().getHours() <= 6;
    
    if (desc.includes('clear') || desc.includes('sunny')) {
      return isNight ? <WiNightClear /> : <WiDaySunny />;
    } else if (desc.includes('cloud')) {
      return isNight ? <WiNightAltCloudy /> : <WiCloudy />;
    } else if (desc.includes('rain') || desc.includes('drizzle')) {
      return isNight ? <WiNightAltRain /> : <WiRain />;
    } else if (desc.includes('snow')) {
      return <WiSnow />;
    } else if (desc.includes('thunder') || desc.includes('storm')) {
      return <WiThunderstorm />;
    } else if (desc.includes('fog') || desc.includes('mist') || desc.includes('haze')) {
      return <WiFog />;
    } else if (desc.includes('wind')) {
      return <WiWindy />;
    }
    return <WiDaySunny />;
  };

  const parseWeatherResponse = (content) => {
    // Extract weather information and add appropriate icons
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
      console.log("Sending request to backend with messages:", [...messages, userMessage]);
      
      // Send request to backend with 15s timeout
      const response = await axios.post('http://localhost:8000/api/weather-chat', {
        messages: [...messages, userMessage]
      }, { timeout: 15000 });
      
      console.log("Received response:", response.data);
      
      // Add AI response to chat
      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.response,
        timestamp: new Date()
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
      
      let errorMessage = 'Sorry, I encountered an error. Please try again later.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. The server might be busy. Please try again.';
      } else if (error.response) {
        console.error("Error data:", error.response.data);
        console.error("Error status:", error.response.status);
        errorMessage = `Server error (${error.response.status}). Please try again.`;
      } else if (error.request) {
        console.error("No response received:", error.request);
        errorMessage = "Couldn't connect to the server. Please check your connection.";
        setConnectionStatus('disconnected');
      } else {
        console.error("Error message:", error.message);
      }
      
      const errorAssistantMessage = { 
        role: 'assistant', 
        content: errorMessage,
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prevMessages => [
        ...prevMessages, 
        errorAssistantMessage
      ]);
      
      // Speak error message if voice is enabled
      if (isVoiceEnabled) {
        setTimeout(() => {
          speakText(errorMessage);
        }, 500);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <IoCheckmarkCircle className="status-icon connected" />;
      case 'disconnected':
        return <IoCloudOffline className="status-icon disconnected" />;
      case 'checking':
        return <IoWarning className="status-icon checking" />;
      default:
        return null;
    }
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className={`App ${isDarkMode ? 'dark' : 'light'}`}>
      <motion.header
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="header"
      >
        <div className="header-content">
          <div className="header-left">
            <BsRobot className="header-icon" />
            <h1>WeatherBot</h1>
            {getStatusIcon()}
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
                      ? parseWeatherResponse(msg.content) 
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
                  <span className="typing-text">WeatherBot is thinking...</span>
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
                  <span className="speaking-text">WeatherBot is speaking...</span>
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
              placeholder={isListening ? "Listening..." : "Ask about weather in any city..."}
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
