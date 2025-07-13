from fastapi import FastAPI
import pickle
import numpy as np
from pydantic import BaseModel

app = FastAPI()

# Load the model and scaler
with open('fraud_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

class ClaimData(BaseModel):
    claim_amount: float
    policy_age: float
    customer_history: int

@app.post("/predict")
async def predict_fraud(claim: ClaimData):
    features = np.array([[
        claim.claim_amount,
        claim.policy_age,
        claim.customer_history
    ]])
    
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0][1]
    
    return {
        "fraud_predicted": bool(prediction),
        "fraud_probability": float(probability)
    }