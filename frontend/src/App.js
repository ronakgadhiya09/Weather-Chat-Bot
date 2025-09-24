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
  IoStopOutline,
  IoLanguageOutline
} from 'react-icons/io5';
import { BsRobot } from 'react-icons/bs';
import { FaUser } from 'react-icons/fa';
import QuickSuggestions from './QuickSuggestions';
import './App.css';

// Language translations
const translations = {
  en: {
    title: 'WeatherBot',
    welcomeMessage: 'Hello! I\'m your AI weather assistant. Ask me about the weather in any city around the world! 🌤️',
    placeholder: 'Ask about weather in any city...',
    listeningPlaceholder: 'Listening...',
    typingIndicator: 'WeatherBot is thinking...',
    speakingIndicator: 'WeatherBot is speaking...',
    voiceTooltips: {
      enable: 'Enable voice',
      disable: 'Disable voice',
      startListening: 'Start voice input',
      stopListening: 'Stop listening',
      stopSpeaking: 'Stop speaking'
    }
  },
  ja: {
    title: 'ウェザーボット',
    welcomeMessage: 'こんにちは！私はあなたのAI天気アシスタントです。世界中のどの都市の天気についても聞いてください！ 🌤️',
    placeholder: 'どの都市の天気について聞きますか...',
    listeningPlaceholder: '聞いています...',
    typingIndicator: 'ウェザーボットが考えています...',
    speakingIndicator: 'ウェザーボットが話しています...',
    voiceTooltips: {
      enable: '音声を有効にする',
      disable: '音声を無効にする',
      startListening: '音声入力を開始',
      stopListening: '聞くのを止める',
      stopSpeaking: '話すのを止める'
    }
  }
};

function App() {
  // Language state
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    const saved = localStorage.getItem('language');
    return saved || 'en';
  });
  
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: translations[currentLanguage].welcomeMessage,
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

  // Language change effect
  useEffect(() => {
    localStorage.setItem('language', currentLanguage);
    // Update welcome message when language changes
    setMessages(prev => [
      {
        role: 'assistant',
        content: translations[currentLanguage].welcomeMessage,
        timestamp: new Date()
      },
      ...prev.slice(1) // Keep all messages except the welcome message
    ]);
  }, [currentLanguage]);

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
      recognition.lang = currentLanguage === 'ja' ? 'ja-JP' : 'en-US';
      
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
  }, [isVoiceEnabled, currentLanguage]);

  // Speech synthesis function
  const speakText = useCallback((text) => {
    if (!isVoiceEnabled || !synthesisRef.current) return;
    
    // Cancel any ongoing speech
    synthesisRef.current.cancel();
    
    // Clean text for better speech (remove emojis and special characters)
    const cleanText = text
      .replace(/[🌤️⛅☀️🌧️❄️⛈️🌪️🌫️]/g, '') // Remove weather emojis
      .replace(/°C/g, currentLanguage === 'ja' ? '度' : ' degrees Celsius')
      .replace(/°F/g, currentLanguage === 'ja' ? '華氏度' : ' degrees Fahrenheit')
      .replace(/\([^)]*\)/g, '') // Remove parentheses content
      .trim();
    
    if (!cleanText) return;
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;
    
    // Set language for speech synthesis
    utterance.lang = currentLanguage === 'ja' ? 'ja-JP' : 'en-US';
    
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
  }, [isVoiceEnabled, currentLanguage]);

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
        // Update language for recognition
        recognitionRef.current.lang = currentLanguage === 'ja' ? 'ja-JP' : 'en-US';
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
      }
    }
  }, [isListening, currentLanguage]);

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

  // Toggle language
  const toggleLanguage = () => {
    const newLanguage = currentLanguage === 'en' ? 'ja' : 'en';
    setCurrentLanguage(newLanguage);
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
      
      // Send request to backend with 15s timeout, including language information
      const response = await axios.post('http://localhost:8000/api/weather-chat', {
        messages: [...messages, userMessage],
        language: currentLanguage
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

  const t = translations[currentLanguage]; // Translation helper

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
            <h1>{t.title}</h1>
            {getStatusIcon()}
          </div>
          <div className="header-controls">
            <button 
              onClick={toggleLanguage}
              className="language-toggle"
              title={`Switch to ${currentLanguage === 'en' ? 'Japanese' : 'English'}`}
            >
              <IoLanguageOutline />
              <span className="language-code">{currentLanguage.toUpperCase()}</span>
            </button>
            {supportsSpeech && (
              <div className="voice-controls">
                <button 
                  onClick={toggleVoice}
                  className={`voice-toggle ${isVoiceEnabled ? 'enabled' : 'disabled'}`}
                  title={isVoiceEnabled ? t.voiceTooltips.disable : t.voiceTooltips.enable}
                >
                  {isVoiceEnabled ? <IoVolumeHighOutline /> : <IoVolumeMuteOutline />}
                </button>
                {isSpeaking && (
                  <button 
                    onClick={stopSpeech}
                    className="stop-speech"
                    title={t.voiceTooltips.stopSpeaking}
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
            language={currentLanguage}
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
                  <span className="typing-text">{t.typingIndicator}</span>
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
                  <span className="speaking-text">{t.speakingIndicator}</span>
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
              placeholder={isListening ? t.listeningPlaceholder : t.placeholder}
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
                title={isListening ? t.voiceTooltips.stopListening : t.voiceTooltips.startListening}
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
