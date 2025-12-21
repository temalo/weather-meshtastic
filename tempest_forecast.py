import requests
import meshtastic
import meshtastic.tcp_interface
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
TEMPEST_STATION_ID = os.getenv("TEMPEST_STATION_ID")
TEMPEST_API_TOKEN = os.getenv("TEMPEST_API_TOKEN")
MESHTASTIC_HOST = os.getenv("MESHTASTIC_HOST", "localhost")
CHANNEL_INDEX = os.getenv("CHANNEL_INDEX", "0")

# Validate required configuration
if not TEMPEST_STATION_ID or not TEMPEST_API_TOKEN:
    raise ValueError("TEMPEST_STATION_ID and TEMPEST_API_TOKEN environment variables must be set")

def main():
    try:
        # Get Tempest Better Forecast data
        print(f"Fetching Better Forecast for station {TEMPEST_STATION_ID}...")
        forecast_url = f"https://swd.weatherflow.com/swd/rest/better_forecast?station_id={TEMPEST_STATION_ID}&token={TEMPEST_API_TOKEN}"
        
        response = requests.get(forecast_url)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if we have valid forecast data
        if "forecast" not in data or "daily" not in data["forecast"]:
            print("Error: Invalid forecast data received")
            return
        
        daily_forecasts = data["forecast"]["daily"]
        
        if not daily_forecasts:
            print("Error: No forecast data available")
            return
        
        # Get today's forecast (first day)
        today = daily_forecasts[0]
        
        # Extract forecast data
        day_num = today.get("day_num", "N/A")
        conditions = today.get("conditions", "N/A")
        icon = today.get("icon", "")
        
        # Temperature data (convert from Celsius to Fahrenheit)
        temp_high_c = today.get("air_temp_high")
        temp_low_c = today.get("air_temp_low")
        
        if temp_high_c is not None:
            temp_high = (temp_high_c * 9/5) + 32
        else:
            temp_high = None
        
        if temp_low_c is not None:
            temp_low = (temp_low_c * 9/5) + 32
        else:
            temp_low = None
        
        # Precipitation
        precip_probability = today.get("precip_probability")
        precip_type = today.get("precip_type", "none")
        precip_icon = today.get("precip_icon", "")
        
        # Wind
        wind_avg = today.get("wind_avg")
        wind_direction = today.get("wind_direction")
        wind_direction_cardinal = today.get("wind_direction_cardinal", "")
        
        # Sunrise/Sunset (Unix timestamps)
        sunrise = today.get("sunrise")
        sunset = today.get("sunset")
        
        # Convert timestamps to local time
        if sunrise:
            sunrise_dt = datetime.fromtimestamp(sunrise)
            sunrise_str = sunrise_dt.strftime("%H:%M")
        else:
            sunrise_str = "N/A"
        
        if sunset:
            sunset_dt = datetime.fromtimestamp(sunset)
            sunset_str = sunset_dt.strftime("%H:%M")
        else:
            sunset_str = "N/A"
        
        # Build output message
        current_date = datetime.now().strftime("%a %d %b")
        message_lines = []
        message_lines.append(f"Daily Wx Forecast for NE Scottsdale on {current_date}:")
        message_lines.append(f"Conditions: {conditions}")
        
        if temp_high is not None and temp_low is not None:
            message_lines.append(f"High/Low: {temp_high:.0f}°F / {temp_low:.0f}°F")
        elif temp_high is not None:
            message_lines.append(f"High: {temp_high:.0f}°F")
        
        if precip_probability is not None:
            message_lines.append(f"Precip Chance: {precip_probability}% ({precip_type})")
        
        if wind_avg is not None:
            wind_mph = wind_avg * 2.23694  # Convert m/s to mph
            if wind_direction_cardinal:
                message_lines.append(f"Wind: {wind_mph:.0f} mph {wind_direction_cardinal}")
            else:
                message_lines.append(f"Wind: {wind_mph:.0f} mph")
        
        message_lines.append(f"Sunrise: {sunrise_str} | Sunset: {sunset_str}")
        
        message = "\n".join(message_lines)
        
        # Display the message
        print("\n" + "="*50)
        print(message)
        print("="*50)
        
        # Enforce 210 character limit for Meshtastic - split into multiple messages if needed
        messages_to_send = []
        if len(message) > 210:
            # First message: 207 chars + "..."
            messages_to_send.append(message[:207] + "...")
            remaining = message[207:]
            
            # Additional messages for remainder
            while remaining:
                if len(remaining) > 210:
                    messages_to_send.append(remaining[:210])
                    remaining = remaining[210:]
                else:
                    messages_to_send.append(remaining)
                    remaining = ""
            
            print(f"Warning: Message split into {len(messages_to_send)} parts (original: {len(message)} chars)")
        else:
            messages_to_send.append(message)
        
        # Send message(s) using Meshtastic API
        try:
            interface = meshtastic.tcp_interface.TCPInterface(hostname=MESHTASTIC_HOST)
            
            for idx, msg in enumerate(messages_to_send, 1):
                print(f"\nSending forecast message part {idx}/{len(messages_to_send)} ({len(msg)} chars)...")
                interface.sendText(msg, channelIndex=int(CHANNEL_INDEX))
                print(f"Part {idx} sent successfully!")
                
                # Wait between messages if there are multiple parts
                if idx < len(messages_to_send):
                    print("Waiting 3 seconds before sending next part...")
                    time.sleep(3)
            
            # Wait to ensure final message is queued before closing
            time.sleep(2)
            interface.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Error sending message: {e}")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Status Code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except KeyError as e:
        print(f"Data Error: Missing expected key {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
