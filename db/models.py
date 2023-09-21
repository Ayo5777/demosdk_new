from sqlalchemy import Boolean, Column, ForeignKey, Integer,Float, String 
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()




class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)


class Portfolio(Base):
    __tablename__ = "portfolio"
    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    percentage = Column(Float)
    user_id = Column(ForeignKey('user.id'))
    user = relationship('User')
    evaluation_id = Column(ForeignKey('portfolio_evaluation.id'))
    evaluation= relationship('PortfolioEvaluation')





class PortfolioEvaluation(Base):
    __tablename__ = "portfolio_evaluation"
    id = Column( Integer, primary_key=True,)
    portfolio_overall_gain_loss = Column(Float)


    