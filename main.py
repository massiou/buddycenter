#!/usr/bin/env python
"""
Buddy center flask application (Google API inside)
"""

# -*- coding: utf-8 -*-

# Tierce libs imports
import re
import requests
import json
import datetime
import uuid
import BeautifulSoup
from flask import Flask, request, render_template

__author__ = "Matthieu Velay"
__copyright__ = "Copyright 2016, Matthieu Velay"
__version__ = "1.0"
__maintainer__ = "Matthieu Velay"
__email__ = "mvelay@gmail.com"
__status__ = "Production"

APP = Flask(__name__)
APP.config['DEBUG'] = True

# google API Key
API_KEY = "AIzaSyC1cgoNFc3hAHRMZWQM2x7uscTciFXrYXM"


def load_json_data(json_file):
    """
    @goal: load data from json file
    @param: json_file, string, json file path
    @return: data
    """
    try:
        with open(json_file, 'rb') as json_data:
            data = json.load(json_data)
    except ValueError:
        data = {}
    return data


def get_address_from_gps(lat, lng):
    """
    get formatted address from GPS coordonnates
    """

    google_api_url = "http://maps.google.com/maps/api/geocode/json?latlng={},{}&sensor=false".format(lat, lng)

    data_google = json.loads(requests.get(google_api_url).content)

    if data_google.get('results'):
        formatted_address = data_google['results'][0]['formatted_address']
    else:
        formatted_address = ''

    return formatted_address


def get_gps_from_address(adress):
    """
    get GPS coordonnates from formatted address
    """

    google_api_url = "http://maps.google.com/maps/api/geocode/json?address=%s&sensor=false" \
                     % adress.encode('utf8')

    data_google = json.loads(requests.get(google_api_url).content)
    if data_google.get('results'):
        lat = float(data_google['results'][0]['geometry']['location']['lat'])
        lng = float(data_google['results'][0]['geometry']['location']['lng'])
    else:
        lat = 48
        lng = 2
    return lat, lng


def calculate_center_from_addresses(addresses):
    """
    @param addresses: list of addresses
    """

    gps_list = [get_gps_from_address(address) for address in addresses]
    if gps_list:
        bary_lat = float(sum(gps_c[0]
                             for gps_c in gps_list)) / float(len(gps_list))
        bary_lgn = float(sum(gps_c[1]
                             for gps_c in gps_list)) / float(len(gps_list))
    else:
        bary_lat = 48
        bary_lgn = 2

    address_center = get_address_from_gps(bary_lat, bary_lgn)

    return bary_lat, bary_lgn, address_center, gps_list


def get_address_from_form(request, input_name):
    """
    get string address from form html
    """
    address = request.form.get(input_name)
    address = request.form.get(input_name, address)
    if not address:
        address = ""

    return address


def get_places_from_gps(lat, lng, places_type, offline=False):
    """
    return places given lat,lng and type
    """

    google_api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%f,%f&types=%s&rankby=distance&key=%s&sensor=false" \
% (lat, lng, places_type, API_KEY)

    if offline:
        json_temp = './places_offline_%s.json' % places_type
        with open(json_temp, 'r') as json_google:
            data_google = load_json_data(json_temp)
    else:
        data_google = json.loads(requests.get(google_api_url).content)

    return data_google.get('results', {})


def get_infos_from_place_id(place_id, offline=False):
    """
    :param place_id
    :param offline: boolean
    :return: dict that contains places ids info
    """
    google_api_url = "https://maps.googleapis.com/maps/api/place/details/json?reference={}&key={}".format(place_id,
                                                                                                          API_KEY)
    if offline:
        json_temp = './info_offline.json'  #% place_id[:10]
        with open(json_temp, 'r') as json_google:
            data_google = load_json_data(json_temp)
    else:
        data_google = json.loads(requests.get(google_api_url).content)

    return data_google.get('result', {})


def get_photo_from_place(place_info):
    """
    :param place_info:
    :return: photo URL corresponding to place_info
    """
    output_url = "http://sponsowl.com/assets/no-image-available.png"
    max_width = 200
    max_height = 150
    photo_reference = place_info.get('photos')
    if photo_reference:
        photo_reference = photo_reference[0]['photo_reference']
        google_api_url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=%s&max_height=%s&photoreference=%s&key=%s" % (max_width, max_height, photo_reference, API_KEY)
        if requests.get(google_api_url):
            output_url = requests.get(google_api_url).url

    return output_url


def get_gps_from_place(place_info):
    """
    :param place_info
    :return: GPS coordonates
    """

    try:
        gps_location = place_info["geometry"]["location"]["lat"], \
                       place_info["geometry"]["location"]["lng"]

    except (KeyError, IndexError):
        gps_location = None

    return gps_location


def get_distance_from_origin_to_dest(origin_address, destination_address,
                                     offline=False):
    """
    :param origin_address
    :param destination_address
    :param offline
    :return: tuple, (distance, duration between two addresses)
    """
    google_api_url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s" \
                      % (origin_address, destination_address)

    if offline:
        json_temp = './distance_offline.json'  #% place_id[:10]
        with open(json_temp, 'r') as json_google:
            data_google = load_json_data(json_temp)
    else:
        data_google = json.loads(requests.get(google_api_url).content)

    try:
        distance = data_google["rows"][0]["elements"][0]["distance"]["text"]
    except (KeyError, IndexError):
        distance = 'unknown'
    try:
        duration = data_google["rows"][0]["elements"][0]["duration"]["text"]
    except (KeyError, IndexError):
        duration = 'unknown'

    return distance, duration


def get_html_content_from_place(place_info):
    """
    :param place_info:
    :return: html page with place infos
    """

    html_content = '<div id="content">' + \
                   '<div id="siteNotice">' + \
                   '</div>' + \
                   '<h1 id="firstHeading" class="firstHeading">' + place_info['name'] + \
                   '</h1>' + \
                   '<div id="bodyContent">'
    html_content += '<a class="fancybox fancybox.iframe" href="%s">%s</a>' % (
        place_info.get("website", ""), place_info.get("website", ""))
    html_content += "Phone: %s" % (place_info.get('international_phone_number',
                                                  "Unknown"))
    html_content += '</div></div>'

    return html_content


def get_reviews_from_place_id(place_id, offline=False):
    """
    :param place_id
    :param offline
    :return:
    """
    raise NotImplementedError


def create_yelp(address):
    """
    :param address
    :return: yelp url with predefined search
    """
    yelp_url = "http://www.yelp.com/search?find_desc=&find_loc=%s" % address

    return yelp_url

def create_doodle(places_list, place_type):
    """
    :param places_list
    :param place_type
    :return: pre-filled doodle url
    """

    doodle_url = "http://doodle.com/polls/wizard.html?type=text&locale=fr&"
    # get infos to give
    title = "title=%s selection ?&" % place_type
    name = "name=Matt "
    places = '&'.join(['option' + str(index + 1) + '=' + unicode(places)
                       for index, places in enumerate(places_list)])
    email = "&eMailAddress=mvelay@gmail.com&"

    # url building
    final_doodle = (doodle_url + title + name + email + places + '#invite'
                   )  #.encode("ascii", "xmlcharrefreplace")

    return final_doodle


def create_unique_html_page(html_page):
    """
    :param html_page
    :return: share html page
    """

    uuid_html = uuid.uuid1()
    html_page_uuid = html_page.split(
        'maps.html')[0] + "share" + str(uuid_html) + '.html'
    url_uuid = 'share' + str(uuid_html) + '.html'
    return html_page_uuid, url_uuid

def share(request):
    """
    :param request
    :return: html page to share
    """
    static_html = "./templates" + request.path

    with open(static_html) as html:
        soup = BeautifulSoup.BeautifulSoup(html.read())

    #get category set in html
    category_before = str(soup.findAll('select', attrs={'name': 'select_place_type'}))
    category_before = category_before.split("value=")[1].split(">")[0].replace('"', '')

    #get addresses set in html
    inputs = soup.findAll('input', attrs={"class": u"autocomplete"})
    address_list_before = [re.sub('.*value="', '', str(input_addr)) for input_addr in inputs]
    address_list_before = [addr.replace('" />', '') for addr in address_list_before]


    #get current category
    place_selected = request.POST.get("select_place_type", False)

    #get current addresses
    address_list_current = [get_address_from_form(request, form_id)
                            for form_id in ['address%d' % id_f for id_f in range(10)]
                            if get_address_from_form(request, form_id) != '']

    # Current list is empty (first load or all was deleted)
    if not address_list_current:
        address_list_current = address_list_before

    if not place_selected:
        place_selected = category_before

    print "address_list_before: %s" % address_list_before
    print "address_list_current: %s" % address_list_current
    page_has_changed = (address_list_before != address_list_current) or (category_before != place_selected)
    print category_before
    print place_selected
    if page_has_changed:
        response = gps()
        print "PAGE HAS CHANGED"
    else:
        response = render_template('./templates' + request.path)
    return response


def create_airbnb(address, date=""):
    """
    :param address
    :param date
    :return: airbnb URL
    """

    airbnb_url = "https://www.airbnb.com/s/%s?checkin=%s&source=bb&ss_id=" % (address, date)

    return airbnb_url

def create_lafourchette(address, lat, lng):
    """
    :param address
    :param lat
    :param lng
    :return: lafourchette URL
    """

    address = address.replace(",", "%2C")
    address = address.replace(" ", "+")
    coordinates_url = ("%s+%s" % (lat, lng))
    coordinates_url = coordinates_url.replace("+", "%2C")
    lafourchette_url = "http://www.lafourchette.com/recherche/415144?searchText=%s&altDate=Sans+date&date=noDate&time=&pax=&coordinate=%s&idRestaurant=&locality=&titleSubstitute=&localeCode=&idGooglePlace=&sb=1&is_restaurant_autocomplete=0" \
% (address, coordinates_url)
    return lafourchette_url


def create_tripadvisor():
    """
    :return
    """
    raise NotImplementedError


def get_reviews_from_place(place):
    """
    :param place:
    :return: google reviews
    """
    reviews = place.get('reviews', [])
    for index, review in enumerate(reviews):
        time_review = review.get('time', 0)
        reviews[index]['time'] = datetime.datetime.fromtimestamp(
            time_review).strftime('%Y-%m-%d')

    return reviews


@APP.route('/', methods=['GET', 'POST'])
def gps():
    """
    Goal: calculate gps center, get places details
    """

    # Initialization
    nb_places = 5
    places_type_remaining = [("bar", "Bar"), ("cafe", "Cafe"),
                             ("night_club", "Night Club"),
                             ("restaurant", "Restaurant"),
                             ("pharmacy", "Pharmacy"),
                             ("church", "Church"), ("lodging", "Hotel"),
                             ("bank", "Bank"), ("zoo", "Zoo")]
    place_selected = None
    address_list = []
    offline = False
    place_value = None
    marker_image = "place_default.png"
    date_selected = request.form.get('date_selected', None)

    if date_selected is None:
        date_selected = datetime.date.today().strftime('%d/%m/%Y')

    date_selected = None
    place_selected_1 = request.form.get("select_place_type", False)
    place_selected = [(value1, value2) for value1, value2 in places_type_remaining
                      if value1 == place_selected_1]

    if place_selected:
        place_value = place_selected[0][0]
        place_selected = place_selected[0]
        marker_image = place_value + ".png"

    places_type_remaining = [(value1, value2) for value1, value2 in places_type_remaining
                             if value1 != place_value]

    # Get all addresses from input text
    address_list = [get_address_from_form(request, form_id)
                    for form_id in ['address%d' % id_f for id_f in range(10)]
                    if get_address_from_form(request, form_id) != '']
    # Calculate barycenter
    lat, lng, address_center, buddies_gps_list = calculate_center_from_addresses(
        address_list)

    distances = [(address_origin, get_distance_from_origin_to_dest(address_origin, address_center))
                 for address_origin in address_list]

    # get places from center
    from operator import itemgetter

    places_result = get_places_from_gps(lat, lng, place_value, offline)

    if offline:
        try:
            with open('./places_result.json', 'w') as places_result_json:
                places_result_json.write(str(places_result))
        except ValueError:
            print 'no json could be decoded'

    places_details = [get_infos_from_place_id(place['reference'], offline)
                      for place in places_result[:nb_places]]

    places = [(place['name'], place['vicinity'], place.get('rating', 0),
               places_details[index].get('international_phone_number'),
               places_details[index].get('website'),
               get_reviews_from_place(places_details[index]),
               place['id'],
               get_gps_from_place(places_details[index]),
               get_html_content_from_place(places_details[index]),
               get_photo_from_place(places_details[index]))
              for index, place in enumerate(places_result[:nb_places])]

    # places sorted by rating
    places = sorted(places, key=itemgetter(2))
    places.reverse()

    # Create doodle page, fill
    doodle_page = create_doodle([place[0] \
                                  for place in places], place_value)

    # Create yelp url
    yelp = create_yelp(address_center)

    # Create lafourchette url
    lafourchette = create_lafourchette(address_center, lat, lng)

    # Create airbnb url
    airbnb = create_airbnb(address_center, date_selected)

    # Create unique link
    html_link_uid, url_uid = create_unique_html_page(
        './maps.html')

    # Build response
    response = render_template('./maps.html',
                               doodle_page=doodle_page,
                               places_type_remaining=places_type_remaining,
                               place_selected=place_selected,
                               date_selected=date_selected,
                               address_center=address_center,
                               buddies_gps_list=buddies_gps_list,
                               places=places,
                               address_list=address_list,
                               marker_image=marker_image,
                               distances=distances,
                               airbnb=airbnb,
                               yelp=yelp,
                               lafourchette=lafourchette,
                               html_link_uid=html_link_uid,
                               url_uid=url_uid,
                               method=request.method)
    #with open(html_link_uid, 'w') as html_unique:
    #    html_unique.write(response.content)
    return response

if __name__ == '__main__':
    APP.run()
