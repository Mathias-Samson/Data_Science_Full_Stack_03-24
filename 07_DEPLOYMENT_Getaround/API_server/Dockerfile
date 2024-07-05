FROM continuumio/miniconda3

WORKDIR /home/app

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

RUN conda install conda-forge::google-cloud-sdk -y

COPY ./home/app

CMD gunicorn api:app  --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker