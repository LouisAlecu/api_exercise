from flask import Blueprint, jsonify, request
from .db_utils.schema import *
from datetime import datetime
from authenticator import Authenticator

data_blueprint = Blueprint("data", __name__)
authenticate = Authenticator()


@data_blueprint.route("/books", methods=["GET"], endpoint="books")
@authenticate.login_user
def books():
    # title = request.args.get("title")
    # authors = request.args.get("authors")
    json_data = request.get_json()
    author = json_data.get("author")
    title = json_data.get("title")
    user_credentials = authenticate.get_user_credentials()
    if user_credentials["user_type"] == "Not authenticated":
        return jsonify({"error": "Unauthorized access."})
    if not title and not author:
        return jsonify(
            {
                "error": f"""
                        You should send an object with either a title,
                        an author, or both. If both it will be interpreted 
                        that the title is meant to be written by that author.
                    """
            }
        )

    book_records = (
        db.session.query(
            ReportingCube.title,
            ReportingCube.author,
            ReportingCube.language,
            ReportingCube.publication_year,
            ReportingCube.ext_id,
            ReportingCube.isbn,
            ReportingCube.is_available,
        )
        .filter(ReportingCube.title == title if title else True)
        .filter(ReportingCube.author == author if author else True)
        .filter(ReportingCube.is_historical_data == False)
        .all()
    )
    print("book record is: ", book_records)

    # book_authors = [
    #     db.session.query(ReportingCube.author)
    #     .filter(ReportingCube.title == row[0])
    #     .filter(ReportingCube.is_historical_data == False)
    #     .all()
    #     for row in book_records
    # ]
    book_authors = []
    for row in book_records:
        book_authors_row = (
            db.session.query(ReportingCube.author)
            .filter(ReportingCube.title == row[0])
            .filter(ReportingCube.is_historical_data == False)
            .all()
        )
        book_authors_row = [row[0] for row in book_authors_row]
        book_authors.append(book_authors_row)
    print(book_authors)
    print("book_authors")
    # return_data = {
    #     "title": book_records[0][0],
    #     "authors": [row[1] for row in book_records],
    #     "language": book_records[0][2],
    #     "publication_year": book_records[0][3],
    #     "ext_id": book_records[0][4],
    #     "isbn": book_records[0][5],
    #     "is_available": book_records[0][6],
    # }
    # print("book is: ", return_data)
    # print("book_records is: ", book_records)
    return jsonify({"data": book_records})


@data_blueprint.route("/books/rental_status", methods=["PUT"], endpoint="rental_status")
@authenticate.login_user
def rental_status():
    title = request.args.get("title")
    author = request.args.get("authors")
    user_credentials = authenticate.get_user_credentials()
    if user_credentials["user_type"] in ("user", "Not authenticated"):
        return jsonify({"error": "Unauthorized access."})

    if request.args.get("rental_status") == "Available":
        is_available = True
    elif request.args.get("rental_status") == "Unavailable":
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
    historical_record = ReportingCube(
        book_id=record[0][0],
        author_id=record[0][1],
        title=record[0][2],
        author=record[0][3],
        language=record[0][4],
        publication_year=record[0][5],
        ext_id=record[0][6],
        isbn=record[0][7],
        is_available=record[0][8],
        is_historical_data=True,
        start_date=record[0][10],
        end_date=datetime.now().strftime("%Y-%m-%d"),
    )
    db.session.query(ReportingCube).filter(ReportingCube.title == title).filter(
        ReportingCube.author == author
    ).filter(ReportingCube.is_historical_data == False).update(
        {
            ReportingCube.is_available: is_available,
            ReportingCube.start_date: datetime.now().strftime("%Y-%m-%d"),
            ReportingCube.end_date: "01-01-2050",
        }
    )
    db.session.commit()
    db.session.add(historical_record)
    db.session.commit()
    return jsonify({"Updated": True})


# @data_blueprint.route("/wishlists", methods=["GET"], endpoint="wishlists")
# @authenticate.login_user
# def wishlists():
#     title = request.args.get("title")
#     author = request.args.get("authors")
#     user_credentials = authenticate.get_user_credentials()
#     if user_credentials["user_type"] == "Not authenticated":
#         return jsonify({"error": "Unauthorized access."})
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
#         .filter(ReportingCube.is_historical_data == False)
#         .all()
#     )
#     print(book)
#     return jsonify({"hello": book})
