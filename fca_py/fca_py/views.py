from flask import Blueprint, jsonify, request
from .db_utils.schema import *
from datetime import datetime

data_blueprint = Blueprint("data", __name__)


@data_blueprint.route("/books", methods=["GET"], endpoint="books")
def books():
    title = request.args.get("title")
    author = request.args.get("authors")

    if not title or not author:
        return f"You should send an object with title as a string and authors as a list of strings."

    book = (
        db.session.query(
            ReportingCube.title,
            ReportingCube.author,
            ReportingCube.language,
            ReportingCube.publication_year,
            ReportingCube.ext_id,
            ReportingCube.isbn,
            ReportingCube.is_available,
        )
        .filter(ReportingCube.title == title)
        .filter(ReportingCube.author == author)
        .filter(ReportingCube.is_historical_data == False)
        .all()
    )
    print(book)
    return jsonify({"hello": book})


@data_blueprint.route("/books/rental_status", methods=["PUT"], endpoint="rental_status")
def rental_status():
    title = request.args.get("title")
    author = request.args.get("authors")
    if request.args.get("rental_status") == "True":
        is_available = True
    elif request.args.get("rental_status") == "False":
        is_available = False
    else:
        return jsonify({"Error, wrong input in rental_status key": 123})
    print("is_available: ", is_available)
    if not title or not author:
        return f"You should send an object with title as a string and authors as a list of strings."

    record = (
        db.session.query(
            ReportingCube.book_id,
            ReportingCube.author_id,
            ReportingCube.title,
            ReportingCube.author,
            ReportingCube.language,
            ReportingCube.publication_year,
            ReportingCube.ext_id,
            ReportingCube.isbn,
            ReportingCube.is_available,
            ReportingCube.is_historical_data,
            ReportingCube.start_date,
            ReportingCube.end_date,
        )
        .filter(ReportingCube.title == title)
        .filter(ReportingCube.author == author)
        .filter(ReportingCube.is_historical_data == False)
    )

    db.session.query(ReportingCube).filter(ReportingCube.title == title).filter(
        ReportingCube.author == author
    ).update(
        {
            ReportingCube.is_available: is_available,
            ReportingCube.start_date: datetime.now().strftime("%Y-%m-%d"),
            ReportingCube.end_date: "01-01-2050",
        }
    )
    db.session.commit()
    return jsonify({"Updated": True})


# @data_blueprint.route("/books", methods=["GET"], endpoint="books")
# def books():
#     title = request.args.get("title")
#     author = request.args.get("authors")

#     if not title or not author:
#         return f"You should send an object with title as a string and authors as a list of strings."

#     book = (
#         db.session.query(
#             ReportingCube.title,
#             ReportingCube.author,
#             ReportingCube.language,
#             ReportingCube.publication_year,
#             ReportingCube.ext_id,
#             ReportingCube.isbn,
#             ReportingCube.is_available,
#         )
#         .filter(ReportingCube.title == title)
#         .filter(ReportingCube.author == author)
#         .all()
#     )
#     print(book)
#     return jsonify({"hello": book})
