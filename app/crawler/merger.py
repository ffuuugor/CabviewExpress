import json
import polyline
import itertools
import math
from geopy.distance import EARTH_RADIUS
from scipy.spatial.distance import euclidean
from scipy.cluster.hierarchy import fclusterdata
from scipy.cluster.vq import whiten,kmeans, vq
from geopy.distance import vincenty
import numpy as np
from collections import defaultdict
from app.crawler.route import Waypoint
import logging


logger = logging.getLogger(__name__)

BEARABLE_CLUSTER_SIZE = 5000


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

        wh = whiten(country_xyz_points)
        k_guess = max(1,len(country_xyz_points)/BEARABLE_CLUSTER_SIZE)
        k_centroids = kmeans(wh,k_guess)[0]
        k_labels = vq(wh, k_centroids)[0]

        k_labeled = sorted(zip(country_xyz_points,country_lat_lng_points,waypoints,k_labels), key=lambda x: x[3])
        logger.debug("Got {} miniclusters".format(len(k_centroids)))
        for key, gr in itertools.groupby(k_labeled, key=lambda x:x[3]):
            gr = list(gr)
            k_waypoints = [x[2] for x in gr]
            k_lat_lng_points = [x[1] for x in gr]
            k_xyz_points = [x[0] for x in gr]
            logger.debug("Running {} minicluster with {} waypoints".format(key, len(k_waypoints)))
            cluster_labels = fclusterdata(np.array(k_xyz_points), 0.2, criterion="distance", metric="euclidean")
            centroids = cluster_centroids(zip(k_lat_lng_points, cluster_labels))
            logger.debug("Got {} hierarhical clusters".format(len(set(cluster_labels))))

            for i in range(0, len(k_waypoints)):
                new_lat, new_lng = centroids[cluster_labels[i]-1]
                k_waypoints[i].lat = new_lat
                k_waypoints[i].lng = new_lng


def cluster_centroids(labeled_points):
    bycluster = defaultdict(list)
    for point, label in labeled_points:
        bycluster[label].append(point)

    centroids = [np.mean(np.array(x), axis=0) for x in bycluster.values()]
    return centroids


