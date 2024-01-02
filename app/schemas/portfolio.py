from typing import Union
from pydantic import BaseModel
import datetime
from sqlalchemy import  BigInteger


class LocalMarketData(BaseModel):
    id : int
    symbol : str
    csi : str
    currency : str
    last_price : float
    last_traded_time : datetime.datetime
    ask : float
    Bid : float
    ask_size : float
    Bid_size : float
    prev_close : float
    prev_close_time : datetime.datetime
    change : float
    per_change : float
    open : float
    high : float
    low : float
    close : float
    eps : float
    p_e : float
    volume = BigInteger
    yearly_high : float
    yearly_low : float
    market_cap : BigInteger
    name : str
    traded_date : datetime.datetime
    asset_class : str
