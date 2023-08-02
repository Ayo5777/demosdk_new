import pandas as pd
from fastapi import APIRouter
from openbb_terminal.sdk import openbb
from typing import Optional, Dict
from app.schemas.forex import ForexInterval, ForexDataResult, ForexSpreadResult, ForexQuoteResult

router = APIRouter(tags=["forex"], prefix="/forex")


@router.get("/data")
def forex_data(
    from_symbol: str,
    to_symbol : str,
    interval: ForexInterval=ForexInterval.ONE_DAY,
    resolution: str = "1 day",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: str = "YahooFinance",
    verbose: Optional[bool] = False
):
    data = openbb.forex.load( from_symbol, to_symbol,resolution, interval.value, start_date, end_date, source, verbose)
#    data['time'] = data.index.tolist()
    data = data.reset_index()
    data_todict = data.to_dict(orient="records")
    #return data
    """
    data_results = []
    for data_dict in data_todict:
        data_results = ForexDataResult(**data_dict)
        data_results.append(data_results)
    
   
    #data = data.index.tolist()
    """
    return data_todict



@router.get("/detailedfxdata")
def detailed_fx_data(
   
):
    
    

    fwd_pairs = openbb.forex.load('jpy','usd',source='Polygon')
    
    data_todict = fwd_pairs.to_dict(orient="records")
    #return data_todict
    return fwd_pairs




@router.get("/spreadanlysis", response_model=list[ForexSpreadResult])
def forex_spread(
    to_symbol: str = "USD",
    from_symbol: str = "EUR"
):
    spread = openbb.forex.fwd(to_symbol, from_symbol)
    spread = spread.reset_index()
    spread_todict = spread.to_dict(orient="records")

    return spread_todict


@router.get("/quote")
def forex_quote(
    symbol: str, 
    source: str = "YahooFinance"
):
    quote = openbb.forex.quote(symbol, source)
    quote_todict = quote.to_dict()
    return quote_todict


@router.get("/display_EurUsd_quote")
def forex_quote(
 
   
):
    quote = openbb.forex.quote('EURUSD', source="YahooFinance")
    quote_todict = quote.to_dict()
    return quote_todict

@router.get("/display_UsdJpy_quote")
def forex_quote(
 
   
):
    quote = openbb.forex.quote('USDJPY', source="YahooFinance")
    quote_todict = quote.to_dict()
    return quote_todict

