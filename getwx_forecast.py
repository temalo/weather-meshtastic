import requests
import meshtastic
import meshtastic.tcp_interface
import time
from datetime import datetime, timezone

# Home Location
LAT = 33.74733
LON = -111.77912
CHANNEL_INDEX = "4"
MESHTASTIC_HOST = "localhost"  # Change to your Meshtastic device IP

USER_AGENT = "WeatherApp/1.0 (your.email@example.com)"  # use your email/domain

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
    
    forecast_text = "\r\n".join(forecast_lines)

    # 4) Useful extras: active alerts for the area
    alerts_url = f"https://api.weather.gov/alerts/active?point={LAT},{LON}"
    alerts = get_json(alerts_url)
    features = alerts.get("features", [])
    if features:
        alerts_lines = ["Active alerts:"]
        for a in features:
            info = a["properties"]
            alerts_lines.append(f"- {info.get('event')}: {info.get('headline')}")
        alerts_message = "\r\n".join(alerts_lines)
    else:
        alerts_message = "No active alerts."
    
    # Send both messages using Meshtastic API
    try:
        interface = meshtastic.tcp_interface.TCPInterface(hostname=MESHTASTIC_HOST)
        
        # Send forecast message
        print(f"Sending forecast message ({len(forecast_text)} chars)...")
        interface.sendText(forecast_text, channelIndex=int(CHANNEL_INDEX))
        print("Forecast message sent successfully!")
        
        # Wait a few seconds for the first message to be queued/transmitted
        print("Waiting 5 seconds before sending alerts message...")
        time.sleep(5)
        
        # Send alerts message
        print(f"Sending alerts message ({len(alerts_message)} chars): {alerts_message}")
        interface.sendText(alerts_message, channelIndex=int(CHANNEL_INDEX))
        print("Alerts message sent successfully!")
        
        # Wait a moment before closing to ensure message is queued
        time.sleep(2)
        
        # Close the connection
        interface.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Error sending messages: {e}")

if __name__ == "__main__":
    main()
