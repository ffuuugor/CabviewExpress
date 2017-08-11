__author__ = 'ffuuugor'
from app.crawler.youtube import Video
from app.crawler.route import Route,Waypoint
from app.crawler.geo import RouteExtractor
from app.crawler.geo import City
from app.crawler.youtube import youtube_search
from app.crawler.youtube import Video
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
from geopy.distance import vincenty
import traceback

extractor = RouteExtractor(CITIES_PATH)
logger = logging.getLogger(__name__)


class Ride:
    _get_id = count(0).next

    def __init__(self, route, video):
        self.route = route
        self.video = video
        self.id = video.id

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        return hash(self.id)

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
            try:
                logger.debug("Processing {}".format(video.title))
                route_cities = extractor.extract_route(video.title, video.duration)
                if route_cities:
                    logger.info("Cities: {} - {}".format(*route_cities))
                    city_from, city_to = route_cities
                    route = build_route(city_from, city_to)
                    if route:
                        rides.append(Ride(route, video))

                else:
                    logger.info("Failed to extract route from '{}'".format(video.title))
            except:
                traceback.print_exc()
                logger.info("Some error")

    return list(set(rides))

def restore_rides(path):
    obj = pickle.load(open(path))
    rides = []

    for ride in obj:
        video = Video(
            title=ride.video.title,
            thumb=ride.video.thumb,
            id = ride.video.id,
            duration=ride.video.duration
        )

        try:
            logger.debug("Processing {}".format(video.title))
            route_cities = extractor.extract_route(video.title, video.duration)
            if route_cities:
                logger.info("Cities: {} - {}".format(*route_cities))
                city_from, city_to = route_cities
                route = build_route(city_from, city_to)
                if route:
                    rides.append(Ride(route, video))

            else:
                logger.info("Failed to extract route from '{}'".format(video.title))
        except:
            traceback.print_exc()
            logger.info("Some error")

    return list(set(rides))


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
                "ride_ids": list(set([ride.id for ride in srides]))
            } for spath, srides in segments
        ],
        "rides": [ride.to_json() for ride in rides]
    }


def make_constant_freq(ride, step=20):
    i = 0
    while i < len(ride.route.waypoints) - 1:
        wps = ride.route.waypoints
        dist = vincenty(wps[i].point(), wps[i+1].point()).meters
        if dist > step:
            extra_points_cnt = int(dist/step)
            start_lat = wps[i].lat
            start_lng = wps[i].lng
            start_country = wps[i].country

            step_lat = (wps[i].lat - wps[i+1].lat)/extra_points_cnt
            step_lng = (wps[i].lng - wps[i+1].lng) / extra_points_cnt

            extra_points = [Waypoint(start_lat + j*step_lat,
                                     start_lng + j*step_lng,
                                     start_country) for j in range(1,extra_points_cnt+1)]

            ride.route.waypoints = ride.route.waypoints[:i+1] + extra_points + ride.route.waypoints[i+1:]
            i+=extra_points_cnt

        i+=1

def run():
    # rides = make_rides(QUERY_LIST, 20)
    # rides = make_rides(["rail live"], 1)
    rides = pickle.load(open("rides_big2.pickle")) + pickle.load(open("rides_norway.pickle"))
    # pickle.dump(rides, open("rides_live.pickle","w"))
    # rides = restore_rides("rides_big2.pickle")

    # for ride in rides:
    #     make_constant_freq(ride)

    all_points = [wp for ride in rides for wp in ride.route.waypoints]
    all_points = [(p.lat, p.lng) for p in all_points]
    print "before", len(set(all_points))

    merge_paths(rides)

    all_points = [wp for ride in rides for wp in ride.route.waypoints]
    all_points = [(p.lat, p.lng) for p in all_points]
    print "after", len(set(all_points))

    segments = group_by_segments(rides)
    return json_format(rides, segments)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # json.dump(run(), open("../../static/test_data_live.json","w"), indent=4)

    obj = json.load(open("../../static/test_data10d.json"))
    json.dump(obj["segments"], open("../../static/final_segments.json", "w"), indent=4)
    json.dump(obj["rides"], open("../../static/final_rides.json", "w"), indent=4)
    # bad = "m4NQDGgOoBU"
    # for segm in obj["segments"]:
    #     if bad in segm["ride_ids"]:
    #         segm["ride_ids"].remove(bad)
    #
    # obj["segments"] = [x for x in obj["segments"] if x["ride_ids"]]
    # obj["rides"] = [x for x in obj["rides"] if x["id"] != bad]
    #
    # json.dump(obj, open("../../static/test_data10d.json", "w"), indent=4)