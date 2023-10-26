import sys
import numpy
import pandas as pd
from sklearn.datasets import make_hastie_10_2
from sklearn.ensemble import GradientBoostingClassifier

# input_csv_train = sys.argv[1]
# input_csv_test = sys.argv[2]
input_csv_train = "tree_dataset_TRAIN.csv"
input_csv_test = "tree_dataset_TEST.csv"

df_train = pd.read_csv(input_csv_train)
df_train = df_train.replace({True: 1, False: -1})
y_train = df_train['mrca_migration_event'].values
df = df_train.drop(columns='mrca_migration_event')
x_train = df.values

df_test = pd.read_csv(input_csv_test)
df_test = df_test.replace({True: 1, False: -1})
y_test = df_test['mrca_migration_event'].values
df = df_test.drop(columns='mrca_migration_event')
x_test = df.values

# x, y = make_hastie_10_2(random_state=0)
# test_cutoff = int(len(x) * 0.8)

# x_train, x_test = x[:test_cutoff], x[test_cutoff:]
# y_train, y_test = y[:test_cutoff], y[test_cutoff:]

clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0,
    max_depth=1, random_state=0).fit(x_train, y_train)
clf.score(x_test, y_test)