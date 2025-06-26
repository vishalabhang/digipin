from pydantic import BaseModel, Field
from typing import Optional


class EncodeRequest(BaseModel):
    lat: float = Field(..., description="Latitude (2.5 to 38.5)")
    lon: float = Field(..., description="Longitude (63.5 to 99.5)")

class DecodeRequest(BaseModel):
    digiPin: str = Field(..., description="10-character DIGIPIN (with optional dashes)")

class Digipin:
    DIGIPIN_GRID = [
        ['F', 'C', '9', '8'],
        ['J', '3', '2', '7'],
        ['K', '4', '5', '6'],
        ['L', 'M', 'P', 'T']
    ]

    BOUNDS = {
        'minLat': 2.5,
        'maxLat': 38.5,
        'minLon': 63.5,
        'maxLon': 99.5
    }

    @classmethod
    def encode(cls, lat, lon):
        if lat < cls.BOUNDS['minLat'] or lat > cls.BOUNDS['maxLat']:
            raise ValueError('Latitude out of range')
        if lon < cls.BOUNDS['minLon'] or lon > cls.BOUNDS['maxLon']:
            raise ValueError('Longitude out of range')

        min_lat = cls.BOUNDS['minLat']
        max_lat = cls.BOUNDS['maxLat']
        min_lon = cls.BOUNDS['minLon']
        max_lon = cls.BOUNDS['maxLon']

        digi_pin = ''

        for level in range(1, 11):
            lat_div = (max_lat - min_lat) / 4
            lon_div = (max_lon - min_lon) / 4

            row = 3 - int((lat - min_lat) / lat_div)
            col = int((lon - min_lon) / lon_div)

            row = max(0, min(row, 3))
            col = max(0, min(col, 3))

            digi_pin += cls.DIGIPIN_GRID[row][col]

            if level == 3 or level == 6:
                digi_pin += '-'

            max_lat = min_lat + lat_div * (4 - row)
            min_lat = min_lat + lat_div * (3 - row)

            min_lon = min_lon + lon_div * col
            max_lon = min_lon + lon_div

        return digi_pin

    @classmethod
    def decode(cls, digi_pin):
        pin = digi_pin.replace('-', '')
        if len(pin) != 10:
            raise ValueError('Invalid DIGIPIN')

        min_lat = cls.BOUNDS['minLat']
        max_lat = cls.BOUNDS['maxLat']
        min_lon = cls.BOUNDS['minLon']
        max_lon = cls.BOUNDS['maxLon']

        for char in pin:
            found = False
            for r in range(4):
                for c in range(4):
                    if cls.DIGIPIN_GRID[r][c] == char:
                        ri, ci = r, c
                        found = True
                        break
                if found:
                    break
            if not found:
                raise ValueError(f'Invalid character in DIGIPIN: {char}')

            lat_div = (max_lat - min_lat) / 4
            lon_div = (max_lon - min_lon) / 4

            lat1 = max_lat - lat_div * (ri + 1)
            lat2 = max_lat - lat_div * ri
            lon1 = min_lon + lon_div * ci
            lon2 = min_lon + lon_div * (ci + 1)

            min_lat = lat1
            max_lat = lat2
            min_lon = lon1
            max_lon = lon2

        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2

        return {
            "latitude": round(center_lat, 6),
            "longitude": round(center_lon, 6)
        }
