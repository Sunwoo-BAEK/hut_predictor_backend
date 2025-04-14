from pydantic import BaseModel
from typing import List
from datetime import datetime

class PredictRequest(BaseModel):
    hours: int

class PredictionResult(BaseModel):
    DateTime: datetime
    HUT_Close: float

class PredictResponse(BaseModel):
    predictions: List[PredictionResult]