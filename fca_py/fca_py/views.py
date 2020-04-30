from flask import Blueprint, jsonify, request
from db_utils.schema import *
from datetime import datetime
from authenticator import Authenticator

data_blueprint = Blueprint("data", __name__)
authenticate = Authenticator()


@data_blueprint.route("/books", methods=["GET"], endpoint="books")
@authenticate.login_user
def books():
    json_data = request.get_json()
    author = json_data.get("author")
    title = json_data.get("title")
    user_credentials = authenticate.get_user_credentials()
    print(user_credentials)
    if user_credentials["user_type"] not in ("user", "staff"):
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
    return_data = [
        {
            "title": book_records[idx][0],
            "authors": book_authors[idx],
            "language": book_records[idx][2],
            "publication_year": book_records[idx][3],
            "ext_id": book_records[idx][4],
            "isbn": book_records[idx][5],
            "is_available": book_records[idx][6],
        }
        for idx in range(len(book_records))
    ]
    return jsonify({"data": return_data})


@data_blueprint.route("/books/rental_status", methods=["PUT"], endpoint="rental_status")
@authenticate.login_user
def rental_status():
    json_data = request.get_json()
    book_id = json_data.get("book_id")
    rental_status = json_data.get("rental_status")
    user_credentials = authenticate.get_user_credentials()
    print(user_credentials)
    if user_credentials["user_type"] != "staff":
        return jsonify({"error": "Unauthorized access."})

    if rental_status == "Available":
        is_available = True
    elif rental_status == "Unavailable":
        is_available = False
    else:
        return jsonify({"Bad Request": "wrong input in rental_status key"})
    if not book_id:
        return f"You should send an object with the book_id and rental_status desired <Available|Unavailable>."

    book_records = (
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
        .filter(ReportingCube.book_id == book_id)
        .filter(ReportingCube.is_historical_data == False)
    )

    historical_records = [
        ReportingCube(
            book_id=record[0],
            author_id=record[1],
            title=record[2],
            author=record[3],
            language=record[4],
            publication_year=record[5],
            ext_id=record[6],
            isbn=record[7],
            is_available=record[8],
            is_historical_data=True,
            start_date=record[10],
            end_date=datetime.now().strftime("%Y-%m-%d"),
        )
        for record in book_records
    ]
    db.session.query(ReportingCube).filter(ReportingCube.book_id == book_id).filter(
        ReportingCube.is_historical_data == False
    ).update(
        {
            ReportingCube.is_available: is_available,
            ReportingCube.start_date: datetime.now().strftime("%Y-%m-%d"),
            ReportingCube.end_date: "01-01-2050",
        }
    )
    db.session.commit()
    db.session.bulk_save_objects(historical_records)
    db.session.commit()
    return jsonify({"Updated": True})


@data_blueprint.route("/wishlists", methods=["GET"], endpoint="wishlists")
@authenticate.login_user
def wishlists():
    json_data = request.get_json()
    title = json_data.get("title")
    isbn = json_data.get("isbn")
    user_credentials = authenticate.get_user_credentials()
    if user_credentials["user_type"] != "user":
        return jsonify({401: "Unauthorized access."})

    if not title and not isbn:
        return f"You should send an object with title as a string and isbn as an int."

    book = (
        db.session.query(
            ReportingCube.book_id,
            ReportingCube.title,
            ReportingCube.isbn,
            ReportingCube.is_available,
        )
        .filter(ReportingCube.title == title)
        .filter(ReportingCube.isbn == isbn)
        .filter(ReportingCube.is_historical_data == False)
        .filter(ReportingCube.is_available == True)
        .group_by(
            ReportingCube.book_id,
            ReportingCube.title,
            ReportingCube.isbn,
            ReportingCube.is_available,
        )
        .all()
    )
    print(book)
    return jsonify({"hello": book})
