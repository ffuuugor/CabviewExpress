from geo import City
from geopy import Nominatim
from googleapiclient.discovery import build
import googlemaps
import config
import logging
import polyline


geocoder = Nominatim()
gmaps = googlemaps.Client(config.DEVELOPER_KEY)
logger = logging.getLogger(__name__)

PERMITTED_VEHICLES = ["RAIL", "METRO_RAIL", "SUBWAY", "TRAM",
                      "MONORAIL", "HEAVY_RAIL", "COMMUTER_TRAIN", "HIGH_SPEED_TRAIN"]


class Route(object):

    def __init__(self, city_from, city_to, path):
        self.city_from = city_from
        self.city_to = city_to
        self.waypoints = Route._label_waypoints(city_from, city_to, path)

    @property
    def path(self):
        return polyline.encode([(x.lat, x.lng) for x in self.waypoints])

    @staticmethod
    def _label_waypoints(city_from, city_to, path):
        points = polyline.decode(path)

        def _label_step(src_country, dst_country, points):
            if len(points) == 0:
                return []

            if len(points) == 1:
                lat, lng = points[0]
                return [Waypoint(lat, lng, Route._get_country(lat, lng))]

            if src_country == dst_country:
                return [Waypoint(lat, lng, src_country) for lat, lng in points]
            else:
                m = len(points)/2
                middle_country = Route._get_country(*points[m])
                return _label_step(src_country, middle_country, points[:m]) \
                       + _label_step(middle_country, dst_country, points[m:])

        return _label_step(city_from.country, city_to.country, points)

    @staticmethod
    def _get_country(lat, lng):
        gmaps_result = gmaps.reverse_geocode((lat, lng))
        return filter(lambda x: "country" in x["types"], gmaps_result[0]["address_components"])[0]["short_name"]


class Waypoint(object):

    def __init__(self, lat, lng, country):
        self.lat = lat
        self.lng = lng
        self.country = country


def _pick_step(routes):
    candidates = []
    for route in routes:
        if len(route["legs"]) > 1:
            logger.warn("More than one leg in {}".format(route))
            continue

        if "steps" not in route["legs"][0]:
            logger.warn("No steps in route {}".format(route))

        steps = route["legs"][0]["steps"]
        for step in steps:
            try:
                if step["travel_mode"] != "TRANSIT":
                    continue

                if step["transit_details"]["line"]["vehicle"]["type"] in PERMITTED_VEHICLES:
                    candidates.append(step)
            except KeyError:
                continue

    if candidates:
        return sorted(candidates, key=lambda x: x["distance"]["value"], reverse=True)[0]
    else:
        return None

def build_route(city_from, city_to):
    directions_result = gmaps.directions((city_from.latitude, city_from.longitude),
                                         (city_to.latitude, city_to.longitude),
                                         mode="transit",
                                         alternatives=True)

    step = _pick_step(directions_result)
    if step:
        return Route(city_from, city_to, step["polyline"]["points"])
    else:
        return None

if __name__ == '__main__':
    y = gmaps.reverse_geocode((40.714224, -73.961452))
    import json
    y = filter(lambda x: "country" in x["types"], y[0]["address_components"])[0]["short_name"]
    print y