from flask import Blueprint, jsonify, request

# from .db_utils import db_toolbox as dbtb
from .db_utils.schema import *

data_blueprint = Blueprint("data", __name__)


@data_blueprint.route("/helloworld", methods=["GET"], endpoint="delete_portfolio")
def helloworld():
    print(db.engine)

    return jsonify({"hello": "HelloWorld!"})
