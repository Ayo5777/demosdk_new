import pandas as pd
from fastapi import APIRouter
from openbb_terminal.sdk import openbb
from typing import Optional, Dict, Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import DBSessionMiddleware, db
from db.schema import  User as SchemaUser
from db.schema import  Portfolio as SchemaPortfolio
from db.schema import  PortfolioEvaluation as SchemaPortfolioEvaluation
from db.models import User as ModelUser
from db.models import Portfolio as ModelPortfolio
from db.models import PortfolioEvaluation as ModelPortfolioEvaluation
import base64

router = APIRouter(tags=["portfolio"], prefix="/portfolio")

def generate_unique_filename():
    import uuid
    unique_filename = str(uuid.uuid4()) + ".xlsx"
    return unique_filename

async def download_report(filename: str):
    file_path = filename
    return FileResponse(file_path, filename=filename)


class Inputdata(BaseModel):
    base64data : str


@router.post('/User/', response_model=SchemaUser)
async def add_user(user : SchemaUser):
    db_user = ModelUser(username=user.username)
    db.session.add(db_user)
    db.session.commit()
    
    return{"success message":"New user created",
        "db_user":db_user
        }






@router.get('/User/{user_id}' )
def get_user(user_id: int):
    db_user = db.session.query(ModelUser).filter(ModelUser.id==user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404,detail=f"User with ID {user_id} not found")
    return db_user

#@router.post('/add_portfolio/')
def add_portfolio(
        user_id: int,
        ticker_percentage_list: list[Dict],
        overall_gain_loss_percentage : float
        ):
    
    try:     
        evaluation = ModelPortfolioEvaluation(portfolio_overall_gain_loss=overall_gain_loss_percentage)
    
        db.session.add(evaluation)
        db.session.commit()
        for entry in ticker_percentage_list:
            ticker = entry["Ticker"]
            gain_loss = entry["Gain_Loss_Percentage"]

            portfolio = ModelPortfolio(
                ticker=ticker,
                percentage=gain_loss,
                user_id=user_id,
                evaluation_id=evaluation.id  # Assign the evaluation ID
            )
            db.session.add(portfolio)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

        raise e
    finally:
        db.session.close()
    return {"message":"successfully added portfolio"}

@router.get("/get_portfolio/{user_id}")
async def get_portfolio(user_id:int):
    try:
        
        eval_id_query = db.session.query(ModelPortfolio).filter(ModelPortfolio.user_id==user_id).first()
        evaluation_id = eval_id_query.evaluation_id
        query = db.session.query(ModelPortfolio).filter(ModelPortfolio.user_id==user_id, ModelPortfolio.evaluation_id == evaluation_id).all()

        
        overall_gain_loss_query = db.session.query(ModelPortfolioEvaluation).filter(ModelPortfolioEvaluation.id==evaluation_id).first()
        query_result = [{"ticker":item.ticker, "percentage":item.percentage} for item in query]
        return{"eval_query":eval_id_query, "query_result":query_result,  "ov_gain":overall_gain_loss_query}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

import base64
import pandas as pd
from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ExcelRequest(BaseModel):
    base64data: str

@app.post('/download_excel')
async def download_excel(request: ExcelRequest):
    try:
        # Decode the Base64 data from the request
        base64_data = request.base64data.encode('utf-8')
        decoded_data = base64.b64decode(base64_data)

        # Load the decoded data into a DataFrame
        excel_data = pd.read_excel(BytesIO(decoded_data))

        # Create a downloadable Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            excel_data.to_excel(writer, index=False, sheet_name='Sheet1')

        output.seek(0)

        # Prepare the response for download
        content = output.read()
        response = {
            "content": content,
            "headers": {
                "Content-Disposition": 'attachment; filename=downloaded_excel.xlsx',
                "Content-Type": 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/summary/")
def portfolio_calculation(encoded_data: Inputdata, user_id: int):
    base64data = encoded_data.base64data
    decoded_data = base64.b64decode(base64data)
    excel_data = pd.read_excel(pd.ExcelFile(decoded_data))

    output_file = generate_unique_filename()  
    tickers = excel_data['Ticker'].tolist()
    purchase_prices = excel_data['Purchase Price'].tolist()
    portfolio_data = dict(zip(tickers, purchase_prices))
    valid_tickers = [ticker for ticker in tickers if isinstance(ticker, str) and ticker.lower() != 'nan']

    # Log in and fetch quotes for valid tickers
    openbb.login(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiWDI3aGQxR2l6bW9aWnBXSUZJNmRqMHZrc0dTYXhOY1R3T3Y2THpUYSIsImV4cCI6MTY5NjEwMjYzNn0.JgMrZnz7w7tHKfIO-PUMIUX-bBwKL2LD4-6t2sjYTA8')  # Replace with your OpenBB token
    quote = openbb.stocks.quote(valid_tickers)

    # Initialize an empty dictionary to store quoted prices for tickers
    ticker_quoted_prices = {}

    ticker_gain_loss_percentages ={}
    for ticker in valid_tickers:
        try:
            purchased_price = portfolio_data[ticker]
            price_value = quote.loc['Price', ticker]
            percentage_difference = (((price_value-purchased_price)/purchased_price) * 100)
            ticker_gain_loss_percentages[ticker] = percentage_difference

        except KeyError:
            # Handle the case where the ticker is not found in the DataFrame
            ticker_quoted_prices[ticker] = None 

    overall_gain_loss_percentage = sum(ticker_gain_loss_percentages.values()) / len(ticker_gain_loss_percentages)
    ticker_percentage_list = [{"Ticker": ticker, "Gain_Loss_Percentage": gain_loss} for ticker, gain_loss in ticker_gain_loss_percentages.items()]
    print(ticker_percentage_list)
    print(overall_gain_loss_percentage)

    add_portfolio(user_id,ticker_percentage_list, overall_gain_loss_percentage)
    # Initialize an empty dictionary to store gain/loss percentages for tickers
    ticker_gain_loss_percentages = {}


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
    
    # Read the Excel file and encode it as base64
    with open(output_file, "rb") as excel_file:
        excel_data_bytes = excel_file.read()
        excel_base64 = base64.b64encode(excel_data_bytes).decode()

    computed_result = output_data

    return {
        "message": "Report generated successfully",
        "ticker_percentage_list": ticker_percentage_list,
        "overall_gain_loss_percentage": overall_gain_loss_percentage,
        "computed_result": computed_result,
        
        "encoded_excel_file": excel_base64,
    }


class PortfolioData(BaseModel):
    Ticker: str
    purchase_price: float
    amount_invested: float
    asset_class: Optional[str]
    sector: Optional[str]
    country: Optional[str]
    industry: Optional[str]


@router.post("/eval_portfolio")
async def generate_portfolio_api(user_id: int, portfolios: Dict[str, PortfolioData]):
    try:
        openbb.login(token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiSXZoN2REM25Sd1RxcG00TnVTNnZGN0s5WnVEbWtKZDA2RXY3azZsNiIsImV4cCI6MTcyOTE4MzYxMH0.F5PwTuGDonbdTkj44H50Hov6nyLOk5PEY3p07x5E8UA")

        print("login successful")
        tickers = [portfolio.Ticker for portfolio in portfolios.values()]
        quote = openbb.stocks.quote(tickers)
        ticker_gain_loss_percentages = {}
        for ticker, portfolio in portfolios.items():
            purchased_price = portfolio.purchase_price
            quoted_price = quote.iloc[1, 0] 
            percentage_difference = (((quoted_price-purchased_price)/purchased_price) * 100)
            
            ticker_gain_loss_percentages[ticker] = percentage_difference

        # Calculate the overall gain/loss percentage
        overall_gain_loss_percentage = sum(ticker_gain_loss_percentages.values()) / len(ticker_gain_loss_percentages)
        print(overall_gain_loss_percentage) 
        ticker_percentage_list = [{"Ticker": ticker, "Gain_Loss_Percentage": gain_loss} for ticker, gain_loss in ticker_gain_loss_percentages.items()]
        #ticker_percentage_json = json.dumps(ticker_percentage_list)
        debug = add_portfolio(user_id,ticker_percentage_list, overall_gain_loss_percentage)

        print(ticker_percentage_list)
        print(debug)
        print(overall_gain_loss_percentage)      
   
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


