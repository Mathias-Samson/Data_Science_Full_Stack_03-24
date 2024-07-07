FROM continuumio/miniconda3

WORKDIR /home/app

# Install necessary packages
RUN apt-get update && apt-get install -y nano unzip curl

# Copy and install Python dependencies
COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

# Copy the entire directory to Docker image
COPY . /home/app

# Set environment variables for MLflow
ENV MLFLOW_HOME /opt/mlflow
ENV MLFLOW_SERVER_DEFAULT_ARTIFACT_ROOT /mlflow/mlflow-artifacts
ENV MLFLOW_SERVER_HOST 0.0.0.0
ENV MLFLOW_SERVER_PORT 4000

# Expose MLflow UI port
EXPOSE 4000

# Start MLflow server
CMD mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root /mlflow/mlflow-artifacts --host 0.0.0.0 --port 4000
