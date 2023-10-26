import sys
import numpy as np
import pandas as pd
from sklearn.datasets import make_hastie_10_2
from sklearn.ensemble import GradientBoostingClassifier

# input_csv_train = sys.argv[1]
# input_csv_test = sys.argv[2]
input_csv_train = "tree_dataset_TRAIN.csv"
input_csv_test = "tree_dataset_TEST.csv"

df_train = pd.read_csv(input_csv_train)
df_train = df_train.sample(frac=1)
df_train = df_train.replace({'PRL': 1, 'HMR': 2, 'LGR': 3})
y_train = df_train['mrca_tissue'].values
df = df_train.drop(columns='mrca_tissue')
x_train = df.values

df_test = pd.read_csv(input_csv_test)
df_test = df_test.sample(frac=1)
df_test = df_test.replace({'PRL': 1, 'HMR': 2, 'LGR': 3})
df_test = df_test[df_test['mrca_tissue'] != 1]
y_test = df_test['mrca_tissue'].values
df = df_test.drop(columns='mrca_tissue')
x_test = df.values

# test_cutoff = int(len(x) * 0.8)

# x_train, x_test = x[:test_cutoff], x[test_cutoff:]
# y_train, y_test = y[:test_cutoff], y[test_cutoff:]

clf = GradientBoostingClassifier().fit(x_train, y_train)
score = clf.score(x_test, y_test)
print(score)
results = clf.predict(x_test)
unique_values, counts = np.unique(results, return_counts=True)