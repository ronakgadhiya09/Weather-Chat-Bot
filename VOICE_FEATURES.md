# Voice Features for WeatherBot 🎤🔊

## Overview
WeatherBot now includes comprehensive voice features that allow users to interact with the weather assistant using speech input and receive spoken responses.

## Features Added

### 🎤 Speech-to-Text (Voice Input)
- **Microphone Button**: Green microphone icon next to the send button
- **Voice Recognition**: Uses Web Speech API for real-time speech recognition
- **Visual Feedback**: 
  - Button turns red when listening
  - Pulsing animation during recording
  - Input placeholder changes to "Listening..."
  - Input field is disabled during voice input

### 🔊 Text-to-Speech (Voice Output)
- **Automatic Speech**: AI responses are automatically spoken when voice is enabled
- **Clean Text Processing**: Removes emojis and special characters for better pronunciation
- **Temperature Conversion**: "°C" is spoken as "degrees Celsius"
- **Speaking Indicator**: Shows sound wave animation when bot is speaking

### 🎛️ Voice Controls
- **Voice Toggle**: Speaker/mute button in header to enable/disable voice features
- **Stop Speech**: Red stop button appears when bot is speaking
- **Voice Preference**: Setting is saved in localStorage and persists across sessions

## Browser Support
- **Speech Recognition**: Chrome, Edge, Safari (requires HTTPS in production)
- **Speech Synthesis**: All modern browsers
- **Fallback**: Voice features gracefully degrade if not supported

## Usage Instructions

### For Users:
1. **Enable Voice**: Click the speaker icon in the header (enabled by default)
2. **Voice Input**: Click the microphone button and speak your weather question
3. **Listen to Responses**: The bot will automatically speak responses
4. **Stop Speech**: Click the stop button if you want to interrupt the speech
5. **Disable Voice**: Click the mute icon to turn off all voice features

### Technical Details:

#### Speech Recognition Configuration:
- Language: English (en-US)
- Continuous: false (single utterance)
- Interim Results: false (final results only)

#### Speech Synthesis Configuration:
- Rate: 0.9 (slightly slower for clarity)
- Pitch: 1.0 (normal pitch)
- Volume: 0.8 (comfortable level)

## File Changes Made

### Frontend (`frontend/src/App.js`):
- Added voice-related state variables and refs
- Implemented speech recognition and synthesis functions
- Added voice controls to header and input form
- Integrated voice feedback with chat functionality

### CSS (`frontend/src/App.css`):
- Voice control buttons with hover effects
- Microphone button with listening animation
- Speaking indicator with sound wave animation
- Responsive design for mobile devices

## Visual Indicators

### Voice States:
- 🟢 **Voice Enabled**: Green speaker icon
- 🔴 **Voice Disabled**: Red mute icon
- 🎤 **Listening**: Pulsing red microphone with ring animation
- 🔊 **Speaking**: Sound wave bars animation

### UI Feedback:
- Input field shows "Listening..." when recording
- Send button is disabled during voice input
- Speaking indicator appears below messages when bot is talking
- Stop button appears in header during speech output

## Error Handling
- Graceful degradation when speech APIs are not supported
- Error logging for speech recognition failures
- Automatic fallback to text-only interaction
- User-friendly error messages

## Privacy & Security
- Speech recognition is processed locally by the browser
- No audio data is sent to external services (except browser's speech API)
- Voice preferences are stored locally only
- Users can disable voice features at any time

## Future Enhancements
- Voice command shortcuts ("stop", "repeat", "louder")
- Multiple language support
- Voice speed/pitch controls
- Wake word detection
- Offline speech recognition
- Custom voice selection

## Troubleshooting

### Common Issues:
1. **Microphone not working**: Check browser permissions for microphone access
2. **No speech output**: Verify browser supports speech synthesis
3. **Recognition errors**: Ensure clear speech and minimal background noise
4. **HTTPS required**: Speech recognition may require HTTPS in production

### Browser Compatibility:
- Chrome/Chromium: Full support
- Firefox: Speech synthesis only (no recognition)
- Safari: Full support (iOS requires user interaction)
- Edge: Full support

Enjoy your voice-enabled WeatherBot experience! 🌤️🎤 