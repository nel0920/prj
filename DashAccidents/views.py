#!/usr/bin/env python

import sys
import os
import traceback
import json
from jinja2 import TemplateNotFound

from random import randint

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

from pandas import read_csv, read_excel, DataFrame

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons

from DashAccidents.config import *
from DashAccidents.utils import *



# matching route and handler


#server = Flask(__name__)
#server.secret_key = os.environ.get('secret_key', 'secret')
#app = dash.Dash(__name__, server=server,  static_external_path='http://localhost:5000/static/')
#app.config.supress_callback_exceptions = True
#app.config['GOOGLEMAPS_KEY'] = GOOGLEMAP
#app.config.from_object(DevelopmentConfig)
#GoogleMaps(server)

# Include the external CSS
cssUrl = ["https://rawgit.com/richard-muir/uk-car-accidents/master/road-safety.css", "https://use.fontawesome.com/releases/v5.8.2/css/all.css"]#, "https://codepen.io/chriddyp/pen/brPBPO.css"]
#cssURL = 'DashAccidents/static/css/main.css'
app.css.append_css({
    "external_url": cssUrl
})

## SETTING UP THE APP LAYOUT ##

# Main layout container
#app.layout = html.Div([#Tab controller
#    html.Div([dcc.Tabs(id="tabs", value='tab_uk', children=[dcc.Tab(label='UK', value='tab_uk'),
#            dcc.Tab(label='HK', value='tab_hk'),]),
 #       html.Div(id = 'tabs_content')])])

app.layout = html.Div([html.H1('Traffic Accidents in the UK',
                style={
                    'width' : '100%', 
                    'text-align': 'center',
                    'fontFamily' : FONT_FAMILY
                    }),            
                html.Div([# Holds the map & the widgets

                    dcc.Graph(id="map") # Holds the map in a div to apply styling to it
                 
                ],
                style={
                    "width" : '100%', 
                    'display' : 'inline-block', 
                    'paddingRight' : 50, 
                    'paddingLeft' : 50,
                    'boxSizing' : 'border-box',
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
                        {'label': sev + ' [{:,}]'.format(len(list(filter(lambda k: k==sev, acc['Accident_Severity'])))), 'value': sev} for sev in acc['Accident_Severity'].unique()
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
                        {'label': day[:3]# + ' [{:,}]'.format(len(list(filter(lambda k: k==day, acc['Day_of_Week']))))
                         , 'value': day} for day in sorted(acc['Day_of_Week'].unique(), key=lambda k: DAYSORT[k])
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
                html.Div('''Select the age group of the accident:''',
                    style={
                        'paddingTop' : 20,
                        'paddingBottom' : 10
                    }),
                dcc.Checklist(# Checklist for the dats of week, sorted using the sorting dict created
                 # earlier
                   id="ageChecklist",
                   options=[
                        {'label': AGES[age] , 'value': age} for age in sorted(AGES) if age >= 0
                        #{'label': DAYSORT[day][:3], 'value': day} for day in sorted(DAYSORT)
                    ],
                    values=[age for age in sorted(AGES) if age >= 0],
                    #values=[day for day in DAYSORT],
                    labelStyle={  # Different padding for the checklist elements
                        'display': 'inline-block',
                        'paddingRight' : 10,
                        'paddingLeft' : 10,
                        'paddingBottom' : 5,
                        },
                    ),
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
                    "width" : '100%', 
                    'display' : 'inline-block', 
                    'paddingLeft' : 50, 
                    'paddingRight' : 10,
                    'boxSizing' : 'border-box',
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
                dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[{"name": i, "id": i} for i in acc.columns],
                    data=acc.to_dict('records'),
                    editable=True,
                    #filtering=True,
                    sorting=True,
                    sorting_type="multi",
                    row_selectable="multi",
                    #row_deletable=True,
                    selected_rows=[],
                    pagination_mode="fe",
                        pagination_settings={
                            "displayed_pages": 1,
                            "current_page": 0,
                            "page_size": 15,
                        },
                        navigation="page",
                    css={
                        'width' : '100%', 
                        'paddingRight' : 50, 
                        'paddingLeft' : 50,
                        'display' : 'inline-block',
                        'boxSizing' : 'border-box',
                        'color': 'rgb(30, 30, 30)',  
                        'fontFamily' : FONT_FAMILY,
                    },
                     style_as_list_view=True,
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'fontWeight': 'bold'
                    },
                    style_cell={
                        'padding': '5px',
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    style_table={                      
                        'overflowX': 'scroll'
                    }),
                html.Div(id='datatable-interactivity-container'),
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
                        })]),
                dcc.Dropdown(
                    id='dropdown',
                    options=[{'label': i, 'value': i} for i in ['a', 'b', 'c']]
                ),
                html.Div(id='loading')],
                style={'paddingBottom' : 20})

#@app.callback(Output('tabs_content', 'children'),[Input('tabs', 'value')])
#def render_tab_content(tab):
# Holds the widgets & Descriptions
 #   if tab == 'tab_uk':   
#        return []
#    elif tab == 'tab_hk':
#        return []

@app.callback(Output('loading', 'children'), [Input('dropdown', 'value')])
def update_value(value):
    time.sleep(2)
    return 'You have computed {}'.format(value)

# Dash CSS
#app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# Loading screen CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})
