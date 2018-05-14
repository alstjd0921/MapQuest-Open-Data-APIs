import urllib
import json

MY_API_KEY = 'MuuupdEt1dE9KM0YHI4y3ylTOkwPczQo'
ROUTE_URL = 'http://open.mapquestapi.com/directions/v2/route'
ELEVATION_URL = 'http://open.mapquestapi.com/elevation/v1/profile'


# STEPS, TOTALDISTANCE, TOTALTIME, LATLONG, ELEVATION 의 각 출력을 위한 객체
class STEPS:
    def __init__(self, directions: [str]):
        self._directions = directions

    def output(self):
        print('DIRECTIONS')
        for dir in self._directions:
            print(dir)
        print()


class TOTALDISTANCE:
    def __init__(self, distance: float):
        self._distance = distance

    def output(self):
        print('TOTAL DISTANCE:', round(self._distance), 'miles')
        print()


class TOTALTIME:
    def __init__(self, minutes: float):
        self._minutes = minutes / 60

    def output(self):
        print("TOTAL TIME:", round(self._minutes), 'minutes')
        print()


class LATLONG:
    def __init__(self, lats: [str], longs: [str]):
        self._lats = lats
        self._longs = longs

    def output(self):
        print('LATLONGS')
        for i in range(len(self._lats)):
            print(self._lats[i], self._longs[i])
        print()


class ELEVATION:
    def __init__(self, heights: [float]):
        self._heights = heights

    def output(self):
        print('ELEVATIONS')
        for height in self._heights:
            print(round(height))

        print()


# 흐름 제어
def navigation():
    try:
        locations = get_locations()
        trip_info = get_outputs()
        route_url = make_route_url(locations)

        res = get_response(route_url)

        coords = get_coords(res)
        coords = merge_lats_and_longs(coords['lats'], coords['longs'])

        elevation_urls = []
        for i in range(0, len(coords), 2):
            latlong = str(coords[i]) + ',' + str(coords[i + 1])
            elevation_urls.append(make_elevation_url(latlong))

        elevation_data = []
        for url in elevation_urls:
            elevation_data.append(get_response(url))

        trip_info = create_outputs(trip_info, res, elevation_data)
        print()
        for data in trip_info:
            data.output()

    except urllib.error.HTTPError:  # 길을 찾지 못했다면
        print("NO ROUTE FOUND")

    except:  # 그 외의 에러
        print("MAPQUEST ERROR")

    else:  # 정상적인 출력을 마친 후
        print('Directions Courtesy of MapQuest; Map Data Copyright OpenStreetMap Contributors.')


# 위치 입력
def get_locations():
    num_of_locations = int(input())
    locations = []
    for i in range(num_of_locations):
        loc = input()
        locations.append(loc)

    return locations


# 출력해야할 정보 입력
def get_outputs():
    num_of_outputs = int(input())
    outputs = []
    for i in range(num_of_outputs):
        output = input()
        outputs.append(output)

    return outputs


# 출력 객체를 생성하는 함수
def create_outputs(output_types: [], mapquest_data: dict, elevation_data: [dict]):
    output_objects = []
    for type in output_types:
        if type == 'STEPS':
            directions = []
            maneuvers = mapquest_data['route']['legs'][0]['maneuvers']
            for i in range(len(maneuvers)):
                directions.append(maneuvers[i]['narrative'])

            type = STEPS(directions)
            output_objects.append(type)

        if type == 'TOTALDISTANCE':
            type = TOTALDISTANCE(mapquest_data['route']['distance'])
            output_objects.append(type)

        if type == 'TOTALTIME':
            type = TOTALTIME(mapquest_data['route']['time'])
            output_objects.append(type)

        if type == 'LATLONG':
            lats = get_coords(mapquest_data)['lats']
            longs = get_coords(mapquest_data)['longs']

            lats = add_direction(lats, 'lat')
            longs = add_direction(longs, 'long')

            type = LATLONG(lats, longs)
            output_objects.append(type)

        if type == 'ELEVATION':
            heights = []

            for i in range(len(elevation_data)):
                profile = elevation_data[i]['elevationProfile']

                for j in range(len(profile)):
                    heights.append(profile[j]['height'])

            type = ELEVATION(heights)
            output_objects.append(type)

    return output_objects


# coords를 만드는 함수
def get_coords(mapquest_data: dict):
    locations = mapquest_data['route']['locations']
    lats = []
    longs = []

    for i in range(len(locations)):
        lats.append(locations[i]['latLng']['lat'])
        longs.append(locations[i]['latLng']['lng'])

    lat_longs = {'lats': lats, 'longs': longs}

    return lat_longs


# coords에 방향을 추가하는 함수
def add_direction(coords: [], type: str):
    if type == 'lat':
        for i in range(len(coords)):
            if coords[i] > 0:
                coords[i] = str(round(coords[i], 2)) + 'N'
            else:
                coords[i] = str(round(coords[i], 2))[1:] + 'S'

    if type == 'long':
        for i in range(len(coords)):
            if coords[i] > 0:
                coords[i] = str(round(coords[i], 2)) + 'E'
            else:
                coords[i] = str(round(coords[i], 2))[1:] + 'W'

    return coords


# lats와 longs를 합치는 함수
def merge_lats_and_longs(lats: [], longs: []):
    latlongs = []
    for i in range(len(lats)):
        latlongs.append(lats[i])
        latlongs.append(longs[i])

    return latlongs


# 요청을 위한 url을 만드는 함수
def make_route_url(locations: []):
    url_parameters = [('key', MY_API_KEY), ('from', locations[0])]
    for i in range(1, len(locations)):
        url_parameters.append(('to', locations[i]))

    print(ROUTE_URL + '?' + urllib.parse.urlencode(url_parameters))
    return ROUTE_URL + '?' + urllib.parse.urlencode(url_parameters)


# Elevation 요청을 위한 url을 만드는 함수
def make_elevation_url(coords: str):
    url_parameters = [('key', MY_API_KEY), ('latLngCollection', coords)]

    return ELEVATION_URL + '?' + urllib.parse.urlencode(url_parameters)


# 요청을 받아오는 함수
def get_response(url: str):
    response = None
    try:
        response = urllib.request.urlopen(url)
        json_text = response.read().decode(encoding='utf-8')

        return json.loads(json_text)

    finally:
        if response != None:
            response.close()


if __name__ == '__main__':
    navigation()
