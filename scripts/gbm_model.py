import sys
import numpy as np
import pandas as pd
from sklearn.datasets import make_hastie_10_2
from sklearn.ensemble import GradientBoostingClassifier

# input_csv_train = sys.argv[1]
# input_csv_test = sys.argv[2]
input_csv_train = "tree_dataset_TRAIN.csv"
input_csv_test = "tree_dataset_TEST.csv"

tissue_num_dict = {'PRL': 1, 'HMR': 2, 'LGR': 3}
tissue_num_dict_rev = {value: key for key, value in tissue_num_dict.items()}

df_train = pd.read_csv(input_csv_train)
df_train = df_train.sample(frac=1)
df_train = df_train.replace(tissue_num_dict)
y_train = df_train['mrca_tissue'].values
df = df_train.drop(columns=['tree_name', 'l1_name', 'l2_name', 'mrca_name', 'mrca_tissue'])
x_train = df.values

df_test = pd.read_csv(input_csv_test)
df_test = df_test.sample(frac=1)
df_test = df_test.replace(tissue_num_dict)
# df_test = df_test[df_test['mrca_tissue'] != 1]
y_test = df_test['mrca_tissue'].values
mrca_key_test = df_test['mrca_name'].values
mrca_tis_df = df_test[['mrca_name', 'mrca_tissue']]
mrca_tis_df = mrca_tis_df.drop_duplicates(subset=['mrca_name'], keep='first')
mrca_tis_df['mrca_tissue'] = mrca_tis_df['mrca_tissue'].replace(tissue_num_dict_rev)
mrca_order = mrca_tis_df['mrca_name'].values
df = df_test.drop(columns=['tree_name', 'l1_name', 'l2_name', 'mrca_name', 'mrca_tissue'])
x_test = df.values

# Train GBM model
clf = GradientBoostingClassifier().fit(x_train, y_train)

# Test GBM model
score = clf.score(x_test, y_test)
results = clf.predict(x_test)
unique_values, counts = np.unique(results, return_counts=True)
print(score)
print(unique_values)
print(counts)

mrca_pred = pd.DataFrame({'mrca_name': mrca_key_test, 'prediction' : results})
collapsed_mrca_pred = pd.crosstab(mrca_pred['mrca_name'], mrca_pred['prediction'])
collapsed_mrca_pred = collapsed_mrca_pred.rename(columns=tissue_num_dict_rev)
collapsed_mrca_pred = collapsed_mrca_pred.reset_index()
collapsed_mrca_pred['max_prediction'] = collapsed_mrca_pred.iloc[:, 1:].idxmax(axis=1)
collapsed_mrca_pred = collapsed_mrca_pred.loc[collapsed_mrca_pred['mrca_name'].isin(mrca_order)]
mrca_tis_df['max_prediction'] = collapsed_mrca_pred['max_prediction'].values

# Compare the two columns to determine TP, FP, and FN
mrca_tis_df['correct'] = (mrca_tis_df['mrca_tissue'] == mrca_tis_df['max_prediction']).astype(int)

correct = mrca_tis_df['correct'].sum()
total = len(mrca_tis_df)
accuracy = correct / total
print(accuracy)


collapsed_mrca_pred.to_csv('mrca_pred.csv', index=False)
