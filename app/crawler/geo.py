# -*- coding: utf-8 -*-

__author__ = 'ffuuugor'
import geograpy
import nltk
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import time
import codecs

geocoder = Nominatim()
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

    def get_point(self):
        return (self.latitude, self.longitude)

    @staticmethod
    def distance(city1, city2):
        point1 = city1.get_point()
        point2 = city2.get_point()

        if point1 is not None and point2 is not None:
            return vincenty(point1, point2).meters
        else:
            return None

class CityExtractor:

    exclude = [u"Train", u"City", u"Valley", u"Pacific"]

    def __init__(self, path):
        self.city_dict = {} # text -> [(name, city)]
        self._read_cities(path)

    def _read_cities(self, path):
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

            city_obj = City(main_name=main_name,
                            names=names,
                            country=country,
                            population=population,
                            latitude=latitude,
                            longitude=longitude)

            for name in names:
                if name is None or len(name) == 0:
                    continue

                key = name.split()[0]
                if key in CityExtractor.exclude:
                    continue


                if key in self.city_dict:
                    self.city_dict[key].append((name,city_obj))
                else:
                    self.city_dict[key] = [(name, city_obj)]

    @staticmethod
    def tokenize(text):
        return nltk.word_tokenize(text=text)

    # {(start_pos, end_pos) -> [city_obj]}
    def parse_text(self, text):
        if type(text) != unicode:
            text = text.decode("utf-8")

        tokens = CityExtractor.tokenize(text)
        ret = {}

        for startpos in range(0, len(tokens)):
            word = tokens[startpos]
            if word in self.city_dict:
                for (cityname, cityobj) in self.city_dict[word]:
                    citytokes = CityExtractor.tokenize(cityname)
                    contains = True
                    for currpos in range(startpos, startpos+len(citytokes)):
                        if currpos >= len(tokens) or tokens[currpos] != citytokes[currpos - startpos]:
                            contains = False
                            break

                    if contains:
                        endpos = startpos+len(citytokes)
                        key = (startpos, endpos)

                        if key in ret:
                            ret[key].append(cityobj)
                        else:
                            ret[key] = [cityobj]

        return ret


if __name__ == "__main__":
    extractor = CityExtractor()
    extractor.read_cities("cities15000.txt")

    print extractor.parse_text("Rotterdam Antwerpen 300 km/h, Thalys cab ride / cabinerit")

