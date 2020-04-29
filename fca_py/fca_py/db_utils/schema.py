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
    full_name = db.Column(db.String)


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
    df_authors = pd.DataFrame(columns=["author", "id"])
    for idx, row in df.iterrows():
        authors = [re.sub(" +", " ", name).strip() for name in row.authors.split(",")]
        book_ids = [row.id] * len(authors)
        df_authors_staging = pd.DataFrame(
            list(zip(authors, book_ids)), columns=["author", "id"]
        )
        df_authors = df_authors.append(df_authors_staging, ignore_index=True)

    print(df_authors)
    print("asdf")
    print(df_authors.loc[df_authors["id"] == 157993])
    print(df_authors["author"].to_dict())
    records = df_authors.to_dict(orient="records")
    db.session.bulk_insert_mappings(Author, records)
