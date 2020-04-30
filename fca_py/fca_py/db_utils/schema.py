# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import db.Column, Integer, String, BigInteger, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import re
from datetime import datetime

db = SQLAlchemy()
# Base = declarative_base()


class ReportingCube(db.Model):
    __tablename__ = "reporting_cube"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    title = db.Column(db.String, db.ForeignKey("books.title"))
    author = db.Column(db.String, db.ForeignKey("authors.author"))
    language = db.Column(db.String)
    publication_year = db.Column(db.String)
    isbn = db.Column(db.BigInteger)
    ext_id = db.Column(db.BigInteger)
    is_available = db.Column(db.Boolean, default=True)
    is_historical_data = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.String, default=datetime.now().strftime("%Y-%m-%d"))
    end_date = db.Column(db.String, default="01-01-2050")


class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    language = db.Column(db.String)
    publication_year = db.Column(db.String)
    isbn = db.Column(db.BigInteger)
    ext_id = db.Column(db.BigInteger)
    author = db.Column(db.String)


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    language = db.Column(db.String)
    publication_year = db.Column(db.String)
    isbn = db.Column(db.BigInteger)
    ext_id = db.Column(db.BigInteger)


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String)


class BookAuthor(db.Model):
    __tablename__ = "book_authors"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    title = db.Column(db.String, db.ForeignKey("books.title"))
    author = db.Column(db.String, db.ForeignKey("authors.author"))


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    user_type = db.Column(db.String)
    db.CheckConstraint("user_type in ('staff', 'user')", name="user_type_values")


class UserWishlist(db.Model):
    __tablename__ = "user_wishlist"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    book_id = db.Column(db.Integer, db.ForeignKey("reporting_cube.book_id"))
    isbn = db.Column(db.Integer, db.ForeignKey("reporting_cube.isbn"))
    title = db.Column(db.String, db.ForeignKey("reporting_cube.title"))
    # is_available = db.Column(db.Boolean, db.ForeignKey("reporting_cube.is_available"))
    # is_historical_data = db.Column(
    #     db.Boolean, db.ForeignKey("reporting_cube.is_historical_data")
    # )
    # we need the constraint below because in the reporting cube we got the is_available
    # field and because we have the historical data in there, so we want the most
    # updated record from the cube
    # __table_args__ = (
    #     db.ForeignKeyConstraint(
    #         [book_id, title, is_available, is_historical_data],
    #         [
    #             ReportingCube.id,
    #             ReportingCube.title,
    #             ReportingCube.is_available,
    #             ReportingCube.is_historical_data,
    #         ],
    #     ),
    #     {},
    # )


def initialize_db(db, data_path):
    df = pd.read_csv(data_path)
    df = df.rename(
        columns={
            "ISBN": "isbn",
            "Title": "title",
            "Publication Year": "publication_year",
            "Language": "language",
            "Authors": "authors",
            "Id": "ext_id",
        }
    )
    df_books = df[["ext_id", "title", "language", "publication_year", "isbn"]]
    books_records = df_books.to_dict(orient="records")
    db.session.query(Book).delete()
    db.session.bulk_insert_mappings(Book, books_records)
    db.session.commit()
    # asdf =
    df_authors_books = pd.DataFrame(columns=["author", "ext_id"])
    for idx, row in df.iterrows():
        authors = [re.sub(" +", " ", name).strip() for name in row.authors.split(",")]
        book_ids = [row.ext_id] * len(authors)
        df_authors_staging = pd.DataFrame(
            list(zip(authors, book_ids)), columns=["author", "ext_id"]
        )
        df_authors_books = df_authors_books.append(
            df_authors_staging, ignore_index=True
        )
    df_authors_books = df_authors_books.merge(df_books, on=("ext_id"))
    data_records = df_authors_books.to_dict(orient="records")

    db.session.query(Data).delete()
    db.session.bulk_insert_mappings(Data, data_records)
    db.session.commit()

    authors = list(set(df_authors_books["author"].values))
    authors_objects = [Author(author=authors[idx]) for idx in range(len(authors))]
    db.session.query(Author).delete()
    db.session.bulk_save_objects(authors_objects)
    db.session.commit()
    book_author_records = (
        db.session.query(Author.id, Book.id, Author.author, Book.title, Data)
        .filter(Data.author == Author.author)
        .filter(Data.isbn == Book.isbn)
        .all()
    )
    book_author_records = [
        {
            "author_id": book_author_records[idx][0],
            "book_id": book_author_records[idx][1],
            "author": book_author_records[idx][2],
            "title": book_author_records[idx][3],
            "id": idx,
        }
        for idx in range(len(book_author_records))
    ]
    db.session.query(BookAuthor).delete()
    db.session.bulk_insert_mappings(BookAuthor, book_author_records)
    db.session.commit()

    reporting_cube_records = (
        db.session.query(
            Book.id,
            Author.id,
            Book.title,
            Author.author,
            Book.language,
            Book.publication_year,
            Book.isbn,
            Book.ext_id,
            Data,
        )
        .filter(Data.author == Author.author)
        .filter(Data.isbn == Book.isbn)
        .all()
    )
    reporting_cube_records = [
        {
            "book_id": reporting_cube_records[idx][0],
            "author_id": reporting_cube_records[idx][1],
            "title": reporting_cube_records[idx][2],
            "author": reporting_cube_records[idx][3],
            "language": reporting_cube_records[idx][4],
            "publication_year": reporting_cube_records[idx][5],
            "isbn": reporting_cube_records[idx][6],
            "ext_id": reporting_cube_records[idx][7],
            "id": idx,
        }
        for idx in range(len(reporting_cube_records))
    ]
    db.session.query(ReportingCube).delete()
    db.session.bulk_insert_mappings(ReportingCube, reporting_cube_records)
    db.session.commit()

    # Now let's add some users
    db.session.query(User).delete()
    db.session.add(
        User(first_name="user_1_fn", last_name="user_1_ln", user_type="user")
    )
    db.session.add(
        User(first_name="user_2_fn", last_name="user_2_ln", user_type="user")
    )
    db.session.add(
        User(first_name="user_3_fn", last_name="user_3_ln", user_type="user")
    )
    db.session.add(
        User(first_name="staff_1_fn", last_name="staff_1_ln", user_type="staff")
    )
    db.session.add(
        User(first_name="staff_2_fn", last_name="staff_2_ln", user_type="staff")
    )
    db.session.commit()
