import requests
from requests.adapters import HTTPAdapter, Retry
import urllib.parse
import os

def geocode_street_address(street_address):
    import requests
    from requests.adapters import HTTPAdapter, Retry

    # Can use the city's geocoding tool but it is less robust and less accurate. 
#    BASE_URL = "https://xmaps.indy.gov/arcgis/rest/services/Locators/CompositeLocator/GeocodeServer/findAddressCandidates?"
#    GEOCODE_URL = f'{BASE_URL}SingleLine={urllib.parse.quote_plus(street_address)}&outFields=*&maxLocations=1&outSR=4326&f=pjson'

    MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')
    BASE_URL = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{urllib.parse.quote_plus(street_address)}.json?country=us&limit=1&types=address&access_token={MAPBOX_TOKEN}"


    s = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.1,
    )
    s.mount('https://', HTTPAdapter(max_retries=retries))
    results_dict = {
        'PNT_WKT': '',
        'Geocoding Accuracy': None,
        'lon': None,
        'lat': None,

    }

    try:
        response = s.get(BASE_URL, timeout=30)
    except RequestException as err:
        print(err)
        return results_dict

    if response.status_code == 200:
        try:
            response_json = response.json()
            wkid = '4326' #response_json['spatialReference']['wkid']
            if len(response_json['features'])>0:
                lon = response_json['features'][0]['center'][0]
                lat = response_json['features'][0]['center'][1]
                results_dict['PNT_WKT'] = 'SRID={wkid};POINT({lon} {lat})'.format(wkid=wkid, lon=lon, lat=lat)
                results_dict['Geocoding Accuracy']  = response_json['features'][0]['properties']['accuracy']
                results_dict['lon'] = lon 
                results_dict['lat'] = lat
        except BaseException as e:
            print(f'Unable to geocode {street_address}')
            print(results_dict)
            print(e)
            
    return results_dict