import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("authors.id"))
    author = orm.relationship('Author')

    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    genre_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("books_genres.id"))
    genre = orm.relationship('BooksGenre')

    link = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    cover = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)