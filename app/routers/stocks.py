import datetime
from fastapi import APIRouter
from openbb_terminal.sdk import openbb
from typing import Optional, Union
from app.schemas.stocks import StockAnalysis, StockInterval, StockDataResult, StockYieldResult, StockInfoResult, StockSpreadResult


router = APIRouter(tags=["stocks"], prefix="/stocks")


@router.get("/{symbol}")
def stock_info(symbol):
    openbb.login(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiWDI3aGQxR2l6bW9aWnBXSUZJNmRqMHZrc0dTYXhOY1R3T3Y2THpUYSIsImV4cCI6MTY5NjEwMjYzNn0.JgMrZnz7w7tHKfIO-PUMIUX-bBwKL2LD4-6t2sjYTA8')
    quote_data = openbb.stocks.quote(symbol)
    return quote_data.to_dict()
    
    

@router.get("/data/{symbol}", response_model=list[StockDataResult])
def stocks_data(
    symbol: str,
    start_date: Optional[Union[datetime.datetime, str, type[None]]] = None,
    interval: Optional[StockInterval] = StockInterval.ONE_DAY,
    end_date: Optional[Union[datetime.datetime, str, type[None]]] = None,
    prepost: Optional[bool] = False, 
    source: Optional[str] = "YahooFinance", 
    weekly: Optional[bool] = False,
    monthly: Optional[bool] = False, 
    verbose:Optional[bool] = True
):
    stocks = openbb.stocks.load(symbol, start_date, interval.value, end_date, prepost, source, weekly, monthly, verbose)
    stocks['time'] = stocks.index.tolist()
    stocks_todict = stocks.to_dict(orient = "records") 
    return stocks_todict


@router.get("/stockspread/", response_model=list[list[StockSpreadResult]])
def stock_spread(
    symbol: str, 
    exchange: Optional[StockAnalysis] = StockAnalysis.EXCHANGE1
    ):
    df1,df2 = openbb.stocks.tob(symbol, exchange.value)
    df1_todict = df1.to_dict(orient = "records")
    df2_todict = df2.to_dict(orient = "records")
    return df1_todict, df2_todict



@router.get("/test-stock")
def test(symbol: str):
   dataset = openbb.stocks.ins.act(symbol)
   return dataset

#openbb.stocks.load(symbol: str, start_date: Union[datetime.datetime, str, NoneType] = None, interval: int = 1440, end_date: Union[datetime.datetime, str, NoneType] = None, prepost: bool = False, source: str = "YahooFinance", weekly: bool = False, monthly: bool = False, verbose: bool = True)
  

@router.get("/yieldanalysis/", response_model=Union[str, StockYieldResult])
def stock_yield(symbol: str):
    syield = openbb.stocks.fa.divs(symbol)
    if syield.empty:
        return "No dividends found for this stock."  
    else:
        syield["Dividends"] = syield["Dividends"].astype(str)
        syield_todict = syield[["Dividends"]].to_dict()
        return syield_todict

@router.get("test")
def test():
   P = openbb.portfolio.load(
          transactions_file_path = '/Users/kopiko/Downloads/Openbb_SDK_API_bridge/openbbuserdata/portfolio/holdings/holdings_example.xlsx',
  benchmark_symbol = 'VTI',
  full_shares = False,
  risk_free_rate = 3.0
    )
   return P