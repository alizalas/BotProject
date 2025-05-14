import sqlalchemy
from MyProject.data.db_session import SqlAlchemyBase


class Film(SqlAlchemyBase):
    __tablename__ = 'films'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # director_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("directors.id"))
    # director = orm.relationship('Director')

    director = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    # genre_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("films_genres.id"))
    # genre = orm.relationship('FilmsGenre')

    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    cover = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)