# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import db.Column, Integer, String, BigInteger, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import re

db = SQLAlchemy()
# Base = declarative_base()


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    language = db.Column(db.String)
    publication_year = db.Column(db.String)
    isbn = db.Column(db.BigInteger)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name,
            self.fullname,
            self.nickname,
        )


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String)


class BookAuthor(db.Model):
    __tablename__ = "book_authors"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))


def initialize_db(db, data_path):
    df = pd.read_csv(data_path)
    df = df.rename(
        columns={
            "ISBN": "isbn",
            "Title": "title",
            "Publication Year": "publication_year",
            "Language": "language",
            "Authors": "authors",
            "Id": "id",
        }
    )
    df_books = df[["id", "title", "language", "publication_year", "isbn"]]
    df_books[["title", "language", "publication_year", "isbn"]].to_sql(
        name="books", con=db.engine, if_exists="replace", index=False
    )
    df_authors_books = pd.DataFrame(columns=["author", "id"])
    for idx, row in df.iterrows():
        authors = [re.sub(" +", " ", name).strip() for name in row.authors.split(",")]
        book_ids = [row.id] * len(authors)
        df_authors_staging = pd.DataFrame(
            list(zip(authors, book_ids)), columns=["author", "id"]
        )
        df_authors_books = df_authors_books.append(
            df_authors_staging, ignore_index=True
        )
    authors = list(set(df_authors_books["author"].values))
    authors_objects = [Author(author=author) for author in authors]
    db.session.query(Author).delete()
    db.session.bulk_save_objects(authors_objects)
    db.session.commit()

    # records = df_authors.to_dict(orient="records")
    # db.session.bulk_insert_mappings(Author, records)
    # df_authors.to_sql(
    #     name="authors", con=db.engine, if_exists="append", index=False,
    # )
