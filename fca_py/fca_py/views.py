from flask import Blueprint, jsonify, request, current_app
from .db_utils.schema import *
from datetime import datetime
from .authenticator import Authenticator
import pandas as pd
from .openlibrary_api_handler import ApiClient

data_blueprint = Blueprint("data", __name__)
authenticate = Authenticator()


@data_blueprint.route("/books", methods=["GET"], endpoint="books")
@authenticate.login_user
def books():
    json_data = request.get_json()
    author = json_data.get("author")
    title = json_data.get("title")
    user_credentials = authenticate.get_user_credentials()
    if user_credentials["user_type"] != "user":
        return jsonify(
            {"error": "Unauthorized access. This endpoint is just for users."}
        )
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
    action = json_data.get("action")
    user_credentials = authenticate.get_user_credentials()
    if user_credentials["user_type"] != "user":
        return jsonify(
            {401: "Unauthorized access. This is an endpoint just for users."}
        )

    if not title and not isbn:
        return f"You should send an object with action <Add|Remove>, title as a string and isbn as an int."

    if action == "Remove":
        db.session.query(UserWishlist).filter(
            UserWishlist.user_id == user_credentials["user_id"]
        ).filter(UserWishlist.title == title).filter(UserWishlist.isbn == isbn).delete()
        return jsonify({"Removed": True})
    elif action == "Add":
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
            .filter(ReportingCube.is_available == False)
            .group_by(
                ReportingCube.book_id,
                ReportingCube.title,
                ReportingCube.isbn,
                ReportingCube.is_available,
            )
            .all()
        )
        if len(book) == 1 and len(book[0]) == 4:
            db.session.add(
                UserWishlist(
                    user_id=user_credentials["user_id"],
                    first_name=user_credentials["first_name"],
                    last_name=user_credentials["last_name"],
                    book_id=book[0][0],
                    title=book[0][1],
                    isbn=book[0][2],
                )
            )
            db.session.commit()
        else:
            return jsonify(
                {
                    "Resource not found": "Book not found in the library or is already available."
                }
            )
        return jsonify({"Book added to wishlist": True})
    else:
        return jsonify({"Bad Request": "Action must be either Add or Remove."})


@data_blueprint.route("/report", methods=["GET"], endpoint="report")
@authenticate.login_user
def report():
    user_credentials = authenticate.get_user_credentials()
    if user_credentials["user_type"] != "staff":
        return jsonify(
            {401: "Unauthorized access. This is an endpoint just for users."}
        )

    report_data = pd.read_sql(
        f""" 
        select
            book_id
            ,title
            ,isbn
            ,start_date
            ,is_available
        from reporting_cube
        where is_historical_data = 0
            and is_available = 0
        group by 1,2,3,4
        """,
        db.engine,
    )
    if len(report_data) > 0:
        report_data["days_rented"] = (
            datetime.now()
            - datetime.strptime(report_data["start_date"].values[0], "%Y-%m-%d")
        ).days
        response = jsonify({"Report generated.": True})
    else:
        response = jsonify(
            {"Report generated. However, all books are available.": True}
        )
    report_data.to_json(current_app.config["REPORTS_DIR_PATH"])
    print("Path of the report is: ", current_app.config["REPORTS_DIR_PATH"])
    return response


@data_blueprint.route("/amazon_ids", methods=["PUT"], endpoint="amazon_ids")
@authenticate.login_user
def amazon_ids():
    json_data = request.get_json()
    user_credentials = authenticate.get_user_credentials()
    if user_credentials["user_type"] != "staff":
        return jsonify({"error": "Unauthorized access."})

    book_isbn_records = db.session.query(Book.id, Book.isbn,).all()
    print(len(book_isbn_records))
    api = ApiClient()
    for record in book_isbn_records:
        amazon_id = None
        book_id = record[0]
        book_isbn = record[1]
        api_response = api.get_response(book_isbn)
        print(api_response.json())
        print(len(dict.keys(api_response.json())))
        if len(dict.keys(api_response.json())) > 0:
            amazon_id = api_response.json()[f"ISBN:{book_isbn}"]["identifiers"].get(
                "amazon"
            )
            if isinstance(amazon_id, list) and len(amazon_id) == 1:
                amazon_id = amazon_id[0]
        if amazon_id:
            print("Updating db.")
            db.session.query(Book).filter(Book.id == book_id).update(
                {Book.amazon_id: amazon_id,}
            )
            db.session.commit()
    return jsonify({"Updated": True})
