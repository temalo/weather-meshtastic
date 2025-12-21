import requests
import meshtastic
import meshtastic.tcp_interface
import meshtastic.serial_interface
import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
LAT = float(os.getenv("LAT", "33.74733"))
LON = float(os.getenv("LON", "-111.77912"))
CHANNEL_INDEX = os.getenv("CHANNEL_INDEX", "4")
MESHTASTIC_INTERFACE = os.getenv("MESHTASTIC_INTERFACE", "tcp")  # 'tcp' or 'serial'
MESHTASTIC_HOST = os.getenv("MESHTASTIC_HOST", "localhost")  # For TCP
MESHTASTIC_PORT = os.getenv("MESHTASTIC_PORT")  # For Serial (e.g., COM3, /dev/ttyUSB0)
USER_AGENT = os.getenv("USER_AGENT", "WeatherApp/1.0 (your.email@example.com)")

def get_json(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept": "application/ld+json"})
    resp.raise_for_status()
    return resp.json()

def main():
    # 1) Resolve lat/lon to forecast URLs via NWS /points
    points_url = f"https://api.weather.gov/points/{LAT},{LON}"
    points = get_json(points_url)

    # NWS API returns data at root level (no "properties" wrapper)
    hourly_url = points["forecastHourly"]
    forecast_url = points["forecast"]
    city = points.get("relativeLocation", {}).get("city", "Phoenix")
    state = points.get("relativeLocation", {}).get("state", "AZ")

    print(f"Location: {city}, {state}  ({LAT}, {LON})")
    print(f"Hourly forecast: {hourly_url}")
    print(f"Period forecast: {forecast_url}\n")

    # 2) Fetch hourly forecast
    hourly = get_json(hourly_url)
    periods = hourly.get("properties", hourly).get("periods", [])

    # 3) Build forecast text for next 2 hours based on current time
    now = datetime.now(timezone.utc)
    forecast_lines = ["NE Scottsdale WX Forecast:", "Next 2 hours:"]
    forecast_count = 0
    
    for p in periods:
        # Parse the forecast start time
        forecast_time = datetime.fromisoformat(p["startTime"].replace("Z", "+00:00"))
        
        # Only include forecasts that are in the future
        if forecast_time > now and forecast_count < 2:
            # NWS returns local TZ offset; format concise
            ts = forecast_time.strftime("%a %I:%M %p")
            temp = f"{p['temperature']}°{p['temperatureUnit']}"
            wind = f"{p['windDirection']} {p['windSpeed']}"
            short = p["shortForecast"]
            forecast_lines.append(f"{ts}: {temp}, wind {wind}, {short}")
            forecast_count += 1
        
        # Stop once we have 2 future forecasts
        if forecast_count >= 2:
            break
    
    # 4) Check for active alerts for the area
    alerts_url = f"https://api.weather.gov/alerts/active?point={LAT},{LON}"
    alerts = get_json(alerts_url)
    features = alerts.get("features", [])
    
    # If no alerts, add it to forecast message; if alerts exist, keep as separate message
    if not features:
        # No alerts - add to forecast message
        forecast_lines.append("No active alerts.")
        forecast_text = "\r\n".join(forecast_lines)
        alerts_message = None
    else:
        # Active alerts - keep as separate message
        forecast_text = "\r\n".join(forecast_lines)
        alerts_lines = ["Active alerts:"]
        for a in features:
            info = a["properties"]
            alerts_lines.append(f"- {info.get('event')}: {info.get('headline')}")
        alerts_message = "\r\n".join(alerts_lines)
    
    # Helper function to split message into 210-char chunks
    def split_message(msg):
        messages = []
        if len(msg) > 210:
            # First message: 207 chars + "..."
            messages.append(msg[:207] + "...")
            remaining = msg[207:]
            
            # Additional messages for remainder
            while remaining:
                if len(remaining) > 210:
                    messages.append(remaining[:210])
                    remaining = remaining[210:]
                else:
                    messages.append(remaining)
                    remaining = ""
        else:
            messages.append(msg)
        return messages
    
    # Split forecast message if needed
    forecast_messages = split_message(forecast_text)
    
    if len(forecast_messages) > 1:
        print(f"Warning: Forecast split into {len(forecast_messages)} parts (original: {len(forecast_text)} chars)")
    
    # Split alerts message if it exists
    alerts_messages = []
    if alerts_message:
        alerts_messages = split_message(alerts_message)
        if len(alerts_messages) > 1:
            print(f"Warning: Alerts split into {len(alerts_messages)} parts (original: {len(alerts_message)} chars)")
    
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
        
        # Send forecast message(s)
        for idx, msg in enumerate(forecast_messages, 1):
            print(f"Sending forecast message part {idx}/{len(forecast_messages)} ({len(msg)} chars)...")
            interface.sendText(msg, channelIndex=int(CHANNEL_INDEX))
            print(f"Forecast part {idx} sent successfully!")
            
            if idx < len(forecast_messages):
                print("Waiting 3 seconds before sending next part...")
                time.sleep(3)
        
        # Send alerts message(s) only if there are alerts
        if alerts_messages:
            # Wait between forecast and alerts
            print("Waiting 5 seconds before sending alerts message...")
            time.sleep(5)
            
            for idx, msg in enumerate(alerts_messages, 1):
                print(f"Sending alerts message part {idx}/{len(alerts_messages)} ({len(msg)} chars): {msg}")
                interface.sendText(msg, channelIndex=int(CHANNEL_INDEX))
                print(f"Alerts part {idx} sent successfully!")
                
                if idx < len(alerts_messages):
                    print("Waiting 3 seconds before sending next part...")
                    time.sleep(3)
        
        # Wait a moment before closing to ensure message is queued
        time.sleep(2)
        
        # Close the connection
        interface.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Error sending messages: {e}")

if __name__ == "__main__":
    main()
