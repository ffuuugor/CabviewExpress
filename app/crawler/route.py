from geo import City
from googleapiclient.discovery import build
import googlemaps
import config
import logging
from itertools import count


gmaps = googlemaps.Client(config.DEVELOPER_KEY)
logger = logging.getLogger(__name__)

PERMITTED_VEHICLES = ["RAIL", "METRO_RAIL", "SUBWAY", "TRAM",
                      "MONORAIL", "HEAVY_RAIL", "COMMUTER_TRAIN", "HIGH_SPEED_TRAIN"]


class Route:

    _get_id = count(0).next

    def __init__(self, city_from, city_to, path):
        self.city_from = city_from
        self.city_to = city_to
        self.path = path
        self.id = self._get_id()


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
