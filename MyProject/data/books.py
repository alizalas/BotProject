import sqlalchemy
from MyProject.data.db_session import SqlAlchemyBase


class Book(SqlAlchemyBase):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("authors.id"))
    # author = orm.relationship('Author')

    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    # genre_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("books_genres.id"))
    # genre = orm.relationship('BooksGenre')

    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    cover = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)