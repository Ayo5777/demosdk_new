from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routers import stocks, news, forex, portfolio

import asyncio
import os
from fastapi_sqlalchemy import DBSessionMiddleware, db
from dotenv import load_dotenv

load_dotenv('.env')



app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(news.router)
app.include_router(stocks.router)
app.include_router(forex.router)
app.include_router(portfolio.router)

