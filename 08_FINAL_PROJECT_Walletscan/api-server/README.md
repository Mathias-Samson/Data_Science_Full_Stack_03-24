# Walletscan-api

## Requirements to access Big Query ethereum

1. Create a google cloud project
2. Create a `Service account` 
    - 2024/06/05 - https://console.cloud.google.com/iam-admin/serviceaccounts?hl=fr&project=walletscan-425408
3. Give the new `Service account` the following roles:
    - Big Query data reader
    - Big Query job user
4. Create an `access key`for the new `Service account``
    - The full credentials.json file is REQUIRED to authenticate using Google Cloud SDK
5. Make sure to save this file is secured places
    - DO NOT PUSH THE FILE TO GITHUB
    - Google cloud platform will revoke the key if it's detected as leaked / exposed

## Running the Wallet-API locally

1. Open your terminal
2. Make sure to be in the `/api-server` folder
3. Create an env variable named `$GOOGLE_APPLICATION_CREDENTIALS` containing the PATH to your previously created `credentials.json`file from this folder
    - This can be done by running the command: `export GOOGLE_APPLICATION_CREDENTIALS=/the/path/to/credentials.json`
    - Exemple: Make sure your terminal is still on the `/api-server` folder. Create a `/env` folder. Save your `credentials.json`file inside this new `/env`folder. Then run the command: `export GOOGLE_APPLICATION_CREDENTIALS=env/credentials.json`
4. Run the following command: `source build_and_run.sh`
    - The Docker application MUST be installed on your desktop
5. When your Docker image is BUILT and then RUN, you can find your api-server here: 0.0.0.0:4000

## Deploying the Wallet-API on Heroku

1. Open your terminal
2. Make sure to be in the `/api-server` folder
3. Run the following command: `deploy_to_heroku.sh`
    - The Docker application MUST be installed on your desktop
    - This will create the `walletscan-api` app on your Heroku
4. Add the env variable `$GOOGLE_APPLICATION_CREDENTIALS` with the value: `gcp-credentials.json` to your new Heroku `walletscan-api` app
5. Also add the env variable `$GOOGLE_JSON_CREDENTIALS` and COPY/PAST the full content of the credentials.json file required to authenticate to google cloud as value.
6. Your `walletscan-api` Heroku app will restart dans should work properly
    - check the logs on Heroku


    



    