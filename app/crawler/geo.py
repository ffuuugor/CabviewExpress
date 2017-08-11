# -*- coding: utf-8 -*-

__author__ = 'ffuuugor'
import nltk
from geopy.distance import vincenty
import codecs
from collections import defaultdict
import os
from app.crawler.config import DATA_DIR

MIN_SPEED = 15  #km/h
MAX_SPEED = 250 #km/h


class City:

    def __init__(self, main_name, names, country, population, latitude, longitude):
        self.main_name = main_name
        self.names = names
        self.country = country
        self.population = int(population)

        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return "(%s, %s)" % (self.main_name, self.country)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.main_name == other.main_name \
               and self.latitude == other.latitude \
               and self.longitude == other.longitude

    def __hash__(self):
        return hash(self.main_name) + 13*hash(self.latitude) + 13*13*hash(self.longitude)

    def to_json(self):
        return {
            "location":{
                "lat": self.latitude,
                "lng": self.longitude
            },
            "name": self.main_name,
            "country": self.country
        }

    def get_point(self):
        return self.latitude, self.longitude

    @staticmethod
    def distance(city1, city2):
        point1 = city1.get_point()
        point2 = city2.get_point()

        if point1 is not None and point2 is not None:
            return vincenty(point1, point2).meters
        else:
            return None

    @staticmethod
    def read_all(path):
        ret = []
        f = codecs.open(path, encoding='utf-8')

        for line in f:
            parts = line.split("\t")

            main_name = parts[2]

            names = set(parts[3].split(","))
            names.add(parts[1])
            names.add(parts[2])

            latitude = float(parts[4])
            longitude = float(parts[5])
            country = parts[8]
            population = parts[14]

            ret.append(City(main_name=main_name,
                            names=names,
                            country=country,
                            population=population,
                            latitude=latitude,
                            longitude=longitude))

        return ret


class RouteExtractor:

    exclude = [u"Train", u"City", u"Valley", u"Pacific"]

    def __init__(self, path):
        self.city_dict = self._read_cities(path) # text -> [(name, city)]

    @staticmethod
    def _read_cities(path):
        ret = defaultdict(list)
        for city in City.read_all(path):
            for city_name in city.names:
                if city_name:
                    key = city_name.split()[0]
                    ret[key].append((city_name, city))

        return ret

    @staticmethod
    def _tokenize(text):
        return nltk.word_tokenize(text=text)

    # {(start_pos, end_pos) -> [city_obj]}
    def _extract_city_objects(self, text):
        if type(text) != unicode:
            text = text.decode("utf-8")

        tokens = RouteExtractor._tokenize(text)
        ret = defaultdict(list)

        for startpos in range(0, len(tokens)):
            word = tokens[startpos]
            if word in self.city_dict:
                for cityname, cityobj in self.city_dict[word]:
                    citytokens = RouteExtractor._tokenize(cityname)
                    contains = True
                    for currpos in range(startpos, startpos+len(citytokens)):
                        if currpos >= len(tokens) or tokens[currpos] != citytokens[currpos - startpos]:
                            contains = False
                            break

                    if contains:
                        endpos = startpos+len(citytokens)
                        key = (startpos, endpos)

                        ret[key].append(cityobj)

        return ret

    def extract_route(self, text, duration):
        """
        
        :param text: 
        :param duration: in seconds
        :return: (city_from, city_to)
        """
        text = text.replace("-"," ")
        geo_info = self._extract_city_objects(text)

        candidate_pairs = []
        for (start1, end1) in geo_info.keys():
            for (start2, end2) in geo_info.keys():

                if end1 <= start2:
                    list_from = geo_info[(start1, end1)]
                    list_to = geo_info[(start2, end2)]

                    for city_from in list_from:
                        for city_to in list_to:
                            distance = City.distance(city_from, city_to)

                            speed = (distance * 3600) / (duration * 1000)
                            if MAX_SPEED >= speed >= MIN_SPEED:
                                candidate_pairs.append((city_from, city_to))

        if len(candidate_pairs) > 0:
            good_pair = sorted(candidate_pairs,
                               key=lambda (city_from, city_to): City.distance(city_from, city_to), reverse=True)[0]
        else:
            good_pair = None

        return good_pair


if __name__ == "__main__":
    extractor = RouteExtractor(os.path.join(DATA_DIR, "cities15000.txt"))

    print extractor._extract_city_objects("Cab Ride Norway : Trondheim - Bodø (Winter) Nordland Line")
