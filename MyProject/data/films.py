import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Film(SqlAlchemyBase):
    __tablename__ = 'films'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    director_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("directors.id"))
    director = orm.relationship('Director')

    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    genre_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("films_genres.id"))
    genre = orm.relationship('FilmsGenre')

    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    link = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    cover = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')