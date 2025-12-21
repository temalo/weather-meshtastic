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
LAT = float(os.getenv("LAT", "33.74733"))
LON = float(os.getenv("LON", "-111.77912"))
USER_AGENT = os.getenv("USER_AGENT", "WeatherApp/1.0 (your.email@example.com)")
MESHTASTIC_HOST = os.getenv("MESHTASTIC_HOST", "localhost")
CHANNEL_INDEX = os.getenv("CHANNEL_INDEX", "4")

def get_json(url):
    """Make a request to NWS API with required headers"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def main():
    # Step 1: Get the nearest weather station from the lat/lon point
    print(f"Looking up weather station for coordinates: {LAT}, {LON}")
    points_url = f"https://api.weather.gov/points/{LAT},{LON}"
    points_data = get_json(points_url)
    
    # Get observation stations URL
    stations_url = points_data.get("properties", {}).get("observationStations")
    if not stations_url:
        stations_url = points_data.get("observationStations")
    
    if not stations_url:
        print("Error: Could not find observation stations URL")
        return
    
    # Step 2: Get list of nearby stations
    print(f"Fetching nearby stations...")
    stations_data = get_json(stations_url)
    features = stations_data.get("features", [])
    
    if not features:
        print("No weather stations found nearby")
        return
    
    # Get the first (closest) station
    station = features[0]
    station_id = station.get("properties", {}).get("stationIdentifier")
    station_name = station.get("properties", {}).get("name")
    
    print(f"Using station: {station_name} ({station_id})")
    
    # Step 3: Get current observations from the station
    obs_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
    obs_data = get_json(obs_url)
    
    props = obs_data.get("properties", {})
    
    # Extract weather data
    timestamp = props.get("timestamp", "N/A")
    temp_c = props.get("temperature", {}).get("value")
    humidity = props.get("relativeHumidity", {}).get("value")
    wind_speed_ms = props.get("windSpeed", {}).get("value")
    wind_direction = props.get("windDirection", {}).get("value")
    pressure_pa = props.get("barometricPressure", {}).get("value")
    description = props.get("textDescription", "N/A")
    
    # Convert to US units
    if temp_c is not None:
        temp_f = (temp_c * 9/5) + 32
    else:
        temp_f = None
    
    if wind_speed_ms is not None:
        wind_mph = wind_speed_ms * 2.23694
    else:
        wind_mph = None
    
    if pressure_pa is not None:
        pressure_inHg = pressure_pa * 0.0002953
    else:
        pressure_inHg = None
    
    # Format timestamp (convert to local time)
    if timestamp != "N/A":
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        local_dt = dt.astimezone()
        time_str = local_dt.strftime("%H:%M")
    else:
        time_str = "N/A"
    
    # Build output message
    message_lines = []
    message_lines.append(f"NWS Current Conditions as of {time_str}")
    message_lines.append(f"Station: {station_name} ({station_id})")
    message_lines.append(f"Conditions: {description}")
    if temp_f is not None:
        message_lines.append(f"Temperature: {temp_f:.1f}°F")
    if humidity is not None:
        message_lines.append(f"Humidity: {humidity:.0f}%")
    if wind_mph is not None and wind_direction is not None:
        message_lines.append(f"Wind: {wind_mph:.1f} mph from {wind_direction}°")
    elif wind_mph is not None:
        message_lines.append(f"Wind Speed: {wind_mph:.1f} mph")
    if pressure_inHg is not None:
        message_lines.append(f"Pressure: {pressure_inHg:.2f} inHg")
    
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
            print(f"\nSending weather message part {idx}/{len(messages_to_send)} ({len(msg)} chars)...")
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

if __name__ == "__main__":
    main()
