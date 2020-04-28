from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    language = Column(String)
    publication_year = Column(String)
    isbn = Column(BigInteger)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name,
            self.fullname,
            self.nickname,
        )


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)


class BookAuthor(Base):
    __tablename__ = "book_authors"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    author_id = Column(Integer, ForeignKey("authors.id"))


def create_database(engine):
    Base.metadata.create_all(engine)
