import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

input_csv_train = sys.argv[1]
input_csv_test = sys.argv[2]
# input_csv_train = "tree_dataset_TRAIN.csv"
# input_csv_test = "tree_dataset_TEST.csv"

tissue_num_dict = {'PRL': 1, 'HMR': 2, 'LGR': 3}    ### need to make this automated in final version to account for migration matrix input with different tissues
tissue_num_dict_rev = {value: key for key, value in tissue_num_dict.items()}

df_train = pd.read_csv(input_csv_train)
df_train = df_train.sample(frac=1)
df_train = df_train.replace(tissue_num_dict)
y_train = df_train['mrca_tissue'].values
df = df_train.drop(columns=['tree_name', 'l1_name', 'l2_name', 'mrca_name', 'mrca_tissue'])
x_train = df.values

# Train GBM model
clf = GradientBoostingClassifier().fit(x_train, y_train)

# Import test data and group by trees to quanitfy tree level accuracy of internal node labels for each tree predictions
df_test_all = pd.read_csv(input_csv_test)
df_test_all = df_test_all.groupby('tree_name')
tree_accuracy = {}
for tree_name, df_test in df_test_all:
    name = tree_name
    df_test = df_test.sample(frac=1)
    df_test = df_test.replace(tissue_num_dict)
    # df_test = df_test[df_test['mrca_tissue'] != 1]
    y_test = df_test['mrca_tissue'].values


    mrca_key_test = df_test['mrca_name'].values
    mrca_tis_df = df_test[['mrca_name', 'mrca_tissue']]
    mrca_tis_df = mrca_tis_df.drop_duplicates(subset=['mrca_name'], keep='first')
    mrca_tis_df['mrca_tissue'] = mrca_tis_df['mrca_tissue'].replace(tissue_num_dict_rev)
    df = df_test.drop(columns=['tree_name', 'l1_name', 'l2_name', 'mrca_name', 'mrca_tissue'])
    x_test = df.values

    # Test GBM model
    # score = clf.score(x_test, y_test)
    results = clf.predict(x_test)
    # unique_values, counts = np.unique(results, return_counts=True)

    mrca_pred = pd.DataFrame({'mrca_name': mrca_key_test, 'prediction' : results})
    collapsed_mrca_pred = pd.crosstab(mrca_pred['mrca_name'], mrca_pred['prediction'])
    collapsed_mrca_pred = collapsed_mrca_pred.rename(columns=tissue_num_dict_rev)
    collapsed_mrca_pred = collapsed_mrca_pred.reset_index()
    collapsed_mrca_pred['max_prediction'] = collapsed_mrca_pred.iloc[:, 1:].idxmax(axis=1)
    collapsed_mrca_pred = collapsed_mrca_pred.sort_values(by='mrca_name', ascending=True)
    mrca_tis_df = mrca_tis_df.sort_values(by='mrca_name', ascending=True)
    mrca_tis_df['max_prediction'] = collapsed_mrca_pred['max_prediction'].values

    mrca_tis_df['correct'] = (mrca_tis_df['mrca_tissue'] == mrca_tis_df['max_prediction']).astype(int)

    accuracy = mrca_tis_df['correct'].sum() / len(mrca_tis_df)
    tree_accuracy[name] = accuracy

accuracy_df = pd.DataFrame(list(tree_accuracy.items()), columns=['tree_name', 'internal_node_accuracy'])
print(accuracy_df)
print(accuracy_df['internal_node_accuracy'].mean())