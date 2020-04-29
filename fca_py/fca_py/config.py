import os
import sys


class FlaskConfigTemplate(object):

    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:////home/louis/repos/testing/fca/fca_py/fca_py/sqlite_db"
    )
    DB_INIT_DATA_PATH = "/home/louis/repos/testing/fca/input_data/data.csv"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(FlaskConfigTemplate):

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:////home/louis/repos/testing/fca/fca_py/fca_py/sqlite_db"
    )
    DB_INIT_DATA_PATH = "/home/louis/repos/testing/fca/input_data/data.csv"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
