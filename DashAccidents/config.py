class Config(object):
    name = "Dash_App_Accidents"
    DEBUG = False
    TESTING = False
    MAPBOX = "pk.eyJ1IjoibmVsMDkyMCIsImEiOiIyMzM5YzgyNWQ4MDM5NzQ2N2NjM2MwODM1ZGE3OTVmOCJ9.zDLTPL1xCEwBzK4aVxAETg"
    GOOGLEMAP = "AIzaSyB-dPy4xZFJZ5wbpS_rQpFBTgGZt0C6zdY"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

