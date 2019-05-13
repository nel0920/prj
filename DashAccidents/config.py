from pandas import read_csv, read_excel, DataFrame

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
#DAYSORT_2015 = dict(zip(['Friday', 'Monday', 'Saturday','Sunday', 'Thursday', 'Tuesday', 'Wednesday'], [4, 0, 5, 6, 3, 1, 2]))

acc = read_csv(csvAccLoc, index_col = 0, low_memory = False).dropna(how='any', axis = 0)
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