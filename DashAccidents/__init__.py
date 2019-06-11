# Import the libraries
import os
import dash
import dash_bootstrap_components as dbc
from flask import Flask
from DashAccidents.config import *

# To set up the flask object
server = Flask(__name__, static_url_path='/DashAccidents/static')
#server.secret_key = os.environ.get('secret_key', 'secret')
server.config.from_object(Config)
server.config.from_object(DevelopmentConfig)

# To set up the dash object
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.supress_callback_exceptions = True
app.scripts.config.serve_locally = True

#app.config['GOOGLEMAPS_KEY'] = GOOGLEMAP
#GoogleMaps(server)
from DashAccidents import views
