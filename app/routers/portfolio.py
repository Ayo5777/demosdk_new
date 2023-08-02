import pandas as pd
from fastapi import APIRouter
from openbb_terminal.sdk import openbb
from typing import Optional, Dict


router = APIRouter(tags=["portfolio"], prefix="/portfolio")

@router.get("/portfolio")
def get_portfolio():
    return "hello"