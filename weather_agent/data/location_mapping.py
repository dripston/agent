class MicroLocationMapper:
    def __init__(self):
        self.micro_regions = {
            "bangalore": {
                "peenya": {"lat": 13.0234, "lon": 77.5144, "sub_regions": [
                    {"name": "industrial_area", "lat": 13.0231, "lon": 77.5142},
                    {"name": "metro_station", "lat": 13.0236, "lon": 77.5146}
                ]},
                "whitefield": {"lat": 12.9698, "lon": 77.7500},
                "electronic_city": {"lat": 12.8458, "lon": 77.6631}
            },
            "mumbai": {
                "bandra": {"lat": 19.0596, "lon": 72.8295},
                "andheri": {"lat": 19.1136, "lon": 72.8697}
            },
            # Add Delhi and Chennai micro-regions
        }