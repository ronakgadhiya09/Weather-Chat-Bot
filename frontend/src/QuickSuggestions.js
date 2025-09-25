import React from 'react';
import { motion } from 'framer-motion';
import { IoLocationSharp } from 'react-icons/io5';

const QuickSuggestions = ({ onSuggestionClick, isVisible, language = 'en' }) => {
  const suggestions = [
    { city: 'New York', country: 'USA' },
    { city: 'London', country: 'UK' },
    { city: 'Tokyo', country: 'Japan' },
    { city: 'Paris', country: 'France' },
    { city: 'Sydney', country: 'Australia' },
    { city: 'Dubai', country: 'UAE' }
  ];

  const translations = {
    en: {
      header: 'Quick weather for popular cities:',
      questionTemplate: (city) => `What's the weather like in ${city}?`
    },
    ja: {
      header: '人気都市の天気をすぐに確認:',
      questionTemplate: (city) => `${city}の天気はどうですか？`
    }
  };

  const t = translations[language];

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
        <span>{t.header}</span>
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
            onClick={() => onSuggestionClick(t.questionTemplate(suggestion.city))}
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