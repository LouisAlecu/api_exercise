from flask import Blueprint, jsonify, request
from .db_utils import db_toolbox as dbtb
from .db_utils.schema import *

data_blueprint = Blueprint("data", __name__)


@data_blueprint.route("/helloworld", methods=["GET"], endpoint="delete_portfolio")
def helloworld():
    # db_con = dbtb.connect_to_database({"db_path": "./sqlite_db"})
    # db_con.create_session()

    # db_con.read_query("SELECT * FROM authors")
    print(db.session.query(Author))
    return jsonify({"hello": "HelloWorld!"})
