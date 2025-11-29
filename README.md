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
