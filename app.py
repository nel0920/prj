#!/usr/bin/env python
import sys
import os
import traceback
import json
from jinja2 import TemplateNotFound

from random import randint

import dash

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from pandas import read_csv, read_excel, DataFrame

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons

import dash
from dash.dependencies import Input, Output, State

class Config(object):
    name = "Dash_App_Accidents"
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True


### GLOBALS, DATA & INTIALISE THE APP ###
MAPBOX = "pk.eyJ1IjoibmVsMDkyMCIsImEiOiIyMzM5YzgyNWQ4MDM5NzQ2N2NjM2MwODM1ZGE3OTVmOCJ9.zDLTPL1xCEwBzK4aVxAETg"
GOOGLEMAP = "AIzaSyB-dPy4xZFJZ5wbpS_rQpFBTgGZt0C6zdY"

# Make the colours consistent for each type of accident
SEVERITY_LOOKUP = {'Fatal' : 'red',
                    'Serious' : 'orange',
                    'Slight' : 'yellow'}
SEVERITY_LOOKUP_2015 = {'Fatal' : 'red',
                    'Serious' : 'orange',
                    'Slight' : 'yellow'}
# Need to downsample the number of Slight and Serious accidents to display them
# on the map.  These fractions reduce the number plotted to about 10k.
# There are only about 10k fatal accidents so don't need to downsample these
SLIGHT_FRAC = 0.1
SERIOUS_FRAC = 0.5

# This dict allows me to sort the weekdays in the right order
# 2017



# Set the global font family
FONT_FAMILY = "PT Sans" 

# Read in data from csv stored on github
csv_2017 = 'DashAccidents/static/data/accidents_2017.csv'  
csv_2016 = 'DashAccidents/static/data/accidents_2016.csv'  
#csvLoc = 'DashAccidents/static/data/accidents2015_V.csv'
#csvLoc = 'DashAccidents/static/data/accidents_2017.test.csv'
#csvLoc =
#'https://raw.githubusercontent.com/richard-muir/uk-car-accidents/master/accidents2015_V.csv'
xlsLoc = 'DashAccidents/static/data/data_guides.xls'


def getCsvLoc(argument):
    switcher = {
        '2017A': 'DashAccidents/static/data/accidents_2017.csv',
        '2017C': 'DashAccidents/static/data/casualtes_2017.csv',
        '2017V': 'DashAccidents/static/data/vehicles_2017.csv',
        '2016': 'DashAccidents/static/data/accidents_2016.csv',
        '2015': 'DashAccidents/static/data/accidents_2015.csv',
        'DG':'DashAccidents/static/data/data_guides.xls'
    }
    return switcher.get(argument, "None")

csvAccLoc = getCsvLoc('2017A')
csvCasLoc = getCsvLoc('2017C')
csvVecLoc = getCsvLoc('2017V')
xlsDGLoc = getCsvLoc('DG')

data_guide_days = read_excel(xlsDGLoc, 'Day of Week')
data_guide_severitys = read_excel(xlsDGLoc, 'Accident Severity')

SEVERITYS = dict(zip(data_guide_severitys['code'], data_guide_severitys['label']))
DAYS = dict(zip(data_guide_days['code'], data_guide_days['label']))

DAYSORT = dict(zip(data_guide_days['label'], data_guide_days['code']))
#DAYSORT_2015 = dict(zip(['Friday', 'Monday', 'Saturday','Sunday', 'Thursday',
#'Tuesday', 'Wednesday'], [4, 0, 5, 6, 3, 1, 2]))
acc = read_csv(csvAccLoc, index_col = 0).dropna(how='any', axis = 0)
cas = read_csv(csvCasLoc, index_col = 0).dropna(how='any', axis = 0)
vec = read_csv(csvVecLoc, index_col = 0).dropna(how='any', axis = 0)

acc['Accident_Severity'] = acc['Accident_Severity'].apply(lambda k: SEVERITYS[k])
acc['Day_of_Week'] = acc['Day_of_Week'].apply(lambda k: DAYS[k])
# Remove observations where speed limit is 0 or 10.  There's only three and it
# adds a lot of
#  complexity to the bar chart for no material benefit
acc = acc[~acc['Speed_limit'].isin([0, 10])]
# Create an hour column
acc['Hour'] = acc['Time'].apply(lambda x: int(x[:2]))

#data = read_excel(loc, index_col=0)



# Set up the Dash instance.
# instantiate a Flask object
server = Flask(__name__, static_url_path='/DashAccidents/static')
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(__name__, server=server)#,  assets_external_path='https://raw.githubusercontent.com/nel0920/prj/master/DashAccidents/static/')
app.config.supress_callback_exceptions = True
server.config.from_object(Config)
#app.config['GOOGLEMAPS_KEY'] = GOOGLEMAP
server.config.from_object(DevelopmentConfig)
#GoogleMaps(server)

# Include the external CSS
cssURL = "https://rawgit.com/richard-muir/uk-car-accidents/master/road-safety.css"
#cssURL = 'DashAccidents/static/css/main.css'
app.css.append_css({
    "external_url": cssURL
})

# matching route and handler
@server.route("/", defaults={"filename": "index.html"})
@server.route("/<path:filename>", methods = ["GET", "POST"])
def display(filename):
    try:
        return render_template(filename)
    except TemplateNotFound:
        return server.send_static_file(filename)

@server.route('/abc')
def hello_world():
    return render_template('test1.html')
## SETTING UP THE APP LAYOUT ##

# Main layout container
app.layout = html.Div([html.Div([html.H1('Traffic Accidents in the UK',
                style={
                    'paddingLeft' : 50,
                    'fontFamily' : FONT_FAMILY
                    }),
                html.Div([html.H3('''In 2017, the UK suffered {:,} traffic accidents, many of them fatal.'''.format(len(acc)),
                    style={
                        'fontFamily' : FONT_FAMILY
                    }),
                html.Div('''You can explore when and where the accidents happened using these filters.''',),
                html.Div('''Select the severity of the accident:''',
                    style={
                        'paddingTop' : 20,
                        'paddingBottom' : 10
                    }),
                dcc.Checklist(# Checklist for the three different severity values
                    options=[
                        {'label': sev, 'value': sev} for sev in acc['Accident_Severity'].unique()
                    ],
                    values=[sev for sev in acc['Accident_Severity'].unique()],
                    labelStyle={
                        'display': 'inline-block',
                        'paddingRight' : 10,
                        'paddingLeft' : 10,
                        'paddingBottom' : 5,
                        },
                    id="severityChecklist",),
                html.Div('''Select the day of the accident:''',
                    style={
                        'paddingTop' : 20,
                        'paddingBottom' : 10
                    }),
                dcc.Checklist(# Checklist for the dats of week, sorted using the sorting dict created
                 # earlier
                    options=[
                        {'label': day[:3], 'value': day} for day in sorted(acc['Day_of_Week'].unique(), key=lambda k: DAYSORT[k])
                        #{'label': DAYSORT[day][:3], 'value': day} for day in sorted(DAYSORT)
                    ],
                    values=[day for day in acc['Day_of_Week'].unique()],
                    #values=[day for day in DAYSORT],
                    labelStyle={  # Different padding for the checklist elements
                        'display': 'inline-block',
                        'paddingRight' : 10,
                        'paddingLeft' : 10,
                        'paddingBottom' : 5,
                        },
                    id="dayChecklist",),
                html.Div('''Select the hours in which the accident occurred (24h clock):''',
                    style={
                        'paddingTop' : 20,
                        'paddingBottom' : 10
                    }),
                dcc.RangeSlider(# Slider to select the number of hours
                    id="hourSlider",
                    count=1,
                    min=-acc['Hour'].min(),
                    max=acc['Hour'].max(),
                    step=1,
                    value=[acc['Hour'].min(), acc['Hour'].max()],
                    marks={str(h) : str(h) for h in range(acc['Hour'].min(), acc['Hour'].max() + 1)})],
                style={
                    "width" : '60%', 
                    'display' : 'inline-block', 
                    'paddingLeft' : 50, 
                    'paddingRight' : 10,
                    'boxSizing' : 'border-box',
                    }),            
                html.Div([# Holds the map & the widgets

                    dcc.Graph(id="map") # Holds the map in a div to apply styling to it
                 
                ],
                style={
                    "width" : '100%', 
                    'float' : 'centre', 
                    'display' : 'inline-block', 
                    'paddingRight' : 50, 
                    'paddingLeft' : 50,
                    'boxSizing' : 'border-box',
                    'fontFamily' : FONT_FAMILY
                    }),
                html.Div([# Holds the heatmap & barchart (60:40 split)
                    html.Div([# Holds the heatmap
                        dcc.Graph(id="heatmap",),],
                    style={
                        "width" : '60%', 
                        'float' : 'left', 
                        'display' : 'inline-block', 
                        'paddingRight' : 5, 
                        'paddingLeft' : 50,
                        'boxSizing' : 'border-box'
                        }),
                    html.Div([# Holds the barchart
                        dcc.Graph(id="bar",)
                        #style={'height' : '50%'})
                    ],
                    style={
                        "width" : '40%', 
                        'float' : 'right', 
                        'display' : 'inline-block', 
                        'paddingRight' : 50, 
                        'paddingLeft' : 5,
                        'boxSizing' : 'border-box'
                        })]),
                html.Div([# Add a source annotation and a note for the downsampling
                    html.Div('Source: https://data.gov.uk/dataset/road-accidents-safety-data',
                        style={
                            'fontFamily' : FONT_FAMILY,
                            'fontSize' : 8,
                            'fontStyle' : 'italic'
                        }),
                    html.Div('Note: Serious and slight accidents were downsampled to allow for speedier map plotting. Other charts are unaffected.',
                        style={
                            'fontFamily' : FONT_FAMILY,
                            'fontSize' : 8,
                            'fontStyle' : 'italic'
                        })])],
                style={'paddingBottom' : 20})])

@app.callback(Output('tabs_content', 'children'),
              [Input('tabs', 'value')])
def render_tab_content(tab):
    # Holds the widgets & Descriptions
    if tab == 'tab_uk':   
        return []
    elif tab == 'tab_hk':
        return []
        




## APP INTERACTIVITY THROUGH CALLBACK FUNCTIONS TO UPDATE THE CHARTS ##

# Callback function passes the current value of all three filters into the
# update functions.
# This on updates the bar.


# Pass in the values of the filters to the heatmap
@app.callback(Output(component_id='heatmap', component_property='figure'),
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
def updateHeatmap(severity, weekdays, time):
    # The rangeslider is selects inclusively, but a python list stops before
    # the last number in a range
    hours = [i for i in range(time[0], time[1] + 1)]
    # Take a copy of the dataframe, filtering it and grouping
    acc2 = DataFrame(acc[['Day_of_Week', 'Hour','Number_of_Casualties']][(acc['Accident_Severity'].isin(severity)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin(hours))].groupby(['Day_of_Week', 'Hour']).sum()).reset_index()

    # Apply text after grouping
    def heatmapText(row):
        return 'Day : {}<br>Time : {:02d}:00<br>Number of casualties: {}'.format(row['Day_of_Week'],row['Hour'], row['Number_of_Casualties'])
    acc2['text'] = acc2.apply(heatmapText, axis=1)
    
    # Pre-sort a list of days to feed into the heatmap
    days = sorted(acc2['Day_of_Week'].unique(), key=lambda k: DAYSORT[k])

    # Create the z-values and text in a nested list format to match the shape
    # of the heatmap
    z = []
    text = []
    for d in days:
        row = acc2['Number_of_Casualties'][acc2['Day_of_Week'] == d].values.tolist()
        t = acc2['text'][acc2['Day_of_Week'] == d].values.tolist()
        z.append(row)
        text.append(t)

    # Plotly standard 'Electric' colourscale is great, but the maximum value is
    # white, as is the
    #  colour for missing values.  I set the maximum to the penultimate maximum
    #  value,
    #  then spread out the other.  Plotly colourscales here:
    #  https://github.com/plotly/plotly.py/blob/master/plotly/colors.py

    Electric = [[0, 'rgb(0,0,0)'], [0.25, 'rgb(30,0,100)'],
        [0.55, 'rgb(120,0,100)'], [0.8, 'rgb(160,90,0)'],
        [1, 'rgb(230,200,0)']]
    
    # Heatmap trace
    traces = [{
        'type' : 'heatmap',
        'x' : hours,
        'y' : days,
        'z' : z,
        'text' : text,
        'hoverinfo' : 'text',
        'colorscale' : Electric,
    }]
        
    fig = {'data' : traces,
          'layout' : {
              'paper_bgcolor' : 'rgb(26,25,25)',
              'font' : {
                  'color' : 'rgb(250,250,250'
              },
              'height' : 300,
              'title' : 'Accidents by time and day',
              'margin' : {
                  'b' : 50,
                  'l' : 70,
                  't' : 50,
                  'r' : 0,
              },
              'xaxis' : {
                  'ticktext' : hours, # for the tickvals and ticktext with one for each hour
                  'tickvals' : hours,
                  'tickmode' : 'array', 
              }
          }}
    return fig

# Feeds the filter outputs into the mapbox
@app.callback(Output(component_id='map', component_property='figure'),
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
def updateMapBox(severity, weekdays, time):
    # List of hours again
    hours = [i for i in range(time[0], time[1] + 1)]
    # Filter the dataframe
    acc2 = acc[(acc['Accident_Severity'].isin(severity)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin(hours))]

    # Once trace for each severity value
    traces = []
    for sev in sorted(severity, reverse=True):
        # Set the downsample fraction depending on the severity
        sample = 1
        if sev == 'Slight':
            sample = SLIGHT_FRAC
        elif sev == 'Serious':
            sample = SERIOUS_FRAC
        # Downsample the dataframe and filter to the current value of severity
        acc3 = acc2[acc2['Accident_Severity'] == sev].sample(frac=sample)
            
        # Scattermapbox trace for each severity
        traces.append({
            'type' : 'scattermapbox',
            'mode' : 'markers',
            'lat' : acc3['Latitude'],
            'lon' : acc3['Longitude'],
            'marker' : {
                'color' : SEVERITY_LOOKUP[sev], # Keep the colour consistent
                'size' : 2,
            },
            'hoverinfo' : 'text',
            'name' : sev,
            'legendgroup' : sev,
            'showlegend' : False,
            'text' : acc3['Local_Authority_(District)'] # Text will show location
        })
        
        # Append a separate marker trace to show bigger markers for the legend.
        #  The ones we're plotting on the map are too small to be of use in the
        #  legend.
        traces.append({
            'type' : 'scattermapbox',
            'mode' : 'markers',
            'lat' : [0],
            'lon' : [0],
            'marker' : {
                'color' : SEVERITY_LOOKUP[sev],
                'size' : 10,
            },
            'name' : sev,
            'legendgroup' : sev,
            
        })
    layout = {
        'height' : 500,
        'paper_bgcolor' : 'rgb(26,25,25)',
              'font' : {
                  'color' : 'rgb(250,250,250'
              }, # Set this to match the colour of the sea in the mapbox colourscheme
        'autosize' : True,
        'hovermode' : 'closest',
        'mapbox' : {
            'accesstoken' : MAPBOX,
            'center' : {  # Set the geographic centre - trial and error, birmingham
                'lat' : 52.489,
                'lon' : -1.898
            },
            'zoom' : 5.2,
            'style' : 'dark',   # Dark theme will make the colours stand out
        },
        'margin' : {'t' : 0,
                   'b' : 0,
                   'l' : 0,
                   'r' : 0},
        'legend' : {
            'font' : {'color' : 'white'},
             'orientation' : 'h',
             'x' : 0,
             'y' : 1.01
        }
    }
    fig = dict(data=traces, layout=layout) 
    return fig

if __name__ == '__main__':
    app.server.run(debug=False, threaded=True)