FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update
RUN apt-get install nano libffi-dev libssl-dev


COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

# gunicorn required for Heroku
CMD python app.py