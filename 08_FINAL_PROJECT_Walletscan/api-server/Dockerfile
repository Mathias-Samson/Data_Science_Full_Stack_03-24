FROM continuumio/miniconda3

WORKDIR /home/app

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

RUN conda install conda-forge::google-cloud-sdk -y

RUN gcloud components update
RUN pip install --upgrade google-cloud-bigquery

COPY ./api.py /home/app

# gunicorn required for Heroku
CMD gcloud config set project ${GOOGLE_CLOUD_PROJECT}; echo ${GOOGLE_JSON_CREDENTIALS} > gcp-credentials.json; gunicorn api:app  --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker 