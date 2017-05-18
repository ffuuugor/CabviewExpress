__author__ = 'ffuuugor'
from youtube import Video
from geo import CityExtractor
from geo import City
from youtube import youtube_search
from youtube import Video
import json

MIN_SPEED = 15  #km/h
MAX_SPEED = 250 #km/h
extractor = CityExtractor("cities1000.txt")
def validate_one(video):
    geo_info = extractor.parse_text(video.title.replace("-"," "))

    #all_cities = list(set(reduce(lambda x,y: x+y, geo_info.values(), [])))
    # for key in geo_info.keys():
    #     geo_info[key] = sorted(geo_info[key], key = lambda x: x.population, reverse=True)

    candidate_pairs = []
    for (start1, end1) in geo_info.keys():
        for (start2, end2) in geo_info.keys():

            if end1 <= start2:
                list_from = geo_info[(start1, end1)]
                list_to = geo_info[(start2, end2)]

                for city_from in list_from:
                    for city_to in list_to:
                        distance = City.distance(city_from, city_to)

                        speed = (distance*3600)/(video.duration*1000)
                        if MAX_SPEED >= speed >= MIN_SPEED:
                            candidate_pairs.append((video, city_from, city_to, int(speed)))

    if len(candidate_pairs) > 0:
        good_pair = sorted(candidate_pairs, key = lambda (v,x,y,z): x.population + y.population, reverse=True)[0]
    else:
        good_pair = None

    return good_pair

def _make_text(video_id, thumb_url, title):
    return "<a href=http://www.youtube.com/watch?v=%s target=_blank><img src=%s></a> %s"\
           % (video_id, thumb_url, title)

def _make_dict(city_from, city_to, video, speed):
    return {"startLat":city_from.latitude,
            "startLng": city_from.longitude,
            "endLat": city_to.latitude,
            "endLng": city_to.longitude,
            "speed": speed,
            "text": _make_text(video.id, video.thumb, video.title)}
def process(query_list, pages=10):
    ret_dict = {}

    for query in query_list:
        for video in youtube_search(query, pages):
            res = validate_one(video)
            if res is not None:
                (video, city_from, city_to, speed) = res
                if (city_from, city_to) not in ret_dict:
                    ret_dict[(city_from, city_to)] = _make_dict(city_from, city_to, video, speed)

    ret = [x for x in ret_dict.values()]
    print json.dumps(ret,indent=0)



if __name__ == "__main__":
    process(["train view", "cabview", "cab view", "cabride", "cab ride", "rail view"],10)