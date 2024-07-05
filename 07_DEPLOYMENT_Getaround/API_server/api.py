import mlflow 
import uvicorn
import json
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
print(mlflow.__version__)
from google.cloud import bigquery
client = bigquery.Client()

description = """
API description
# Just try it 
"""

tags_metadata = [
    {
        "name": "tag_1",
        "description": "description"
    },
    {
        "name": "tag_2",
        "description": "description"
    }
]

# Input data types definition goes here
class Input(BaseModel):
    input: list

# FastAPI server creation
app = FastAPI(
    title="👽 Walletscan-API",
    description=description,
    version="0.1",
    contact={
        "name": "Aon",
        "url": "http://none.com",
    },
    openapi_tags=tags_metadata
)

# MLflow tracker configuration 
mlflow.set_tracking_uri("https://mlflow-s3-5c46c0d9d46b.herokuapp.com/")

# Loading all required models 
logged_model_name_1 = 'runs:/2d469d9db04b4bb7b63c8ec9c8aae5c2/xgboost'
logged_model_name_2 = 'runs:/2d469d9db04b4bb7b63c8ec9c8aae5c2/xgboost'
print('loading models...')
loaded_model_name_1 = 'temp' # to delete later
#loaded_model_name_1 = mlflow.pyfunc.load_model(logged_model_name_1)
#loaded_model_name_2 = mlflow.pyfunc.load_model(logged_model_name_2)
print('...models loaded')

@app.get("/wallet-info/{address}", tags=["tag_1"])
async def index(address:str):
    ######################################################
    wallet_info_query = f'''
        WITH token_transfers AS (
        SELECT
            block_timestamp,
            token_address,
            from_address AS wallet_address,
            -CAST(value AS FLOAT64) AS value
        FROM
            `bigquery-public-data.crypto_ethereum.token_transfers`
        WHERE
            CAST(value AS FLOAT64) != 0
        UNION ALL
        SELECT
            block_timestamp,
            token_address,
            to_address AS wallet_address,
            CAST(value AS FLOAT64) AS value
        FROM
            `bigquery-public-data.crypto_ethereum.token_transfers`
        WHERE
            CAST(value AS FLOAT64) != 0
        ),
        daily_balances AS (
        SELECT
            DATE(block_timestamp) AS day,
            wallet_address,
            token_address,
            SUM(value) AS daily_value
        FROM
            token_transfers
        WHERE
            wallet_address = {f'"{address.lower()}"'}
        GROUP BY
            day,
            wallet_address,
            token_address
        ),
        filtered_balances AS (
        SELECT
            db.day AS timestamp,
            db.wallet_address,
            db.token_address,
            CAST(SUM(db.daily_value) OVER (PARTITION BY db.token_address ORDER BY db.day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / 1e14 AS FLOAT64) AS balance
        FROM
            daily_balances db
        LEFT JOIN
            `bigquery-public-data.crypto_ethereum.contracts` c
        ON
            db.wallet_address = c.address
        WHERE
            c.address IS NULL
        )
        SELECT
        timestamp,
        wallet_address,
        token_address,
        balance
        FROM
        filtered_balances
        ORDER BY
        timestamp DESC;
    '''

    query_job = client.query(wallet_info_query)
    iterator = query_job.result(timeout=30)
    rows = list(iterator)

    # Transform the rows into a nice pandas dataframe
    if len(rows) > 0:
        df = pd.DataFrame(data=[list(x.values()) for x in rows], columns=list(rows[0].keys()))
    else :
        df = pd.DataFrame()
    return df
    #################################################

@app.get("/top-holders/{token_address}", tags=["tag_1"])
async def index(token_address:str):
    ######################################################
    top_holders_query = f'''
        WITH token_transfers AS (
        SELECT
            block_timestamp,
            token_address,
            from_address AS wallet_address,
            -CAST(value AS FLOAT64) AS value
        FROM
            `bigquery-public-data.crypto_ethereum.token_transfers`
        WHERE
            CAST(value AS FLOAT64) != 0
        UNION ALL
        SELECT
            block_timestamp,
            token_address,
            to_address AS wallet_address,
            CAST(value AS FLOAT64) AS value
        FROM
            `bigquery-public-data.crypto_ethereum.token_transfers`
        WHERE
            CAST(value AS FLOAT64) != 0
        ),
        daily_balances AS (
        SELECT
            wallet_address,
            token_address,
            SUM(value) AS daily_value
        FROM
            token_transfers
        WHERE
            token_address = {f'"{token_address.lower()}"'}
        GROUP BY
            wallet_address,
            token_address
        ),
        filtered_balances AS (
        SELECT
            wallet_address,
            token_address,
            SUM(daily_value) OVER (PARTITION BY wallet_address, token_address ORDER BY token_address) AS balance
        FROM
            daily_balances
        )
        SELECT
        wallet_address,
        balance / 1e18
        FROM
        filtered_balances
        WHERE
        token_address = {f'"{token_address.lower()}"'}
        ORDER BY
        balance DESC
        LIMIT 200;
    '''
    query_job = client.query(top_holders_query)
    iterator = query_job.result(timeout=30)
    rows = list(iterator)

    # Transform the rows into a nice pandas dataframe
    if len(rows) > 0:
        df = pd.DataFrame(data=[list(x.values()) for x in rows], columns=list(rows[0].keys()))
    else :
        df = pd.DataFrame()
    return df

@app.get("/isContract/{address}", tags=["tag_1"])
async def index(address:str):
    ######################################################
    is_contract_query = f"""
    SELECT 'address_exists' AS status
    FROM `bigquery-public-data.crypto_ethereum.contracts`
    WHERE address = {f'"{address.lower()}"'}
    LIMIT 1
    """

    is_contract_query_job = client.query(is_contract_query)

    is_contract_iterator = is_contract_query_job.result(timeout=30)
    is_contract_rows = list(is_contract_iterator)
    is_contract_result = dict({'result' : False})
    if len(is_contract_rows) > 0:
        is_contract_result['result'] = True
    return is_contract_result
    #################################################

# API endpoint creation
@app.post("/predict", tags=["tag_1"])
async def index(input:Input):

    # Read data 
    print(input)
    columns = ['col_1', 'col_2']
    features = pd.DataFrame([input.input], columns=columns)
    print(features)

    # Run prediction
    prediction = loaded_model_name_1.predict(features)
    print('prediction',prediction)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response
    
# Command to load the server 
if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000) # Here you define your web server to run the `app` variable (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (4000)