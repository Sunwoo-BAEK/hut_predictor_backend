from pydantic import BaseModel
from typing import List
from datetime import datetime

class PredictRequest(BaseModel):
    hours: int  # e.g., 1–21

class PredictionResult(BaseModel):
    DateTime: datetime
    HUT_Close: float  # float for the predicted HUT_Close value

class PredictResponse(BaseModel):
    predictions: List[PredictionResult]  # A list of PredictionResult dictionaries