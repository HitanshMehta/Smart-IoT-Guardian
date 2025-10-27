CITIES = {
    "mumbai": {
        "name": "Mumbai, India",
        "country": "India",
        "climate": "tropical",
        "base_temp": (25.0, 32.0),  # REALISTIC Mumbai temperatures
        "base_humidity": (65.0, 85.0),
        "max_vibration": 0.8,
        "sensor_count": 5,
        "timezone": "IST"
    },
    "new_york": {
        "name": "New York, USA", 
        "country": "USA",
        "climate": "temperate",
        "base_temp": (5.0, 25.0),  # REALISTIC NYC temperatures (seasonal)
        "base_humidity": (55.0, 75.0),
        "max_vibration": 0.6,
        "sensor_count": 6,
        "timezone": "EST"
    },
    "london": {
        "name": "London, UK",
        "country": "UK", 
        "climate": "temperate",
        "base_temp": (8.0, 22.0),  # REALISTIC London temperatures
        "base_humidity": (70.0, 90.0),
        "max_vibration": 0.5,
        "sensor_count": 5,
        "timezone": "GMT"
    },
    
    "dubai": {
        "name": "Dubai, UAE",
        "country": "UAE",
        "climate": "desert",
        "base_temp": (25.0, 42.0),  # REALISTIC: 25-42°C, not 60+!
        "base_humidity": (20.0, 50.0),
        "max_vibration": 1.5,
        "sensor_count": 6,
        "timezone": "GST"
    }
}