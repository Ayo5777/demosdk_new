from fastApi import APIRouter




router = APIRouter(tags=["home"])


@router.get('/')
def home():
    return{"message": "FastAPI Server is up"}