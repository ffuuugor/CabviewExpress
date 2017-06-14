import json
import polyline
import itertools
import math
from geopy.distance import EARTH_RADIUS
from scipy.spatial.distance import euclidean
from scipy.cluster.hierarchy import fclusterdata
from geopy.distance import vincenty
import numpy as np
from collections import defaultdict
from route import Waypoint
import logging

logger = logging.getLogger(__name__)


def latlng_to_xyz(lat, lng):
    lat = math.radians(lat)
    lng = math.radians(lng)

    x = math.cos(lat) * math.cos(lng) * EARTH_RADIUS
    y = math.cos(lat) * math.sin(lng) * EARTH_RADIUS
    z = math.sin(lat) * EARTH_RADIUS

    return x, y, z


def merge_paths(rides):
    waypoints = list(itertools.chain(*[ride.route.waypoints for ride in rides]))
    waypoints = sorted(waypoints, key=lambda x: x.country)

    logger.info("Merging {} rides with {} total waypoints".format(len(rides), len(waypoints)))

    for country, group in itertools.groupby(waypoints, key=lambda x: x.country):
        waypoints = list(group)
        country_lat_lng_points = [(x.lat, x.lng) for x in waypoints]
        country_xyz_points = [latlng_to_xyz(lat, lng) for lat, lng in country_lat_lng_points]

        logger.debug("Processing {} with {} waypoints".format(country, len(country_xyz_points)))

        cluster_labels = fclusterdata(country_xyz_points, 0.01, criterion="distance", metric="euclidean")
        centroids = cluster_centroids(zip(country_lat_lng_points, cluster_labels))

        for i in range(0, len(waypoints)):
            new_lat, new_lng = centroids[cluster_labels[i]-1]
            waypoints[i].lat = new_lat
            waypoints[i].lng = new_lng


def cluster_centroids(labeled_points):
    bycluster = defaultdict(list)
    for point, label in labeled_points:
        bycluster[label].append(point)

    centroids = [np.mean(np.array(x), axis=0) for x in bycluster.values()]
    return centroids

if __name__ == '__main__':
    l = [1,1,2]

    for k, g in itertools.groupby(l):
        for x in g:
            print k, x


