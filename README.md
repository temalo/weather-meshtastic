# Weather Scripts for Meshtastic

A collection of Python scripts for fetching weather data from various sources and sending it via Meshtastic radio network.

## Features

This project provides professional weather monitoring scripts with centralized configuration management:

- **Environment-based configuration**: All settings managed via `.env` file for security and flexibility
- **Multiple weather data sources**: NWS and Tempest Weather Station support
- **Meshtastic integration**: Seamless transmission to your mesh network
- **Current conditions and forecasts**: Real-time observations and future predictions

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

This project uses environment variables for configuration. All settings are managed through a `.env` file, which keeps your sensitive information (like API tokens) separate from the code.

### Quick Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your specific configuration values (see below for detailed instructions)

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration Variables

Edit your `.env` file with the following variables:

#### Required for All Scripts
- `MESHTASTIC_HOST` - IP address or hostname of your Meshtastic device (default: `localhost`)
- `CHANNEL_INDEX` - Meshtastic channel index to send messages to (default: `4`)

#### Required for NWS Scripts (getwx_forecast.py, nws_current_weather.py)
- `LAT` - Your location latitude (e.g., `33.74733`)
- `LON` - Your location longitude (e.g., `-111.77912`)
- `USER_AGENT` - Contact info for NWS API (e.g., `WeatherApp/1.0 (your.email@example.com)`)

#### Required for Tempest Scripts (getwx.py, tempest_forecast.py)
- `TEMPEST_STATION_ID` - Your Tempest weather station ID
- `TEMPEST_API_TOKEN` - Your Tempest API token

#### Optional for getwx.py (Solar Panel Calculations)
- `PANEL_SIZE` - Solar panel size in square meters (default: `0.04`)
- `PANEL_EFFICIENCY` - Panel efficiency as decimal (default: `0.20` for 20%)

### Example .env File

```bash
# Meshtastic Configuration
MESHTASTIC_HOST=192.168.1.100
CHANNEL_INDEX=4

# Location Coordinates (for NWS scripts)
LAT=33.74733
LON=-111.77912

# NWS API Configuration
USER_AGENT=WeatherApp/1.0 (your.email@example.com)

# Tempest Weather Station Configuration
TEMPEST_STATION_ID=12345
TEMPEST_API_TOKEN=your-api-token-here

# Solar Panel Configuration (for getwx.py)
PANEL_SIZE=0.04
PANEL_EFFICIENCY=0.20
```

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
5. Copy the generated token and add it to your `.env` file's `TEMPEST_API_TOKEN` variable

### Tempest API Documentation

For more information about the Tempest/WeatherFlow API, refer to the official documentation:
- [WeatherFlow Tempest API Documentation](https://weatherflow.github.io/Tempest/api/)

## Requirements

```
requests>=2.31.0
meshtastic>=2.2.0
python-dotenv>=1.0.0
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your `.env` file is properly configured (see Configuration section above)

2. Run any script directly:
```bash
python getwx_forecast.py
python getwx.py
python nws_current_weather.py
python tempest_forecast.py
```

**Note**: Each script will validate that required environment variables are set before running.

## Security Best Practices

- **Never commit your `.env` file** to version control (it's already in `.gitignore`)
- Keep your API tokens and credentials secure
- Use the `.env.example` file as a template for new installations
- Regularly rotate your API tokens
- Consider using restrictive file permissions on your `.env` file: `chmod 600 .env`

## Meshtastic Setup

These scripts use the Meshtastic TCP interface. Make sure your Meshtastic device is accessible via TCP on the configured host.

## License

MIT License
