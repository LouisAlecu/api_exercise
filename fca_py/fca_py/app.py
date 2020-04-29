from flask import Flask
from .config import DevelopmentConfig
from .views import data_blueprint
from .db_utils import db_toolbox as dbtb
from .db_utils.schema import *


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DevelopmentConfig)
    app.register_blueprint(data_blueprint)
    db.init_app(app)
    print("ASDF")
    with app.app_context():
        db.create_all()
        initialize_db(db, app.config["DB_INIT_DATA_PATH"])
    return app
