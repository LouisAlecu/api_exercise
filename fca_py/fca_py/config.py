import os
import sys


class FlaskConfigTemplate(object):

    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/louis/repos/testing/fca/fca_py/fca_py"


class DevelopmentConfig(FlaskConfigTemplate):

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/louis/repos/testing/fca/fca_py/fca_py"
