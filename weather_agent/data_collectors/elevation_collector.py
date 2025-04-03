import requests
import numpy as np

class ElevationAPI:
    def __init__(self):
        # SRTM data API endpoint (30-meter resolution)
        self.api_url = "https://api.opentopodata.org/v1/srtm30m"
        
    def get_detailed_elevation(self, location):
        # Get elevation data for 1km² area around point
        lat, lon = location['lat'], location['lon']
        points = self._generate_grid(lat, lon, resolution=0.001)  # ~100m spacing
        
        response = requests.post(self.api_url, json={
            "locations": points
        })
        
        return self._process_elevation_data(response.json())


import elevation
import rasterio
import numpy as np

class ElevationData:
    def __init__(self):
        self.data_dir = 'c:/Users/drips/agent-2/weather_agent/data/elevation'
        
    def get_elevation(self, lat, lon):
        # Download SRTM 30m data (free)
        elevation.clip(bounds=(lon-0.1, lat-0.1, lon+0.1, lat+0.1),
                      output=f'{self.data_dir}/temp.tif')
        
        with rasterio.open(f'{self.data_dir}/temp.tif') as dataset:
            return dataset.read(1)  # Returns elevation array