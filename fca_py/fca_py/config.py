import os
import sys


class FlaskConfigTemplate(object):

    DEBUG = True
    TESTING = True
    DB_SERVER = "localhost"
    SQLALCHEMY_DATABASE_URI = "sqlite:///sqlite_db"
    DB_INIT_DATA_PATH = "/input_data/data.csv"
    REPORTS_DIR_PATH = "/output_data/report_generated.json"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(FlaskConfigTemplate):

    DEBUG = True
    TESTING = True
    DB_SERVER = "localhost"
    SQLALCHEMY_DATABASE_URI = "sqlite:///sqlite_db"
    DB_INIT_DATA_PATH = "/input_data/data.csv"
    REPORTS_DIR_PATH = "/output_data/report_generated.json"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(FlaskConfigTemplate):
    pass
