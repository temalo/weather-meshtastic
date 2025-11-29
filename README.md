# Weather Scripts for Meshtastic

A collection of Python scripts for fetching weather data from various sources and sending it via Meshtastic radio network.

## Scripts

### getwx_forecast.py
Fetches NWS (National Weather Service) hourly forecast data and sends the next 2 hours via Meshtastic.

**Features:**
- Gets hourly forecast from NWS API
- Compares forecast times with current time
- Sends next 2 upcoming hours of weather data
- Includes active weather alerts

### getwx.py
Fetches current weather conditions from your Tempest Weather Station and sends via Meshtastic.

**Features:**
- Real-time conditions from Tempest API
- Temperature, humidity, pressure, wind data
- Rainfall and lightning strike counts
- Solar radiation index
- Estimated charge rate for solar panel based on configured panel size in square meters

### nws_current_weather.py
Fetches current weather observations from the nearest NWS weather station and sends via Meshtastic.

**Features:**
- Automatically finds nearest NWS station
- Current conditions including temperature, humidity, wind, pressure
- Converts all data to US units

### tempest_forecast.py
Fetches daily forecast from Tempest Weather Station Better Forecast API and sends via Meshtastic.

**Features:**
- Daily high/low temperatures
- Precipitation probability
- Wind forecast
- Sunrise/sunset times

## Configuration

Each script requires configuration variables at the top of the file:

- `LAT` / `LON` - Your location coordinates
- `MESHTASTIC_HOST` - IP address of your Meshtastic device
- `CHANNEL_INDEX` - Meshtastic channel to send messages to
- `TEMPEST_STATION_ID` / `TEMPEST_API_TOKEN` - For Tempest scripts
- `USER_AGENT` - Your contact info for NWS API requests

## Tempest API Setup

The Tempest scripts (`getwx.py` and `tempest_forecast.py`) require a Tempest Weather Station and API token.

### Getting Your Station ID

Your Station ID can be found in your Tempest account at [tempestwx.com](https://tempestwx.com):
1. Log in to your Tempest account
2. Click on your station name in the left sidebar
3. Click the gear icon (⚙️) or "Settings" for your station
4. Your Station ID will be displayed in the station information section

### Generating a Tempest API Token

To generate an API token:
1. Go to [tempestwx.com/settings/tokens](https://tempestwx.com/settings/tokens)
2. Log in with your Tempest account credentials
3. Click "Create Token"
4. Give your token a descriptive name (e.g., "Meshtastic Weather")
5. Copy the generated token and add it to your script's `TEMPEST_API_TOKEN` variable

### Tempest API Documentation

For more information about the Tempest/WeatherFlow API, refer to the official documentation:
- [WeatherFlow Tempest API Documentation](https://weatherflow.github.io/Tempest/api/)

## Requirements

```
requests
meshtastic
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run any script directly:
```bash
python getwx_forecast.py
python getwx.py
python nws_current_weather.py
python tempest_forecast.py
```

## Meshtastic Setup

These scripts use the Meshtastic TCP interface. Make sure your Meshtastic device is accessible via TCP on the configured host.

## License

MIT License
