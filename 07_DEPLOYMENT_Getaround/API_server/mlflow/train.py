import pandas as pd
import time
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor, AdaBoostRegressor, VotingRegressor, StackingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, f1_score, r2_score

# Point to the MLflow server running at localhost:4000
mlflow.set_tracking_uri("http://localhost:4000")

# Set your variables for your environment
EXPERIMENT_NAME = "getaround_model_test_1"
mlflow.set_experiment(EXPERIMENT_NAME)
experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
if experiment:
    print("Experiment ID:", experiment.experiment_id)
    print("Artifact Location:", experiment.artifact_location)
else:
    print(f"Experiment '{EXPERIMENT_NAME}' does not exist.")

# Start experiment time tracking
start_time = time.time()
mlflow.sklearn.autolog(log_models=True)

# Load dataset
data_price = pd.read_csv(r"/home/app/get_around_pricing_project.csv")
data_price = data_price.drop(columns="Unnamed: 0")

# Preprocessing
target_variable = "rental_price_per_day"
X = data_price.drop(target_variable, axis=1)
Y = data_price.loc[:, target_variable]
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

numeric_features = list(X.select_dtypes(include=['float', 'int']).columns)
categorical_features = list(X.select_dtypes(exclude=['float', 'int']).columns)

# Check
print("Found numeric features ", numeric_features)
print("Found categorical features ", categorical_features)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features),
    ]
)
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", GradientBoostingRegressor())
])
print("preprocess OK")

# Start training
with mlflow.start_run(experiment_id=experiment.experiment_id):
    model.fit(X_train, Y_train)
    print("model trained")
    X_train_pred = model.predict(X_train)
    mlflow.sklearn.log_model(model, "GradientBoostingRegressor")

print('train_score', model.score(X_train, Y_train))
print('test_score', model.score(X_test, Y_test))

mlflow.end_run()
