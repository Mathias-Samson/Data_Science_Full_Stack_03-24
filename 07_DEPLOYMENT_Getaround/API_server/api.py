import mlflow 
import uvicorn
import json
import pandas as pd
import pickle
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile



print(mlflow.__version__)

description = """
API description 
This API will let you have an idea of the best price for your car rental based on its description
"""

tags_metadata = [
    {
        "name": "tag_1",
        "description": "description"
    },
]

class Input(BaseModel):
    input: list

app = FastAPI(
    title="🚗 Getaround price rental prediction Api",
    description=description,
    version="0.1",
    openapi_tags=tags_metadata
)

with open('/home/app/model.pkl', 'rb') as f:
  loaded_model = pickle.load(f)
print('...model loaded')


@app.post("/predict", tags=["tag_1"])
async def index(input:Input):
    print(input)
    # Read data 
    columns = ['model_key', 'mileage', 'engine_power', 'fuel', 'paint_color',
       'car_type', 'private_parking_available', 'has_gps',
       'has_air_conditioning', 'automatic_car', 'has_getaround_connect',
       'has_speed_regulator', 'winter_tires']
    features = pd.DataFrame([input.input], columns=columns)
    features['private_parking_available'].astype(bool)
    features['has_gps'].astype(bool)
    features['has_air_conditioning'].astype(bool)
    features['automatic_car'].astype(bool)
    features['has_getaround_connect'].astype(bool)
    features['has_speed_regulator'].astype(bool)
    features['winter_tires'].astype(bool)
    print('features_type',type(features))
    print(features)

    # Run prediction
    prediction = loaded_model.predict(features)
    print('prediction',prediction)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response

    

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000) # Here you define your web server to run the `app` variable (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (4000)