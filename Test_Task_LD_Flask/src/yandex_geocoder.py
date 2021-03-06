from decimal import Decimal
from typing import Tuple
import requests
import json

from math import sin, cos, sqrt, atan2, radians

from src.exceptions import InvalidKey, NothingFound, UnexpectedResponse

class YandexGeocoder(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.long_moscow_ring_road, self.lat_moscow_ring_road = self.find_coordinates(address="Moscow Ring Road")
    
    def request_geocoder(self, location):
        """Send request to yandex_geocoder API

        Args:
            location: str, location could be address or 'longitude, latitude'
        
        Returns:
            json response from yandex_geocoder API

        """

        response = requests.get(
            "https://geocode-maps.yandex.ru/1.x/",
            params=dict(format="json", apikey=self.api_key, geocode=location, lang='en_RU'),
        )

        if response.status_code == 200:
            return response.json()["response"]
        elif response.status_code == 400:
            raise InvalidKey()
        else:
            raise UnexpectedResponse(
                f"status_code={response.status_code}, body={response.content}"
            )

    def find_coordinates(self, address=None) -> Tuple[Decimal]:
        """Find coordinates from address using request_geocoder function

        Args:
            address: str, address that want to find coordinates
        
        Returns:
            longitude, latitude

        """
        data = self.request_geocoder(address)["GeoObjectCollection"]["featureMember"]

        if not data:
            raise NothingFound(f'Nothing found for "{address}"')

        coordinates = data[0]["GeoObject"]["Point"]["pos"]  # type: str
        longitude, latitude = tuple(coordinates.split(" "))

        return Decimal(longitude), Decimal(latitude)

    def find_address(self, longitude=None, latitude=None) -> str:
        """Find address from coordinates using request_geocoder function

        Args:
            longitude: str
            latitude: str
        
        Returns:
            address from coordinates

        """
        coordinates = str(longitude) + ',' + str(latitude)
        data = self.request_geocoder(coordinates)["GeoObjectCollection"]["featureMember"]

        if not data:
            raise NothingFound(f'Nothing found for "{longitude}, {latitude}"')
        
        return data[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]

    def calculate_distance(self, address=None):
        """Find distance from Moscow Ring Road to some address

        Args:
            longitude: str
            latitude: str
            address: str
        
        Returns:
            distance calculated in miles

        """

        # find longitude and latitude from given address
        if address is not None:
            longitude, latitude = self.find_coordinates(address=address)
            address = self.find_address(longitude=longitude, latitude=latitude)
        
        # check is address in MKAD or not
        if "MKAD" in address:
            return 0
        else:
            R = 6373.0

            lat1 = radians(self.lat_moscow_ring_road)
            lon1 = radians(self.long_moscow_ring_road)
            lat2 = radians(latitude)
            lon2 = radians(longitude)

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c
            return distance