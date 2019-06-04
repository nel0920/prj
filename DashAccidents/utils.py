# Import the libraries
import dash
from dash.dependencies import Input, Output, State

from DashAccidents import server, app 
from DashAccidents.config import *



## APP INTERACTIVITY THROUGH CALLBACK FUNCTIONS TO UPDATE THE CHARTS ##

# Callback function passes the current value of all three filters into the
# update functions.
# This on updates the bar.


@app.callback(Output(component_id='bar', component_property='figure'),
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
def updateBarChart(severity, weekdays, weathers, months, time):
    # The rangeslider is selects inclusively, but a python list stops before
    # the last number in a range
    hours = [i for i in range(time[0], time[1] + 1)]
    
    # Create a copy of the dataframe by filtering according to the values
    # passed in.
    # Important to create a copy rather than affect the global object.
    acc2 = DataFrame(acc[['Accident_Severity','Speed_limit','Number_of_Casualties']][(acc['Accident_Severity'].isin(severity)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin(hours))& (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))].groupby(['Accident_Severity','Speed_limit']).sum()).reset_index()

    # Create the field for the hovertext.  Doing this after grouping, rather
    # than
    #  immediately after loading the df.  Should be quicker this way.
    def barText(row):
        return 'Speed Limit: {}mph<br>{:,} {} accidents'.format(row['Speed_limit'], row['Number_of_Casualties'], row['Accident_Severity'].lower())
    acc2['text'] = acc2.apply(barText, axis=1)

    # One trace for each accidents severity
    traces = []
    for sev in severity:
        traces.append({
            'type' : 'bar',
            'y' : acc2['Number_of_Casualties'][acc2['Accident_Severity'] == sev],
            'x' : acc2['Speed_limit'][acc2['Accident_Severity'] == sev],
            'text' : acc2['text'][acc2['Accident_Severity'] == sev],
            'hoverinfo' : 'text',
            'marker' : {
                'color' : SEVERITY_LOOKUP[sev], # Use the colur lookup for consistency
            'line' : {'width' : 2,
                      'color' : '#333'}},
            'name' : sev,
        })  
        
    fig = {'data' : traces,
          'layout' : {
              'paper_bgcolor' : 'rgb(26,25,25)',
              'plot_bgcolor' : 'rgb(26,25,25)',
              'font' : {
                  'color' : 'rgb(250,250,250'
              },
              'height' : 300,
              'title' : 'Accidents by speed limit',
              'margin' : { # Set margins to allow maximum space for the chart
                  'b' : 25,
                  'l' : 30,
                  't' : 70,
                  'r' : 0
              },
              'legend' : { # Horizontal legens, positioned at the bottom to allow maximum space for the
                           # chart
                  'orientation' : 'h',
                  'x' : 0,
                  'y' : 1.01,
                  'yanchor' : 'bottom',
                  },
            'xaxis' : {
                'tickvals' : sorted(acc2['Speed_limit'].unique()), # Force the tickvals & ticktext just in case
                'ticktext' : sorted(acc2['Speed_limit'].unique()),
                'tickmode' : 'array'
            }
          }}
    
    # Returns the figure into the 'figure' component property, update the bar
    # chart
    return fig

# Pass in the values of the filters to the heatmap
@app.callback(Output(component_id='heatmap', component_property='figure'),
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
def updateHeatmap(severity, weekdays, weathers, months, time):
    # The rangeslider is selects inclusively, but a python list stops before
    # the last number in a range
    hours = [i for i in range(time[0], time[1] + 1)]
    # Take a copy of the dataframe, filtering it and grouping
    acc2 = DataFrame(acc[['Day_of_Week', 'Hour','Number_of_Casualties']][(acc['Accident_Severity'].isin(severity)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin(hours))& (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))].groupby(['Day_of_Week', 'Hour']).sum()).reset_index()

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
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
def updateMapBox(severity, weekdays, weathers, months, time):
    # List of hours again
    hours = [i for i in range(time[0], time[1] + 1)]
    # Filter the dataframe
    acc2 = acc[(acc['Accident_Severity'].isin(severity)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin(hours))& (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))]

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
            'text' : acc3['Local_Authority_(District)']# + '[lat:' + acc3['Latitude'] +', lng:' +  acc3['Longitude'] + ']' # Text will show location
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



@app.callback(Output(component_id='datatable-interactivity', component_property='data'),
    [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
def updateDataTable(severity, weekdays, weathers, months, time):
    # The rangeslider is selects inclusively, but a python list stops before
    # the last number in a range
    hours = [i for i in range(time[0], time[1] + 1)]
    
    # Create a copy of the dataframe by filtering according to the values
    # passed in.
    # Important to create a copy rather than affect the global object.
    acc2 = acc[(acc['Accident_Severity'].isin(severity)) & (acc['Day_of_Week'].isin(weekdays)) & (acc['Hour'].isin(hours))& (acc['Weather_Conditions'].isin(weathers)) & (acc['Month'].isin(months))]

    return acc2.to_dict('records')



    
@app.callback(Output("loading-output-1", "children"), [Input(component_id='severityChecklist', component_property='values'),
    Input(component_id='dayChecklist', component_property='values'),
    Input(component_id='weatherChecklist', component_property='values'),
    Input(component_id='monthChecklist', component_property='values'),
    Input(component_id='hourSlider', component_property='value'),])
def input_triggers_spinner(severity, weekdays, weathers, months, time):
    time.sleep(1)
    return 0