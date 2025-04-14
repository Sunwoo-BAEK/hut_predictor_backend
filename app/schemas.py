from pydantic import BaseModel

class PredictRequest(BaseModel):
    hours: int  # e.g., 1–21

class PredictResponse(BaseModel):
    predictions: list[float]