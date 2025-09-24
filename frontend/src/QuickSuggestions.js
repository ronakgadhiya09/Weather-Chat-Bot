import React from 'react';
import { motion } from 'framer-motion';
import { IoLocationSharp } from 'react-icons/io5';

const QuickSuggestions = ({ onSuggestionClick, isVisible }) => {
  const suggestions = [
    { city: 'New York', country: 'USA' },
    { city: 'London', country: 'UK' },
    { city: 'Tokyo', country: 'Japan' },
    { city: 'Paris', country: 'France' },
    { city: 'Sydney', country: 'Australia' },
    { city: 'Dubai', country: 'UAE' }
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
      <div className="suggestions-header">
        <IoLocationSharp className="location-icon" />
        <span>Quick weather for popular cities:</span>
      </div>
      <div className="suggestions-grid">
        {suggestions.map((suggestion, index) => (
          <motion.button
            key={`${suggestion.city}-${suggestion.country}`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="suggestion-chip"
            onClick={() => onSuggestionClick(`What's the weather like in ${suggestion.city}?`)}
          >
            <span className="city-name">{suggestion.city}</span>
            <span className="country-name">{suggestion.country}</span>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

export default QuickSuggestions; 