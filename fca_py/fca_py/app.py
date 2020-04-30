from flask import Flask
from .config import ProductionConfig
from .views import data_blueprint
from .db_utils.schema import *


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(ProductionConfig)
    app.register_blueprint(data_blueprint)
    db.init_app(app)
    print("Restarted app.")
    with app.app_context():
        db.create_all()
        initialize_db(db, app.config["DB_INIT_DATA_PATH"])
    return app
