from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import DevelopmentConfig
from .views import data_blueprint
from .db_utils import db_toolbox as dbtb
from .db_utils.schema import *


def create_app():
    db_path = {"db_path": "./sqlite_db"}
    # db_con = dbtb.connect_to_database()
    # db_con.create_session()
    # create_database(db_con.get_db_engine())

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DevelopmentConfig)
    app.register_blueprint(data_blueprint)
    print(app.config)
    db = SQLAlchemy(app)
    print(db)
    return app
