import sqlalchemy
from .db_session import SqlAlchemyBase


class FilmsGenre(SqlAlchemyBase):
    __tablename__ = 'films_genres'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)