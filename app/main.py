from fastapi import FastAPI
from app.schemas import PredictRequest, PredictResponse
from app.model import predict_price

app = FastAPI()

@app.post("/predict", response_model=PredictResponse)
def get_prediction(req: PredictRequest):
    hours = req.hours
    if not isinstance(hours, int):
        raise ValueError(f"Expected an integer for hours, but got {type(hours)}.")

    preds = predict_price(req.hours)
    return PredictResponse(predictions=preds)

"""
Remember, it only works for hours 1 to 21. Error handling is not done.

Next, show the predictions by:
- Adding docs and try it in swagger. (handy for demo/testing)
- Frontend or visualization.
- Streamlit for visual demo.
- Dockerize for deployment with Dockerfile.

"""
