import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

input_csv_train = sys.argv[1]

# input_csv_train = "tree_dataset_TRAIN.csv"

df_train = pd.read_csv(input_csv_train)
df_train = df_train.sample(frac=1)
y_train = df_train['node_tissue'].values

df = df_train.drop(columns=['tree_name', 'node_name', 'node_tissue'])
x_train = df.values

# Train GBM model
clf = GradientBoostingClassifier().fit(x_train, y_train)

joblib.dump(clf, 'trained_gbm_model.joblib')