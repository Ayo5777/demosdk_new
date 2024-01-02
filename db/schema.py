from pydantic import BaseModel
from typing import Union
from pydantic import BaseModel, validator
import datetime
from sqlalchemy import  BigInteger




class User(BaseModel):
    
    username : str
    class Config:
        orm_mode = True

class Portfolio(BaseModel):
  
    ticker : str
    percentage : float
    evaluation_id : int
    user_id = int
    class Config:
        orm_mode = True

class PortfolioEvaluation(BaseModel):
    
    overall_gain_loss : float
    
    class Config:
        orm_mode = True






