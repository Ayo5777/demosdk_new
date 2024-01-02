from sqlalchemy import Boolean, Column, ForeignKey, Integer,Float, String ,DateTime,BigInteger
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
    purchase_price = Column(Float)
    user_id = Column(ForeignKey('user.id'))
    user = relationship('User')
    evaluation_id = Column(ForeignKey('portfolio_evaluation.id'))
    evaluation= relationship('PortfolioEvaluation')





class PortfolioEvaluation(Base):
    __tablename__ = "portfolio_evaluation"
    id = Column( Integer, primary_key=True,)
    portfolio_overall_gain_loss = Column(Float)




class LocalMarketData(Base):
    __tablename__ = "local_market_data"
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    csi = Column(String)
    currency = Column(String)
    last_price = Column(Float)
    last_traded_time = Column(DateTime)
    ask = Column(Float, nullable=True)
    Bid = Column(Float,  nullable=True)
    ask_size = Column(Float, nullable=True)
    Bid_size = Column(Float,  nullable=True)
    prev_close = Column(Float)
    prev_close_time = Column(DateTime)
    change = Column(Float)
    per_change = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    eps = Column(Float)
    p_e = Column(Float)
    volume = Column(BigInteger)
    yearly_high = Column(Float)
    yearly_low = Column(Float)
    market_cap = Column(BigInteger)
    name = Column(String)
    traded_date = Column(DateTime)
    asset_class = Column(String)


"""
    "Symbol": "IKEJAHOTEL",
    "CSI": "IKEJAHOTEL",
    "Currency": "NGN",
    "Last": 5,
    "LastTradeTime": "2023-12-27T14:30:00.003",
    "Ask": 5,
    "Bid": 4.55,
    "AskSize": null,
    "BidSize": null,
    "PrevClose": 4.9,
    "PrevCloseDate": "2023-12-27T00:00:00",
    "Change": 0.1,
    "PerChange": 2.04,
    "Open": 4.9,
    "High": 5,
    "Low": 5,
    "Close": 5,
    "EPS": 0.1552,
    "PE": 31.572164948453608,
    "Volume": 879407,
    "High52Week": 5,
    "Low52Week": 0.74,
    "MktCap": 13858642660,
    "Name": "IKEJA HOTEL PLC",
    "TradeDate": "2023-12-27T00:00:00",
    "Asset": "EQUITY"
"""    