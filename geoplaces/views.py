import re

import requests
from django.db.models import Q

from geoplaces.models import Place


def fetch_coordinates(api_key: str, address: str) -> tuple:
    """Получение координат."""

    base_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': api_key,
        'format': 'json',
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None, None, None

    most_relevant = found_places[0]
    longitude, latitude = most_relevant['GeoObject']['Point']['pos'].split(" ")
    formatted_address = most_relevant['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
    return longitude, latitude, formatted_address


def get_or_create_place_object(dirty_address: str, api_key: str) -> Place:
    """Создание объекта Place, если нету, то получаем данные из апи."""
    print('>>> get_or_create_place_object')
    city, street, house = map(str.strip, dirty_address.split(',', 2))
    print('***city, street, house: ', city, street, house)

    #TODO: починить запрос к базе, не работает поиск по номеру дома
    place = Place.objects.filter(
        Q(raw_address__icontains=city) &
        Q(raw_address__icontains=street) &
        Q(raw_address__iregex=rf'(?<!\w){re.escape(house)}(?!\w)')
    ).order_by('id').first()
    print('*place', place)
    if not place:
        longitude, latitude, formatted_address = fetch_coordinates(api_key, dirty_address)
        place = Place.objects.create(
            raw_address=dirty_address,
            normalized_address=formatted_address,
            longitude=longitude,
            latitude=latitude,
        )
        print('<<< if get_or_create_place_object')
        return place
    print('<<< get_or_create_place_object')
    return place
