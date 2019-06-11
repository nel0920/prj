# To import the libraries
import dash
from dash.dependencies import Input, Output, State
from DashAccidents import server, app 
from DashAccidents.config import *

##### To define the callback method for the components on the web app
@app.callback(
    # To define the target object for the updates
    Output(component_id='barchart', component_property='figure'),
    # To define the target object that could affect the updates
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
# The method for updating the barchart
def updateBarChart(severities, weekdays, weathers, months, time):
    # To define the dataset for flitering the data set fomr controls and remove unused data fields
    accTemp = DataFrame(acc[['Accident_Severity','Speed_limit','Number_of_Casualties']][(acc['Accident_Severity'].isin(severities)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin([hour for hour in range(time[0], time[1] + 1)])) & (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))].groupby(['Accident_Severity','Speed_limit']).sum()).reset_index()

    # The method for processing the text when user hovering to the target
    def text(row):
        return 'In speed limit of {} mph<br>{:,}, it has {} accidents'.format(row['Speed_limit'], row['Number_of_Casualties'], row['Accident_Severity'].lower())
    # To apply the set of text into dataset
    accTemp['text'] = accTemp.apply(text, axis=1)
    # To create the empty traces object for storing the processed data
    traces = []

    for severity in severities:
        traces.append({
            'type' : 'bar', # To define the type of the chart
            'y' : accTemp['Number_of_Casualties'][accTemp['Accident_Severity'] == severity],
            'x' : accTemp['Speed_limit'][accTemp['Accident_Severity'] == severity],
            'text' : accTemp['text'][accTemp['Accident_Severity'] == severity],
            'hoverinfo' : 'text',
            'marker' : {
                'color' : SEVERITY_LOOKUP[severity], 
            'line' : {'width' : 2,
                      'color' : '#333'}},
            'name' : severity,
        })  
    # To define all reuired fields for the barchart
    fig = {'data' : traces,
          'layout' : {
              'paper_bgcolor' : BACKGROUND_COLOUR ,
              'plot_bgcolor' : BACKGROUND_COLOUR ,
              'font' : {
                  'color' : COLOUR 
              },
              'height' : HEIGHT_OF_COMPONENT - 200,
              'title' : 'Accidents by speed limit',
              'margin' : { 
                  'b' : 25,
                  'l' : 30,
                  't' : 70,
                  'r' : 0
              },
              'legend' : { 
                  'orientation' : 'h',
                  'x' : 0,
                  'y' : 1.01,
                  'yanchor' : 'bottom',
                  },
            # To enforce the tickvals & ticktext to show in graph
            'xaxis' : {
                'tickvals' : sorted(accTemp['Speed_limit'].unique()), 
                'ticktext' : sorted(accTemp['Speed_limit'].unique()),
                'tickmode' : 'array'
            }
          }}
    return fig

@app.callback(
    # To define the target object for the updates
    Output(component_id='heatmap', component_property='figure'),
    # To define the target object that could affect the updates
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
# The method for updating the heatmap
def updateHeatmap(severities, weekdays, weathers, months, time):
    # To transfer the hours from time object
    hours = [hour for hour in range(time[0], time[1] + 1)]
    # To define the dataset for flitering the data set fomr controls and remove unused data fields
    accTemp = DataFrame(acc[['Day_of_Week', 'Hour','Number_of_Casualties']][(acc['Accident_Severity'].isin(severities)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin(hours)) & (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))].groupby(['Day_of_Week', 'Hour']).sum()).reset_index()

    # The method for processing the text when user hovering to the target
    def text(row):
        return 'Time : {:02d}:00<br>Day : {}<br>Number of casualties: {}'.format(row['Hour'], row['Day_of_Week'], row['Number_of_Casualties'])
    # To apply the set of text into dataset
    accTemp['text'] = accTemp.apply(text, axis=1)

    # To define the sorted days and empty object for the next step of processes
    days = sorted(accTemp['Day_of_Week'].unique(), key=lambda k: DAY[k])
    z = []
    text = []

    # To process data into required format
    for day in days:
        row = accTemp['Number_of_Casualties'][accTemp['Day_of_Week'] == day].values.tolist()
        temp = accTemp['text'][accTemp['Day_of_Week'] == day].values.tolist()
        z.append(row)
        text.append(temp)
    
    # To define the processed data into traces object
    traces = [{
        'type' : 'heatmap',# To define the type of chart
        'x' : hours,
        'y' : days,
        'z' : z,
        'text' : text,
        'hoverinfo' : 'text',
        'colorscale' : [[0, 'rgb(0, 0, 0)'], [0.25, 'rgb(30, 0, 100)'], [0.55, 'rgb(120, 0, 100)'], [0.8, 'rgb(160, 90, 0)'], [1, 'rgb(230, 200, 0)']],
    }]
    
    # To define all reuired fields for the heatmap
    fig = {'data' : traces, # To deine data right here
          'layout' : {
              'paper_bgcolor' : BACKGROUND_COLOUR ,
              'font' : {
                  'color' : COLOUR
              },
              'height' : HEIGHT_OF_COMPONENT - 200,
              'title' : 'Accidents by time and day',
              'margin' : {
                  'b' : 50,
                  'l' : 70,
                  't' : 50,
                  'r' : 0,
              },
              # To enforce the tickvals & ticktext to show in graph
              'xaxis' : {
                  'ticktext' : hours, 
                  'tickvals' : hours,
                  'tickmode' : 'array', 
              }
          }}
    return fig

@app.callback(
    # To define the target object for the updates
    Output(component_id='map', component_property='figure'),
    # To define the target object that could affect the updates
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
# The method for updating the barchart
def updateMapBox(severities, weekdays, weathers, months, time):     
    # To define the dataset for flitering the data set fomr controls and remove unused data fields
    accTemp = acc[(acc['Accident_Severity'].isin(severities)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin([hour for hour in range(time[0], time[1] + 1)])) & (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))]

    #def text(row):
    #    return '{} <br> ({},
    #    {})'.format(accTemp['Local_Authority_(District)'],accTemp['Latitude'],
    #    accTemp['Longitude'])
    #accTemp['text'] = accTemp.apply(text, axis=1)
    # To create the empty traces object for storing the processed data
    traces = []

    for severity in sorted(severities, reverse=True):
        sample = 1

        if severity == 'Slight':
            sample = SLIGHT_FRAC
        elif severity == 'Serious':
            sample = SERIOUS_FRAC

        accTemp_ = accTemp[accTemp['Accident_Severity'] == severity].sample(frac=sample)
        
        traces.append({
            'type' : 'scattermapbox',# To define the type of map
            'mode' : 'markers',
            'lat' : accTemp_['Latitude'],
            'lon' : accTemp_['Longitude'],
            'marker' : {
                'color' : SEVERITY_LOOKUP[severity], 
                'size' : 2,
            },
            'hoverinfo' : 'text',
            'name' : severity,
            'legendgroup' : severity,
            'showlegend' : False,
            'text' : accTemp_['Local_Authority_(District)']# + '[lat:' + accTemp_['Latitude'] +', lng:' + accTemp_['Longitude'] + ']' # Text will
                                                       # show location
            #'text' : accTemp['text']
        })
        traces.append({
            'type' : 'scattermapbox',
            'mode' : 'markers',
            'lat' : [0],
            'lon' : [0],
            'marker' : {
                'color' : SEVERITY_LOOKUP[severity],
                'size' : FONT_SIZE,
            },
            'name' : severity,
            'legendgroup' : severity,
            
        })

    layout = {
        'height' : HEIGHT_OF_COMPONENT,
        'paper_bgcolor' : BACKGROUND_COLOUR ,
              'font' : {
                  'color' : COLOUR
              }, 
        'autosize' : True,
        'hovermode' : 'closest',
        'mapbox' : {
            'accesstoken' : MAPBOX,
            'center' : {  
                'lat' : CENTER_LAT,
                'lon' : CENTER_LON
            },
            'zoom' : ZOOM,
            'style' : 'dark',   
        },
        'margin' : {'t' : 0,
                   'b' : 0,
                   'l' : 0,
                   'r' : 0},
        'legend' : {
            'font' : {'color' : COLOUR},
             'orientation' : 'h',
             'x' : 0,
             'y' : 1.01
        }
    }

    fig = dict(data=traces, layout=layout) 

    return fig

@app.callback(
    # To define the target object for the updates
    Output(component_id='linechart', component_property='figure'),
    # To define the target object that could affect the updates
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
# The method for updating the linechart
def updateLineChart(severities, weekdays, weathers, months, time):
    # To define the dataset for flitering the data set fomr controls and remove unused data fields    
    accTemp = acc[['Accident_Severity', 'Month']][(acc['Accident_Severity'].isin(severities)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin([hour for hour in range(time[0], time[1] + 1)])) & (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))] 
    # To add the data into dataset   
    accTemp['Total'] = 1
    # To create the empty traces object for storing the processed data
    traces = []
    # To filter unused data & get only required data field
    accTemp_ = accTemp[['Accident_Severity','Month', 'Total']].groupby(['Accident_Severity','Month']).sum(axis=0).reset_index()
    # The method for processing the text when user hovering to the target
    
    def text(row):
        return '{} 2017 <br>{:,} {} accidents'.format(MONTHS[row['Month']], row['Total'], row['Accident_Severity'].lower())
    # To apply the set of text into dataset
    accTemp_['text'] = accTemp_.apply(text, axis=1)

    for severity in severities:
      traces.append({
          'type' : 'line',# To define the type of the chart
          'y' : accTemp_['Total'][accTemp_['Accident_Severity'] == severity],
          'x' : accTemp_['Month'][accTemp_['Accident_Severity'] == severity].apply(lambda k: MONTHS[k]),
          'text' : accTemp_['text'][accTemp_['Accident_Severity'] == severity],
          'hoverinfo' : 'text',
          'marker' : {
              'color' : SEVERITY_LOOKUP[severity], 
          'line' : {'width' : 3,
                    'color' : '#333'}},
          'name' : severity,
      })  

    # To define all reuired fields for the barchart2
    fig = {
      'data' : traces, 
      'layout' : {
        'paper_bgcolor' : BACKGROUND_COLOUR ,
        'plot_bgcolor' : BACKGROUND_COLOUR ,
        'font' : {
            'color' : COLOUR
        },
        'height' : 500,
        'title' : 'Accidents by month',
        'margin' : {
            'b' : 25,
            'l' : 30,
            't' : 70,
            'r' : 0
        },
        'legend' : {
            'orientation' : 'h',
            'x' : 0,
            'y' : 1.01,
            'yanchor' : 'bottom',
            },
        # To enforce the tickvals & ticktext to show in graph
        'xaxis' : {
            'tickvals' : sorted(accTemp_['Month'].apply(lambda k: MONTHS[k])),
            'ticktext' : sorted(accTemp_['Month'].apply(lambda k: MONTHS[k])),
            'tickmode' : 'array'
        }
      }
    }
    return fig

@app.callback(
    # To define the target object for the updates
    Output(component_id='barchart2', component_property='figure'),
    # To define the target object that could affect the updates
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value')])
# The method for updating the barchart2
def updateBarChart2(severities, weekdays, weathers, months, time):
    # To define the dataset for flitering the data set fomr controls and remove unused data fields
    accTemp = acc[['Accident_Severity', 'Weather_Conditions']][(acc['Accident_Severity'].isin(severities)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin([hour for hour in range(time[0], time[1] + 1)])) & (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))]    
    # To add the data into dataset
    accTemp['Total'] = 1
    # To create the empty traces object for storing the processed data
    traces = []    
    # To filter unused data & get only required data field
    accTemp_ = accTemp[['Accident_Severity','Weather_Conditions', 'Total']][acc['Weather_Conditions'].isin(range(1,7))].groupby(['Accident_Severity','Weather_Conditions']).sum(axis=0).reset_index()
     # The method for processing the text when user hovering to the target
    def text(row):
        return 'Over {:,} {} accidents happened in {} .'.format(row['Total'], row['Accident_Severity'].lower(), WEATHERS[row['Weather_Conditions']])
    # To apply the set of text into dataset
    accTemp_['text'] = accTemp_.apply(text, axis=1)

    for severity in severities:
      traces.append({
          'type' : 'bar',# To define the type of chart
          'y' : accTemp_['Total'][accTemp_['Accident_Severity'] == severity],
          'x' : accTemp_['Weather_Conditions'][accTemp_['Accident_Severity'] == severity].apply(lambda k: WEATHERS[k]),
          'marker' : {
              'color' : SEVERITY_LOOKUP[severity], 
          'line' : {'width' : 3,
                    'color' : '#333'}},
          'name' : severity
      })  
    
    # To define all reuired fields for the barchart2
    fig = {'data' : traces,
          'layout' : {
              'paper_bgcolor' : BACKGROUND_COLOUR ,
              'plot_bgcolor' : BACKGROUND_COLOUR ,
              'font' : {
                  'color' : COLOUR
              },
              'height' : HEIGHT_OF_COMPONENT,
              'title' : 'Accidents by weather',
              'margin' : { 
                  'b' : 25,
                  'l' : 30,
                  't' : 70,
                  'r' : 0
              },
              'legend' : { 
                  'orientation' : 'b',
                  'x' : 0,
                  'y' : 1.01,
                  'yanchor' : 'bottom',
                  },
            # To enforce the tickvals & ticktext to show in graph
            'xaxis' : {
                'tickvals' : sorted(accTemp_['Weather_Conditions'].apply(lambda k: WEATHERS[k])), 
                'ticktext' : sorted(accTemp_['Weather_Conditions'].apply(lambda k: WEATHERS[k])),
                'tickmode' : 'array',
                'tickangle' : 4,
                'fonts':{
                  'size': FONT_SIZE
                }
            }
          }}
    return fig

@app.callback(
    # To define the target object for the updates
    Output(component_id='datatable-interactivity', component_property='data'),
    # To define the target object that could affect the updates
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
# The method for updating the data table
def updateDataTable(severities, weekdays, weathers, months, time):
    # To return the data frame object directly by using the implemented filtering fuctions    
    return (acc[(acc['Accident_Severity'].isin(severities)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin( [hour for hour in range(time[0], time[1] + 1)])) & (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))]).to_dict('records')

# The loading callback function that aims to show the loading screen when any of control has been changed    
@app.callback(
    # To define the target object for the updates
    Output("loading-output-1", "children"),
    # To define the target object that could affect the updates
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value')])
# The method for showing the loading screen
def input_triggers_spinner(severities, weekdays, weathers, months, time):
    time.sleep(1)
    return 0