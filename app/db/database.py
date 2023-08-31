from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from db_config import Base




class User(Base):

    __tablename__ = "user"

    userid = Column(primary_key=True)


class Portfolio(Base):
    __tablename__ = "portfolio"

    stocks = Column()
    