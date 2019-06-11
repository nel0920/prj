# Import the libraries
from pandas import read_csv, read_excel, DataFrame

# The configuration of the web app
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

##### Global variables, datasets and initialisation
# To define the key for map
MAPBOX = "pk.eyJ1IjoibmVsMDkyMCIsImEiOiIyMzM5YzgyNWQ4MDM5NzQ2N2NjM2MwODM1ZGE3OTVmOCJ9.zDLTPL1xCEwBzK4aVxAETg"
GOOGLEMAP = "AIzaSyB-dPy4xZFJZ5wbpS_rQpFBTgGZt0C6zdY"

##### Pre-defined variables for web app layout
# To define the colours for each type of accident
SEVERITY_LOOKUP = { 'Fatal' : 'red', 'Serious' : 'orange', 'Slight' : 'yellow' }

SLIGHT_FRAC = 0.1
SERIOUS_FRAC = 0.5

# To define the global font family
FONT_FAMILY = "PT Sans" 
# To define the global font size
FONT_SIZE = 8

# To defeine the global padding
PADDING_TOP = 10
PADDING_BOTTOM = 10
PADDING_LEFT = 15
PADDING_RIGHT = 15

# To define the global colour
COLOUR = 'rgb(250,250,250)'
BACKGROUND_COLOUR = 'rgb(26,25,25)'

# To define the global size
HEIGHT_OF_COMPONENT = 500

# Golbal variable of map
ZOOM = 5.2

CENTER_LAT = 52.489 #Birmingham
CENTER_LON = -1.898 #Birmingham

##### Pre-defined variables for data processing
# The method for getting the csv files location
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

# To get and define the csv file location to from method getCsvLoc as a variable
csvAccLoc = getCsvLoc('2017A')
csvCasLoc = getCsvLoc('2017C')
csvVecLoc = getCsvLoc('2017V')
xlsDGLoc = getCsvLoc('DG')

# To read the csv file dataset guideline fo each page
data_guide_days = read_excel(xlsDGLoc, 'Day of Week')
data_guide_severitys = read_excel(xlsDGLoc, 'Accident Severity')
data_guide_ages = read_excel(xlsDGLoc, 'Age Band')
data_guide_weathers = read_excel(xlsDGLoc, 'Weather')
data_guide_ladistricts = read_excel(xlsDGLoc, 'Local Authority (District)')

# To define the global variables from the dataset guideline
SEVERITYS = dict(zip(data_guide_severitys['code'], data_guide_severitys['label']))
DAYS = dict(zip(data_guide_days['code'], data_guide_days['label']))
AGES = dict(zip(data_guide_ages['code'], data_guide_ages['label']))
WEATHERS = dict(zip(data_guide_weathers['code'], data_guide_weathers['label']))
LADISTRICTS = dict(zip(data_guide_ladistricts['code'], data_guide_ladistricts['label']))
MONTHS = dict(zip([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],['JAN', 'FEB', 'MAR', 'ARP', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']))
DAY = dict(zip(data_guide_days['label'], data_guide_days['code']))
#DAY_2015 = dict(zip(['Friday', 'Monday', 'Saturday','Sunday', 'Thursday', 'Tuesday', 'Wednesday'], [4, 0, 5, 6, 3, 1, 2]))

##### To read different type of datasets in 2017
# To read the traffic accident dataset of UK in 2017
acc = read_csv(csvAccLoc, index_col = 0, low_memory = False).dropna(how='any', axis = 0)
#cas = read_csv(csvCasLoc, index_col = 0, low_memory = False).dropna(how='any',
#axis = 0)
#vec = read_csv(csvVecLoc, index_col = 0, low_memory = False).dropna(how='any',
#axis = 0)

##### To modify the dataset for removing unused or unrelated data fields ans also replacing the database values from the actual values in the guideline
acc['Accident_Severity'] = acc['Accident_Severity'].apply(lambda k: SEVERITYS[k])
acc['Hour'] = acc['Time'].apply(lambda x: int(x[:2]))
acc['Day_of_Week'] = acc['Day_of_Week'].apply(lambda k: DAYS[k])
acc['Local_Authority_(District)'] = acc['Local_Authority_(District)'].apply(lambda k: LADISTRICTS[k])
acc['Month'] = acc['Date'].apply(lambda x: int((x[:5])[3:]))
# To remove the unrelated data
acc = acc[~acc['Speed_limit'].isin([0, 10])]
acc = acc[~acc['Weather_Conditions'].isin([0, 9])]

#vec['Age_Band_of_Driver'] = vec['Age_Band_of_Driver'].apply(lambda k: AGES[k])
#cas['Age_Band_of_Driver'] = cas['Age_Band_of_Casualty'].apply(lambda k: AGES[k])
