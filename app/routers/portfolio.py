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





@router.post("/report")
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
  
# Provide a download link in the response
    download_link = f"/download/{output_file}"

    return {"message": "Report generated successfully",
        "computed_result": computed_result,
        "excel_file_path": output_file,
        "download_link": download_link}
    


def generate_portfolio_excel(payload, output_filepath):
    # Create an empty DataFrame to hold the investment data
    investment_data = pd.DataFrame(columns=['Ticker', 'Symbol', 'Date Purchase', 'Amount Invested', 'Sector', 'Country', 'Industry', 'Asset Class'])

    # Iterate through the payload and populate the investment data
    for ticker, info in payload.items():
        investment_data = investment_data.append({
            'Ticker': ticker,
            'Symbol': info['symbol'],
            'Date Purchase': info['date_purchase'],
            'Amount Invested': info['amount_invested'],
            'Sector': info['sector'],
            'Country': info['country'],
            'Industry': info['industry'],  # Add the industry field
            'Asset Class': info['asset_class']
        }, ignore_index=True)

    # Calculate sums and percentages for each category
    category_columns = ['Sector', 'Country', 'Industry', 'Asset Class']  # Include 'Industry'
    category_names = ['sector', 'country', 'industry', 'asset_class']  # Include 'industry'
    output_data = {}

    for category_col, category_name in zip(category_columns, category_names):
        category_sum = investment_data.groupby(category_col)['Amount Invested'].sum()
        category_data_set = pd.DataFrame(category_sum)
        category_data_set['percentage %'] = (category_data_set['Amount Invested'] / category_data_set['Amount Invested'].sum()) * 100

        output_data[category_name] = category_data_set

    # Concatenate all categories into a single data frame
    combined_data = pd.concat(output_data.values(), keys=output_data.keys(), names=['Category'])

    # Save the combined data to an Excel file
    combined_data.to_excel(output_filepath, index=True)

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
        openbb.login(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiWDI3aGQxR2l6bW9aWnBXSUZJNmRqMHZrc0dTYXhOY1R3T3Y2THpUYSIsImV4cCI6MTY5NjEwMjYzNn0.JgMrZnz7w7tHKfIO-PUMIUX-bBwKL2LD4-6t2sjYTA8')
        Tickers = [portfolio.Ticker for portfolio in portfolios.values()]
        quote = openbb.stocks.quote(Tickers)
        ticker_gain_loss_percentages = {}
        for ticker, portfolio in portfolios.items():
            purchased_price = portfolio.purchase_price
            quoted_price = quote.loc[ticker, 'price']
            percentage_difference = (((quoted_price-purchased_price)/purchased_price) * 100)
            overall_gain_loss_percentage[ticker] = percentage_difference
 # Calculate the overall gain/loss percentage
        overall_gain_loss_percentage = sum(ticker_gain_loss_percentages.values()) / len(ticker_gain_loss_percentages)
        
        # Respond with the calculated gain/loss percentages
        return {"message": "success", "ticker_gain_loss_percentages": ticker_gain_loss_percentages, "overall_gain_loss_percentage": overall_gain_loss_percentage}
        
       
        # Respond with a success message
        #return {"message": "success", "data": quote}
    except Exception as e:
        # Handle any exceptions and return an error response
        return HTTPException(status_code=500, detail=str(e))


