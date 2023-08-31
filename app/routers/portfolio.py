import pandas as pd
from fastapi import APIRouter
from openbb_terminal.sdk import openbb
from typing import Optional, Dict
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse,FileResponse
import base64

router = APIRouter(tags=["portfolio"], prefix="/portfolio")

def generate_unique_filename():
    import uuid
    unique_filename = str(uuid.uuid4()) + ".xlsx"
    return unique_filename

async def download_report(filename: str):
    file_path = filename
    return FileResponse(file_path, filename=filename)





@router.post("/summary")
def portfolio_calculation(base64data: str):
    decoded_data = base64.b64decode(base64data)
    excel_data = pd.read_excel(pd.ExcelFile(decoded_data))
    #excel_data['Current Invested Amount'] = excel_data['Current Invested Amount'].str.replace('[\$,]', '', regex=True).astype(int)

    output_file = generate_unique_filename()  
    
    # Calculate sums and percentages for each category
    category_columns = ['Sector', 'Country', 'Industry', 'Asset Class']
    category_names = ['sector', 'country', 'industry', 'asset_class']
    output_data = {}
    
    for category_col, category_name in zip(category_columns, category_names):
        category_sum = excel_data.groupby(category_col)['Current Invested Amount'].sum()
        category_data_set = pd.DataFrame(category_sum)
        category_data_set['percentage %'] = (category_data_set['Current Invested Amount'] / category_data_set['Current Invested Amount'].sum()) * 100
        
        output_data[category_name] = category_data_set

    # Concatenate all categories into a single data frame
    combined_data = pd.concat(output_data.values(), keys=output_data.keys(), names=['Category'])
    
    # Save the combined data to an Excel file
    combined_data.to_excel(output_file, index=True)
    computed_result = output_data
    
    with open(output_file, "rb") as excel_file:
        excel_data_bytes = excel_file.read()
        excel_base64 = base64.b64encode(excel_data_bytes).decode()

    computed_result = output_data

    return {
        "message": "Report generated successfully",
        "computed_result": computed_result,
        "encoded_excel_file": excel_base64,
        }
    




class PortfolioData(BaseModel):
    Ticker: str
    purchase_price: float
    amount_invested: float
    asset_class_: Optional[str]
    sector: Optional[str]
    country: Optional[str]
    industry: Optional[str]
    asset_class: Optional[str]


@router.post("/get-portfolio")
async def generate_portfolio_api(portfolios: Dict[str, PortfolioData]):
    try:
        openbb.login(token='joiWDI3aGQxR2l6bW9aWnBXSUZJNmrc0Y1R3T3Y2THpUYSIsImV4cCI6MTY5NjEwMjYzNn0.JgMrZnz7w7tHKfIO-PUMIUX-bBwKL2LD4-6t2sjYTA8')
        Tickers = [portfolio.Ticker for portfolio in portfolios.values()]
        quote = openbb.stocks.quote(Tickers)
        ticker_gain_loss_percentages = {}
        for ticker, portfolio in portfolios.items():
            purchased_price = portfolio.purchase_price
            quoted_price = quote.iloc[1, 0] 
            percentage_difference = (((quoted_price-purchased_price)/purchased_price) * 100)
            
            ticker_gain_loss_percentages[ticker] = percentage_difference
        # Calculate the overall gain/loss percentage
        overall_gain_loss_percentage = sum(ticker_gain_loss_percentages.values()) / len(ticker_gain_loss_percentages)
        ticker_percentage_list = [{"Ticker": ticker, "Gain_Loss_Percentage": gain_loss} for ticker, gain_loss in ticker_gain_loss_percentages.items()]

        # Respond with the calculated gain/loss percentages
        # Calculate category data
        category_columns = ['sector', 'country', 'industry', 'asset_class']
        category_names = ['Sector', 'Country', 'Industry', 'Asset Class']
        category_data = {}

        for category_col, category_name in zip(category_columns, category_names):
            category_sum = {}
            for portfolio in portfolios.values():
                category_value = getattr(portfolio, category_col)
                category_sum[category_value] = category_sum.get(category_value, 0) + portfolio.amount_invested
            category_data_set = pd.DataFrame({'Current Invested Amount': category_sum.values()}, index=category_sum.keys())
            category_data_set['percentage %'] = (category_data_set['Current Invested Amount'] / category_data_set['Current Invested Amount'].sum()) * 100
            category_data[category_name] = category_data_set

        computed_result = category_data






        return {
                "ticker_percentage_list": ticker_percentage_list, 
                "overall_gain_loss_percentage": overall_gain_loss_percentage,
                "computed_result": computed_result
                }
      
       
        
        #return {"message": "success", "data": quote}
    except Exception as e:
        # Handle any exceptions and return an error response
        return HTTPException(status_code=500, detail=str(e))


