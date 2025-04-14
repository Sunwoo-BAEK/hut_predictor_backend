from fastapi import FastAPI
from app.schemas import PredictRequest, PredictResponse
from app.model import predict_stock

app = FastAPI()

@app.post("/predict", response_model=PredictResponse)
def get_prediction(req: PredictRequest):
    return predict_stock(req)