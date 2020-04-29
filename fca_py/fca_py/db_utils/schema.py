# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import db.Column, Integer, String, BigInteger, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import re

db = SQLAlchemy()
# Base = declarative_base()


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

    # def __repr__(self):
    #     return "<User(name='%s', fullname='%s', nickname='%s')>" % (
    #         self.name,
    #         self.fullname,
    #         self.nickname,
    #     )


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String)


class BookAuthor(db.Model):
    __tablename__ = "book_authors"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    # __table_args__ = (
    #     db.PrimaryKeyConstraint("book_id", "author_id"),
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
        db.session.query(Author, Book, Data)
        .filter(Data.author == Author.author)
        .filter(Data.isbn == Book.isbn)
        .all()
    )

    db.session.query(BookAuthor).delete()
    db.session.bulk_save_objects(book_author_records)
    db.session.commit()
    print("book author records: ", book_author_records)
    print(type(book_author_records[0][0]))
    f"""
        insert into book_authors
        select
            bk.id
            ,at.id
        from data dt
        inner join authors at
            on dt.author = at.author
        inner join books bk
            on dt.isbn = bk.isbn
    """
