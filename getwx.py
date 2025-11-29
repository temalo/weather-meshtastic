import requests
import meshtastic
import meshtastic.tcp_interface
import time
from datetime import datetime

# Replace with your personal API token
API_TOKEN = "YOUR_API_TOKEN"
STATION_ID = "YOUR_STATION_ID"  # You can find this in your Tempest account
CHANNEL_INDEX = "4"
MESHTASTIC_HOST = "192.168.111.153"  # Change to your Meshtastic device IP/hostname
PANEL_SIZE = .04 #Panel size in square meters. Adjust based on your solar panel size.
PANEL_EFFICIENCY = 0.20 #Assumed panel efficiency (20%)

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

    # Send message using Meshtastic API
    try:
        interface = meshtastic.tcp_interface.TCPInterface(hostname=MESHTASTIC_HOST)
        print(f"Sending weather message ({len(message)} chars)...")
        interface.sendText(message, channelIndex=int(CHANNEL_INDEX))
        print("Message sent successfully!")
        
        # Wait to ensure message is queued before closing
        time.sleep(2)
        interface.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Error sending message: {e}")

else:
    print(f"Error: {response.status_code}")
