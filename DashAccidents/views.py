# To import the libraries
import sys
import os
import traceback
import json

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons

from DashAccidents.config import *
from DashAccidents.utils import *

from pandas import read_csv, read_excel, DataFrame
from jinja2 import TemplateNotFound
from random import randint

##### To set up the web app layout
# To include the external css
cssUrl = [#"https://raw.githubusercontent.com/nel0920/prj/development/DashAccidents/main.css",
          "https://use.fontawesome.com/releases/v5.8.2/css/all.css"]

app.css.append_css({  "external_url": cssUrl })

days = acc['Day_of_Week'].unique()

# To set up the main layout container
app.layout = html.Div([
                html.Div([
                    dcc.Graph(id = "map") 
                ],
                style = {
                    "width" : '100%', 
                    'paddingRight' : PADDING_RIGHT, 
                    'paddingLeft' : PADDING_LEFT,
                    'boxSizing' : 'border-box',
                    'display' : 'inline-block',
                    'fontFamily' : FONT_FAMILY
                    }),
                # The heading of the web app
                html.Div([html.H3('The United Kindom suffered {:,} traffic accidents in 2017.'.format(len(acc)),
                    style = {
                        'paddingTop' : PADDING_TOP,
                        'fontFamily' : FONT_FAMILY
                    }),
                # The control section that contains few filtering controls
                html.Div('Here is the control section that allow you to select which kind of the data is avaliable in the data set:',),
                # The control section that enables to select which severity of the accidents could be showed on the dataset                
                html.Div([html.Div('Select the severity of the accident:',
                        style  =  {
                            'paddingTop' : PADDING_TOP,
                            'paddingBottom' : PADDING_BOTTOM
                        }),
                    dcc.Checklist(# The checklist for selecting the differernt kind of serertiy of the accident
                        options = [ { 
                            'label' : (severity + ' [{:,}]').format(len(list(filter(lambda k: k == severity, acc['Accident_Severity'])))), 'value': severity
                        } for severity in acc['Accident_Severity'].unique()], # The dataset field of Accident_Severity does not store the actual text of severity, it need to be replace the field value into the catual text for showing as a label option 
                        values = [severity for severity in acc['Accident_Severity'].unique()],
                        labelStyle = {
                            'paddingRight' : PADDING_RIGHT,
                            'paddingLeft' : PADDING_LEFT,
                            'paddingBottom' : PADDING_BOTTOM,
                            'display': 'inline-block'
                            },
                        id = "severityChecklist",)],
                        style = {
                            'width' : '50%', 
                            'float' : 'left'
                        }),
                # The control section that enables to select which day of the accidents could be showed on the dataset    
                html.Div([html.Div('Select the day of the accident:',
                    style = {
                        'paddingTop' : PADDING_TOP,
                        'paddingBottom' : PADDING_BOTTOM
                    }),
                dcc.Checklist(# The checklist for selecting the differernt day of the accident
                    options = [{ 
                        'label': day[:3],# To avoid the options to be too long for display
                        'value': day
                    } for day in sorted(days, key = lambda k : DAY[k])],
                    values = [ day for day in days ],
                    labelStyle = { 
                        'paddingRight' : PADDING_RIGHT,
                        'paddingLeft' : PADDING_LEFT,
                        'paddingBottom' : PADDING_BOTTOM,
                        'display': 'inline-block'
                        },
                    id = "dayChecklist",)],
                    style = {
                        'width' : '50%', 
                        'float' : 'right'  
                    }),  
                # The control section that enables to select which hour of the accidents could be showed on the dataset    
                html.Div('Select the hours in which the accident occurred (24h clock):',
                    style = {
                        'paddingTop' : PADDING_TOP,
                        'paddingBottom' : PADDING_BOTTOM
                    }),
                dcc.RangeSlider(
                    id = "hourSlider",
                    min = -acc['Hour'].min(),
                    max = acc['Hour'].max(),
                    count = 1,
                    step = 1,
                    value = [acc['Hour'].min(), acc['Hour'].max()],
                    marks = {str(hour) : str(hour) for hour in range(acc['Hour'].min(), acc['Hour'].max() + 1)})],
                    style = {
                        "width" : '100%', 
                        'paddingLeft' : PADDING_LEFT, 
                        'paddingRight' : PADDING_RIGHT,
                        'paddingBottom' : PADDING_BOTTOM,
                        'boxSizing' : 'border-box',
                        'display' : 'inline-block'
                        }),                        
                # The control section that enables to select which month of the accidents could be showed on the dataset                
                html.Div('Select the month of accident:',
                    style = {
                        'paddingTop' : PADDING_TOP,
                        'paddingBottom' : PADDING_BOTTOM,                        
                        'paddingLeft' : PADDING_LEFT
                    }),
                dcc.Checklist(
                    options = [{
                        'label': MONTHS[month], 
                        'value': month
                    } for month in MONTHS],
                    values = [month for month in acc['Month']],
                    labelStyle = {  
                        'paddingRight' : PADDING_RIGHT,
                        'paddingLeft' : PADDING_LEFT,
                        'paddingBottom' : PADDING_BOTTOM,
                        'display': 'inline-block'
                        },
                    id = "monthChecklist", 
                    style = {
                    "width" : '100%', 
                    'paddingLeft' : PADDING_LEFT, 
                    'paddingRight' : PADDING_RIGHT,
                    'boxSizing' : 'border-box',
                    'display' : 'inline-block'
                    }),                
                # The control section that enables to select which weather of the accidents could be showed on the dataset    
                html.Div('Select the weather condition of accident:',
                    style = {
                        'paddingTop' : PADDING_TOP,
                        'paddingBottom' : PADDING_BOTTOM,                        
                        'paddingLeft' : PADDING_LEFT, 
                    }),
                dcc.Checklist(
                    options = [{
                        'label': WEATHERS[weather],
                        'value': weather
                    } for weather in sorted(WEATHERS) if weather >=  0],
                    values = [weather for weather in acc['Weather_Conditions'].unique()],
                    labelStyle = {  
                        'paddingRight' : PADDING_RIGHT,
                        'paddingLeft' : PADDING_LEFT,
                        'paddingBottom' : PADDING_BOTTOM,
                        'display': 'inline-block'
                        },
                    id = "weatherChecklist", 
                    style = {
                    "width" : '100%', 
                    'paddingLeft' : PADDING_LEFT, 
                    'paddingRight' : PADDING_RIGHT,
                    'paddingBottom' : PADDING_BOTTOM,
                    'boxSizing' : 'border-box',
                    'display' : 'inline-block'
                    }),
                
                # The sub layout of containing the heatmap & bar chart
                html.Div([
                    html.Div([
                        dcc.Graph(id = "heatmap",),],
                    style = {
                        "width" : '60%', 
                        'float' : 'left', 
                        'paddingRight' : PADDING_RIGHT, 
                        'paddingLeft' : PADDING_LEFT,
                        'display' : 'inline-block', 
                        'boxSizing' : 'border-box'
                        }),
                    html.Div([
                        dcc.Graph(id = "barchart",)
                    ],
                    style = {
                        "width" : '40%', 
                        'float' : 'right', 
                        'paddingRight' : PADDING_RIGHT, 
                        'paddingLeft' : PADDING_LEFT,
                        'display' : 'inline-block', 
                        'boxSizing' : 'border-box'
                        })]),
                html.Div([
                    dcc.Graph(id = "linechart")
                ],
                style = {
                    "width" : '100%', 
                    'paddingRight' : PADDING_RIGHT, 
                    'paddingLeft' : PADDING_LEFT,
                    'paddingBottom' : PADDING_BOTTOM,
                    'display' : 'inline-block', 
                    'boxSizing' : 'border-box',
                    'fontFamily' : FONT_FAMILY
                    }),
                html.Div([
                        dcc.Graph(id = "barchart2",)
                    ],
                    style = {
                        "width" : '100%', 
                        'paddingRight' : PADDING_RIGHT, 
                        'paddingLeft' : PADDING_LEFT,
                        'paddingBottom' : PADDING_BOTTOM,
                        'display' : 'inline-block', 
                        'boxSizing' : 'border-box',
                        'fontFamily' : FONT_FAMILY
                    }),
                dash_table.DataTable(id = 'datatable-interactivity',
                    columns = [{"name": i, "id": i} for i in acc.columns],
                    data = acc.to_dict('records'),
                    editable = True,
                    #filtering = True,
                    sorting = True,
                    sorting_type = "multi",
                    row_selectable = "multi",
                    #row_deletable = True,
                    selected_rows = [],
                    pagination_mode = "fe",
                        pagination_settings = {
                            "displayed_pages": 1,
                            "current_page": 0,
                            "page_size": 15,
                        },
                        navigation = "page",
                    css = {
                        'width' : '100%',
                        'paddingTop' : PADDING_TOP, 
                        'paddingRight' : PADDING_RIGHT, 
                        'paddingLeft' : PADDING_LEFT,
                        'display' : 'inline-block',
                        'boxSizing' : 'border-box',
                        'color': COLOUR,  
                        'fontFamily' : FONT_FAMILY
                    },
                     style_as_list_view = True,
                    style_header = {
                        'backgroundColor': BACKGROUND_COLOUR,
                        'fontWeight': 'bold'
                    },
                    style_cell = {
                        'padding': '5px',
                        'backgroundColor': BACKGROUND_COLOUR,
                        'color': COLOUR
                    },
                    style_table = {                      
                        'overflowX': 'scroll'
                    }),
                html.Div(
                    id = 'datatable-interactivity-container',
                    style = {                            
                        'paddingTop' : PADDING_TOP, 
                        'paddingRight' : PADDING_RIGHT, 
                        'paddingLeft' : PADDING_LEFT
                    }),
                # It states where is the data set from
                html.Div([
                    html.Div('The orginal data source from: https://data.gov.uk/dataset/road-accidents-safety-data, ',
                        style = {                            
                            'paddingTop' : PADDING_TOP, 
                            'paddingRight' : PADDING_RIGHT, 
                            'paddingLeft' : PADDING_LEFT, 
                            'fontFamily' : FONT_FAMILY,
                            'fontSize' : FONT_SIZE
                        })
                    ]),
                # The loading section that only appear when the control changed
                html.Div([dcc.Loading(id = "loading-1", children = [html.Div(id = "loading-output-1", style = {
                                'display':'block',
                                'float':'center',
                                'position':'absolute'
                            })], type = "default", fullscreen = True,
                            style = {
                                'display':'block',
                                'float':'center',
                                'position':'absolute',
                                'background-color': 'rgba(0, 0, 0, 0.8)'
                            }),])],
                style = {
                    'paddingBottom' : PADDING_BOTTOM,
                    'color' : COLOUR,
                    'background-color' : BACKGROUND_COLOUR
                    })

