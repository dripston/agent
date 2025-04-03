import osmnx as ox

class OpenStreetMapData:
    def __init__(self):
        # Configure OSM with free tier settings
        ox.config(use_cache=True, 
                 log_console=True,
                 useful_tags_way=['building', 'natural', 'water'],
                 cache_folder='c:/Users/drips/agent-2/weather_agent/data/osm_cache')
    
    def get_area_details(self, location):
        # Get 1km² area features
        area = ox.geometries_from_point(
            (location['lat'], location['lon']),
            dist=500,  # 500m radius
            tags={'building': True, 
                  'natural': True,
                  'water': True}
        )
        
        return self._analyze_urban_features(area)