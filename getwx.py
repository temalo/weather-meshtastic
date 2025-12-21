import requests
import meshtastic
import meshtastic.tcp_interface
import meshtastic.serial_interface
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
API_TOKEN = os.getenv("TEMPEST_API_TOKEN")
STATION_ID = os.getenv("TEMPEST_STATION_ID")
CHANNEL_INDEX = os.getenv("CHANNEL_INDEX", "4")
MESHTASTIC_INTERFACE = os.getenv("MESHTASTIC_INTERFACE", "tcp")  # 'tcp' or 'serial'
MESHTASTIC_HOST = os.getenv("MESHTASTIC_HOST", "localhost")  # For TCP
MESHTASTIC_PORT = os.getenv("MESHTASTIC_PORT")  # For Serial (e.g., COM3, /dev/ttyUSB0)
PANEL_SIZE = float(os.getenv("PANEL_SIZE", "0.04"))
PANEL_EFFICIENCY = float(os.getenv("PANEL_EFFICIENCY", "0.20"))

# Validate required configuration
if not API_TOKEN or not STATION_ID:
    raise ValueError("TEMPEST_API_TOKEN and TEMPEST_STATION_ID environment variables must be set")

# API endpoint for current observations
url = f"https://swd.weatherflow.com/swd/rest/observations/station/{STATION_ID}?token={API_TOKEN}"

# Make the request to Tempest API
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    obs = data.get("obs", [{}])[0]  # Get the latest observation

    # Extract required elements
    timestamp = obs.get("timestamp", "N/A")
    temperature = obs.get("air_temperature", "N/A")
    feelslike = obs.get("feels_like", "N/A")
    humidity = obs.get("relative_humidity", "N/A")
    pressure = obs.get("barometric_pressure", "N/A")
    trend = obs.get("pressure_trend", "N/A")
    wind_speed = obs.get("wind_avg", "N/A")
    wind_direction = obs.get("wind_direction", "N/A")
    rainfall = obs.get("precip_accum_local_day", "N/A")
    lightning_strikes = obs.get("strike_count", "N/A")
    solar_radiation = obs.get("solar_radiation", "N/A")


    # Convert to U.S. units
    local = datetime.fromtimestamp(timestamp).strftime("%H:%M")
    temp_f = (temperature * 9/5) + 32
    feel_f = (feelslike *9/5) + 32
    pressure_inHg = pressure * 0.02953
    wind_speed_mph = wind_speed * 2.23694
    rainfall_in = rainfall * 0.03937
    panel_power = PANEL_SIZE * PANEL_EFFICIENCY * solar_radiation #Calculate estimated power output in Watts

    # Construct formatted message
    message = (
        f"WX NE Scottsdale as of {local}: Temp:{temp_f:.0f}°F, Feels Like: {feel_f:.0f}°F, Humidity:{humidity}%, Barometer:{pressure_inHg:.2f} Hg, and {trend}, "
        f"Wind:{wind_speed_mph:.0f} mph at {wind_direction}°, Rain:{rainfall_in:.2f} in, "
        f"Lightning Strikes:{lightning_strikes}, Solar Index:{solar_radiation} W/m², Est panel power:{panel_power:.2f} W"
    )

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
        # Create interface based on configuration
        if MESHTASTIC_INTERFACE.lower() == "serial":
            if not MESHTASTIC_PORT:
                raise ValueError("MESHTASTIC_PORT must be set when using serial interface")
            interface = meshtastic.serial_interface.SerialInterface(MESHTASTIC_PORT)
            print(f"Connected via Serial: {MESHTASTIC_PORT}")
        else:
            interface = meshtastic.tcp_interface.TCPInterface(hostname=MESHTASTIC_HOST)
            print(f"Connected via TCP: {MESHTASTIC_HOST}")
        
        for idx, msg in enumerate(messages_to_send, 1):
            print(f"Sending weather message part {idx}/{len(messages_to_send)} ({len(msg)} chars)...")
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

else:
    print(f"Error: {response.status_code}")
