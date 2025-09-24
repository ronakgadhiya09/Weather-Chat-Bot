#!/usr/bin/env python3
"""
Fixed Weather Tools for Agno Framework

Provides weather-related tools with proper error handling and memory support.
"""

import os
import json
import httpx
from typing import Optional, Dict, Any


class FixedWeatherTools:
    """Fixed weather tools with enhanced error handling and memory support"""
    
    def __init__(self, api_key: str, units: str = "metric"):
        """Initialize weather tools with API key and units"""
        self.api_key = api_key
        self.units = units
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, location: str) -> str:
        """
        Get current weather for a location.
        
        Args:
            location (str): City name or location
            
        Returns:
            str: Current weather information
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": self.units
            }
            
            with httpx.Client() as client:
                response = client.get(url, params=params, timeout=10)
                
                if response.status_code == 404:
                    return f"Sorry, I couldn't find weather data for '{location}'. Please check the city name and try again."
                
                response.raise_for_status()
                data = response.json()
                
                # Extract weather information
                city = data["name"]
                country = data["sys"]["country"]
                description = data["weather"][0]["description"].title()
                temp = round(data["main"]["temp"])
                feels_like = round(data["main"]["feels_like"])
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                
                # Format response
                weather_info = f"📍 {city}, {country}\n"
                weather_info += f"🌡️ {temp}°C (feels like {feels_like}°C)\n"
                weather_info += f"☁️ {description}\n"
                weather_info += f"💧 Humidity: {humidity}%\n"
                weather_info += f"💨 Wind: {wind_speed} m/s"
                
                return weather_info
                
        except httpx.HTTPError as e:
            return f"Error fetching weather data: {str(e)}"
        except Exception as e:
            return f"Unexpected error getting weather for {location}: {str(e)}"
    
    def get_forecast(self, location: str, days: int = 1) -> str:
        """
        Get weather forecast for a location.
        
        Args:
            location (str): City name or location
            days (int): Number of days (1-5)
            
        Returns:
            str: Weather forecast information
        """
        try:
            # Limit days to reasonable range
            days = max(1, min(days, 5))
            
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": self.units
            }
            
            with httpx.Client() as client:
                response = client.get(url, params=params, timeout=10)
                
                if response.status_code == 404:
                    return f"Sorry, I couldn't find forecast data for '{location}'. Please check the city name and try again."
                
                response.raise_for_status()
                data = response.json()
                
                city = data["city"]["name"]
                country = data["city"]["country"]
                
                forecast_info = f"📍 {days}-day forecast for {city}, {country}:\n\n"
                
                # Process forecast data (API returns 3-hour intervals)
                forecasts = data["list"][:days * 8]  # 8 intervals per day (3-hour each)
                
                current_date = None
                for forecast in forecasts[::8]:  # Take one forecast per day
                    date = forecast["dt_txt"].split()[0]
                    if date != current_date:
                        current_date = date
                        temp_max = round(forecast["main"]["temp_max"])
                        temp_min = round(forecast["main"]["temp_min"])
                        description = forecast["weather"][0]["description"].title()
                        
                        forecast_info += f"📅 {date}: {temp_min}°C - {temp_max}°C, {description}\n"
                
                return forecast_info
                
        except httpx.HTTPError as e:
            return f"Error fetching forecast data: {str(e)}"
        except Exception as e:
            return f"Unexpected error getting forecast for {location}: {str(e)}"
    
    def get_air_pollution(self, location: str) -> str:
        """
        Get air quality information for a location.
        
        Args:
            location (str): City name or location
            
        Returns:
            str: Air quality information
        """
        try:
            # First get coordinates for the location
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            
            with httpx.Client() as client:
                geo_response = client.get(geo_url, params=geo_params, timeout=10)
                geo_response.raise_for_status()
                geo_data = geo_response.json()
                
                if not geo_data:
                    return f"Sorry, I couldn't find coordinates for '{location}' to check air quality."
                
                lat = geo_data[0]["lat"]
                lon = geo_data[0]["lon"]
                
                # Get air pollution data
                air_url = f"{self.base_url}/air_pollution"
                air_params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key
                }
                
                air_response = client.get(air_url, params=air_params, timeout=10)
                air_response.raise_for_status()
                air_data = air_response.json()
                
                aqi = air_data["list"][0]["main"]["aqi"]
                components = air_data["list"][0]["components"]
                
                # Map AQI to description
                aqi_descriptions = {
                    1: "Good",
                    2: "Fair", 
                    3: "Moderate",
                    4: "Poor",
                    5: "Very Poor"
                }
                
                air_info = f"🌬️ Air Quality in {location}:\n"
                air_info += f"📊 AQI: {aqi} ({aqi_descriptions.get(aqi, 'Unknown')})\n"
                air_info += f"🏭 CO: {components.get('co', 'N/A')} μg/m³\n"
                air_info += f"🌫️ PM2.5: {components.get('pm2_5', 'N/A')} μg/m³\n"
                air_info += f"💨 PM10: {components.get('pm10', 'N/A')} μg/m³"
                
                return air_info
                
        except httpx.HTTPError as e:
            return f"Error fetching air quality data: {str(e)}"
        except Exception as e:
            return f"Unexpected error getting air quality for {location}: {str(e)}" 