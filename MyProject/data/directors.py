import sqlalchemy
from .db_session import SqlAlchemyBase


class Director(SqlAlchemyBase):
    __tablename__ = 'directors'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)