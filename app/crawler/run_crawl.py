__author__ = 'ffuuugor'
from youtube import Video
from geo import RouteExtractor
from geo import City
from youtube import youtube_search
from youtube import Video
import json
import os
from config import DATA_DIR, CITIES_PATH, QUERY_LIST
import logging
from collections import defaultdict
from route import build_route

extractor = RouteExtractor(CITIES_PATH)
logger = logging.getLogger(__name__)


class RouteVideo:

    def __init__(self, route, video):
        self.route = route
        self.video = video

    def to_json(self):
        return {"id": self.route.id,
                "path": self.route.path,
                "video": self.video.to_json()}


def process_videos(query_list=QUERY_LIST, pages=10):
    routes = []
    cities = defaultdict(list)

    for query in query_list:
        for video in youtube_search(query, pages):
            logger.debug("Processing {}".format(video.title))
            route_cities = extractor.extract_route(video.title, video.duration)
            if route_cities:
                city_from, city_to = route_cities
                route = build_route(city_from, city_to)
                if route:
                    route_video = RouteVideo(route, video)

                    cities[city_from].append(route_video)
                    cities[city_to].append(route_video)
                    routes.append(route_video)

            else:
                logger.info("Failed to extract route from '{}'".format(video.title))

    return cities, routes


def json_format(cities, routes):
    return {"cities": [{"city": city.to_json(),
                        "routes": [route.to_json() for route in city_routes]}
                       for city, city_routes in cities.items()],
            "routes": [route.to_json() for route in routes]}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cities, routes = process_videos(["cabview"], 2)
    print json.dumps(json_format(cities, routes), indent=4)