import os
import dash

from flask import Flask
from DashAccidents.config import *



# instantiate a Flask object
server = Flask(__name__, static_url_path='/DashAccidents/static')
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(__name__, server=server,  assets_external_path='https://raw.githubusercontent.com/nel0920/prj/master/DashAccidents/static/')
app.config.supress_callback_exceptions = True
server.config.from_object(Config)
#app.config['GOOGLEMAPS_KEY'] = GOOGLEMAP
server.config.from_object(DevelopmentConfig)
#GoogleMaps(server)

from DashAccidents import views
