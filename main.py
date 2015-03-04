#!/usr/bin/python
# -*- coding:utf-8 -*

# standard lib imports
import json
import requests
import sys

# logging imports
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

# fabric imports
from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import blue
from fabric.colors import white

# logger object creation
logger = logging.getLogger('map')
logger.setLevel(logging.DEBUG)

# Build formatter for each handler
formatter_file = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
formatter_console = logging.Formatter(yellow('[%(asctime)s]') + \
                                      blue('[%(levelname)s]') + \
                                      white(' %(message)s'))

# Set handlers filesize is < 1Mo
file_handler = RotatingFileHandler('map.log', 'a', 1000000, 1)
stream_handler = logging.StreamHandler(stream=sys.stdout)

# Set formatters
file_handler.setFormatter(formatter_file)
stream_handler.setFormatter(formatter_console)

# Set level
file_handler.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.INFO)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def load_json_data(json_file):
    """
    @goal: load data from json file
    @param: json_file, string, json file path
    @return: data
    """

    with open(json_file, 'rb') as json_data:
        data = json.load(json_data)

    return data

def get_gps_from_address(adress):
    """
    get GPS coordonnates from formatted address
    """

    google_api_url = "http://maps.google.com/maps/api/geocode/json?address=%s&sensor=false" \
                     % adress.encode('utf8')
    json_temp      = './tmp.json-%s' % adress[:10]
    with open(json_temp, 'w') as json_google:
        json_google.write(requests.get(google_api_url).content)

    data_google = load_json_data(json_temp)
    lat = float(data_google['results'][0]['geometry']['location']['lat'])
    lng = float(data_google['results'][0]['geometry']['location']['lng'])

    logger.info(adress)
    logger.info('latitude:%f, longitude:%f', lat, lng)

    return lat, lng 

def get_address_from_gps(lat, lng):
    '''
    get formatted address from GPS coordonnates
    '''

    google_api_url = "http://maps.google.com/maps/api/geocode/json?latlng=%f,%f&sensor=false" \
                     % (lat, lng)

    json_temp      ='./tmp.json_%d-%d' % (lat, lng) 

    with open(json_temp, 'w') as json_google:
        json_google.write(requests.get(google_api_url).content)

    data_google = load_json_data(json_temp)

    return data_google['results'][0]['formatted_address']

if __name__ == '__main__':
    # Guests list
    GUESTS = ['Matt', 'Dim', 'Gamin', 'Fred', 'Tibi']
    logger.info("Guests: " + ' / '.join(GUESTS))

    # Get addresses
    ADDRESSES = load_json_data('./dudes.json')

    # GPS coordonates list
    GPS_COORD = [get_gps_from_address(ADDRESSES[guest]) for guest in ADDRESSES \
                 if guest in GUESTS]

    # GPS Barycenter
    BARY = float(sum(gps[0] for gps in GPS_COORD)) / float(len(GUESTS)), \
                 float(sum(gps[1] for gps in GPS_COORD)) / float(len(GUESTS))
    logger.info("GPS barycentre: %s", BARY)

    # Formatted address Barycenter
    ICICI = get_address_from_gps(BARY[0], BARY[1])
    logger.info("ICICI: %s", ICICI)


