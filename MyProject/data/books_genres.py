import sqlalchemy
from MyProject.data.db_session import SqlAlchemyBase


class BooksGenre(SqlAlchemyBase):
    __tablename__ = 'books_genres'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)