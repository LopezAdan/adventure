from flask import Flask


import requests
import json, csv
import pandas as pd
import datetime
from geojson import Feature, FeatureCollection, Point, dump



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/postmethod', methods=['POST'])
def postmethod():
    data = request.get_json()
    print(data)

class yelpQuery:
    yelp_url = "https://api.yelp.com/v3/businesses/search"
    api_key = "Ph5ToEVanaZhUmnCWJDAWFnlCah55sgnz3r91I-sC6ObZI8KCAyXDtI4cAqs7hoUg0GgquEJCnHhMBBoXfe6P2uPgafPpa5GkDLAGDtbeliu2JzileqOOHdPAN6zXXYx"
    business_keys = ['id', 'name', 'latitude', 'longitude', 'url']

    def __init__(self, lat, lon, time, radius = 200, filename='businesses'):
        self.latitude = lat
        self.longitude = lon
        self.radius = radius
        self.time = time
        self.filename = filename
        self.headers = {'Authorization': 'Bearer %s' % yelpQuery.api_key}

    def yelp_main(self):
        self.yelp_search()
        self.parse_businesses()
        self.write_businesses()

    def yelp_search(self):
        self.params = {'latitude': self.latitude, 'longitude': self.longitude, 'radius': self.radius, 'open_at': self.time}
        self.req = requests.get(yelpQuery.yelp_url, params=self.params, headers= self.headers)
        if self.req.status_code == 200:
            return self.req
        else:
            print('JSON status code:{}'.format(self.req.status_code))

    def parse_businesses(self):
        self.business_dict = {business_key:[] for business_key in yelpQuery.business_keys}

        businesses = json.loads(self.req.text)
        businesses_parsed = businesses['businesses']

        for business in businesses_parsed:
            self.business_dict['id'].append(business['id'])
            self.business_dict['name'].append(business['name'])
            self.business_dict['latitude'].append(business['coordinates']['latitude'])
            self.business_dict['longitude'].append(business['coordinates']['longitude'])
            self.business_dict['url'].append(business['url'])

    def write_businesses(self):
        self.businesses_df = pd.DataFrame.from_dict(self.business_dict)
        self.businesses_df.to_csv('{}.csv'.format(self.filename), encoding='utf-8', index=False, header = False)
        print('File {0}{1} written successfully'.format(self.filename, '.csv'))



lat = 37.866510
lon = -122.259800
radius = 200 # meters
curr_time = datetime.datetime.now().hour
unix_time = 1572138000 # 6 pm Oct 26


yq = yelpQuery(lat, lon, unix_time, radius)
yq.yelp_main()


features = []
with open('businesses.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for id, name, latitude, longitude, url in reader:
        latitude, longitude = map(float, (latitude, longitude))
        features.append(
            Feature(
                geometry = Point((longitude, latitude)),
                properties = {
                    'name': name,
                    'url': url
                }
            )
        )

collection = FeatureCollection(features)
with open("businesses.geojson", "w") as f:
    dump(collection,f)
