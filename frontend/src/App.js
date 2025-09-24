import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  console.log("App component rendered");
  
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your weather assistant. Ask me about the weather in any city!' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Test backend connection on load
  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        console.log("Testing connection to backend...");
        const response = await axios.get('http://localhost:8000/health');
        console.log("Backend health check:", response.data);
      } catch (error) {
        console.error("Error connecting to backend:", error);
      }
    };
    
    checkBackendConnection();
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setIsLoading(true);
    setInput('');
    
    try {
      console.log("Sending request to backend with messages:", [...messages, userMessage]);
      
      // Send request to backend with 10s timeout
      const response = await axios.post('http://localhost:8000/api/weather-chat', {
        messages: [...messages, userMessage]
      }, { timeout: 10000 });
      
      console.log("Received response:", response.data);
      
      // Add AI response to chat
      setMessages(prevMessages => [
        ...prevMessages, 
        { role: 'assistant', content: response.data.response }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      let errorMessage = 'Sorry, I encountered an error. Please try again later.';
      
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error("Error data:", error.response.data);
        console.error("Error status:", error.response.status);
        errorMessage = `Server error (${error.response.status}). Please try again.`;
      } else if (error.request) {
        // The request was made but no response was received
        console.error("No response received:", error.request);
        errorMessage = "Couldn't connect to the server. Please check your connection.";
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error("Error message:", error.message);
      }
      
      setMessages(prevMessages => [
        ...prevMessages, 
        { role: 'assistant', content: errorMessage }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header>
        <h1>Weather Chatbot</h1>
      </header>
      
      <div className="chat-container">
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <span className="message-content">{msg.content}</span>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <span className="message-content loading">Thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <form onSubmit={sendMessage} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the weather..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
