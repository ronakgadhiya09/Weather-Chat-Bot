import React from 'react';
import { motion } from 'framer-motion';
import { IoLocationSharp, IoFitnessSharp } from 'react-icons/io5';

const QuickSuggestions = ({ onSuggestionClick, isVisible }) => {
  const weatherSuggestions = [
    { city: 'New York', country: 'USA' },
    { city: 'London', country: 'UK' },
    { city: 'Tokyo', country: 'Japan' },
    { city: 'Paris', country: 'France' },
    { city: 'Sydney', country: 'Australia' },
    { city: 'Dubai', country: 'UAE' }
  ];

  const activitySuggestions = [
    'Can I play cricket in Mumbai this evening?',
    'Is it good weather for running in Delhi?',
    'Should I go cycling in Bangalore today?',
    'Can I have a picnic in Chennai tomorrow?',
    'Is it suitable for football in Pune?',
    'Good weather for walking in Kolkata?'
  ];

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
      className="quick-suggestions"
    >
      <div className="suggestions-section">
        <div className="suggestions-header">
          <IoLocationSharp className="location-icon" />
          <span>Quick weather for popular cities:</span>
        </div>
        <div className="suggestions-grid">
          {weatherSuggestions.map((suggestion, index) => (
            <motion.button
              key={`weather-${suggestion.city}-${suggestion.country}`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="suggestion-chip weather-chip"
              onClick={() => onSuggestionClick(`What's the weather like in ${suggestion.city}?`)}
            >
              <span className="city-name">{suggestion.city}</span>
              <span className="country-name">{suggestion.country}</span>
            </motion.button>
          ))}
        </div>
      </div>

      <div className="suggestions-section">
        <div className="suggestions-header">
          <IoFitnessSharp className="location-icon" />
          <span>Try smart activity planning:</span>
        </div>
        <div className="activity-suggestions">
          {activitySuggestions.map((suggestion, index) => (
            <motion.button
              key={`activity-${index}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              className="activity-suggestion-chip"
              onClick={() => onSuggestionClick(suggestion)}
            >
              {suggestion}
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default QuickSuggestions; 