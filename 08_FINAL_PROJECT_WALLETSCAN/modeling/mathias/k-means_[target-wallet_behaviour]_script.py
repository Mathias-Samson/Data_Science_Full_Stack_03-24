# %%
import mlflow
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# %%
# mlflow server connection
mlflow.set_tracking_uri("https://mlflow-s3-5c46c0d9d46b.herokuapp.com/")
#mlflow.set_tracking_uri("../mlruns")
EXPERIMENT_NAME="Mathias_experiment"
mlflow.set_experiment(EXPERIMENT_NAME)
experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
if experiment:
    print("Experiment ID:", experiment.experiment_id)
    print("Artifact Location:", experiment.artifact_location)
else:
    print(f"Experiment '{EXPERIMENT_NAME}' does not exist.")

# start experiment time tracking
start_time = time.time()
mlflow.sklearn.autolog(log_models=False)

# %%
# df = pd.read_csv("/content/drive/MyDrive/Fichiers/2.Scolarité/1. Jedha_Data_Science/PROJETS/DEMO_DAY/Dataset_src_02/2023-01-15___2023_02-01.csv")
df = pd.read_csv(r"G:\Mon Drive\Fichiers\2.Scolarité\1. Jedha_Data_Science\PROJETS\DEMO_DAY\Dataset_src_02\2023-01-15___2023_02-01.csv")

# %%
dataset = df.copy()

# %%
# dataset = dataset.sample(n=500000)

# %% [markdown]
# ### Total_transaction

# %%
total_transaction_df = dataset.groupby('wallet_address').size().to_frame(name='total_wallet_transactions')
# total_transaction_df = total_transaction_df.reset_index()

# %%
total_transaction_df['log_total_wallet_transactions'] = np.log1p(total_transaction_df['total_wallet_transactions'])

# %%
unique_tokens_by_wallet = dataset.groupby('wallet_address')['token_address'].nunique()
u_token_df = unique_tokens_by_wallet.to_frame(name='tokens_by_wallet')
# u_token_df = u_token_df.reset_index()

# %%
u_token_df['log_tokens_by_wallet'] = np.log1p(u_token_df['tokens_by_wallet'])

# %% [markdown]
# ## K-Means_Test_1

# %%
dataset_kmeans_1 = pd.concat([total_transaction_df, u_token_df], axis=1)

# %%
dataset_kmeans_1 = dataset_kmeans_1.drop(columns = ["total_wallet_transactions","tokens_by_wallet"],axis = 1)

# %%
numerical_features = dataset_kmeans_1[["log_total_wallet_transactions","log_tokens_by_wallet"]]
scaler = StandardScaler()
standardized_features = scaler.fit_transform(numerical_features)

# %%
kmeans = KMeans(n_clusters=7, random_state=0)

# %%
# train the model
with mlflow.start_run(experiment_id = experiment.experiment_id):
    kmeans.fit(dataset_kmeans_1)
    predictions = kmeans.labels_

    mlflow.sklearn.log_model(kmeans, "Kmeans_1")

print("...Done!")
print(f"---Total training time: {time.time()-start_time}")


mlflow.end_run()

# %%



