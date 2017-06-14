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
from itertools import count
import polyline
from merger import merge_paths
import pickle

extractor = RouteExtractor(CITIES_PATH)
logger = logging.getLogger(__name__)


class Ride:
    _get_id = count(0).next

    def __init__(self, route, video):
        self.route = route
        self.video = video
        self.id = self._get_id()

    def to_json(self):
        return {"id": self.id,
                "path": self.route.path,
                "from": self.route.city_from.to_json(),
                "to": self.route.city_to.to_json(),
                "video": self.video.to_json()}


def make_rides(query_list=QUERY_LIST, pages=10):
    rides = []

    for query in query_list:
        for video in youtube_search(query, pages):
            logger.debug("Processing {}".format(video.title))
            route_cities = extractor.extract_route(video.title, video.duration)
            if route_cities:
                city_from, city_to = route_cities
                route = build_route(city_from, city_to)
                if route:
                    rides.append(Ride(route, video))

            else:
                logger.info("Failed to extract route from '{}'".format(video.title))

    return rides


def group_by_segments(rides):
    segments = defaultdict(list)
    for ride in rides:
        points = polyline.decode(ride.route.path)
        for i in range(0, len(points)-1):
            src = points[i]
            dst = points[i+1]

            segments[_sorted_tuple((src, dst))].append(ride)

    logger.info("Got {} distinct segments".format(len(segments)))

    return [(polyline.encode([src, dst]), rides) for (src, dst), rides in segments.items()]


def _sorted_tuple(tpl):
    return tuple(sorted(tpl))


def json_format(rides, segments):
    return {
        "segments":[
            {
                "path": spath,
                "ride_ids": [ride.id for ride in srides]
            } for spath, srides in segments
        ],
        "rides": [ride.to_json() for ride in rides]
    }


def run():
    # rides = make_rides(["cabview"], 2)
    rides = pickle.load(open("rides.pickle"))

    all_points = [wp for ride in rides for wp in ride.route.waypoints]
    all_points = [(p.lat, p.lng) for p in all_points]
    print len(set(all_points))

    merge_paths(rides)

    all_points = [wp for ride in rides for wp in ride.route.waypoints]
    all_points = [(p.lat, p.lng) for p in all_points]
    print len(set(all_points))

    segments = group_by_segments(rides)
    return json_format(rides, segments)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    json.dumps(run(), indent=4)

