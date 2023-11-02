import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

trained_model = sys.argv[1]
input_csv_test = sys.argv[2]
# trained_model = "trained_gbm_model.joblib"
# input_csv_test = "test_features_leaf_tree.csv"

# Train GBM model
clf = joblib.load(trained_model)

# Import test data and group by trees to quanitfy tree level accuracy of internal node labels for each tree predictions
df_test_all = pd.read_csv(input_csv_test)
ground_truth_tissues_provided = False
if 'node_tissue' in df_test_all.columns.to_list():
    ground_truth_tissues_provided = True
df_test_all = df_test_all.groupby('tree_name')

tree_accuracy = {}
tree_accuracy_dfs = {}
for tree_name, df_test in df_test_all:
    df_test = df_test.sample(frac=1)
    if ground_truth_tissues_provided == True:
        y_test = df_test['node_tissue'].values
        node_tis_df = df_test[['node_name', 'node_tissue']]
    else:
        node_tis_df = df_test[['node_name']]

    node_tis_df.reset_index(drop=True, inplace=True)
    if ground_truth_tissues_provided == True:
        df = df_test.drop(columns=['tree_name', 'node_name', 'node_tissue'])
    else:
        df = df_test.drop(columns=['tree_name', 'node_name'])

    x_test = df.values

    # Test GBM model
    # score = clf.score(x_test, y_test)
    results = clf.predict(x_test)
    # unique_values, counts = np.unique(results, return_counts=True)

    node_tis_df['prediction'] = results

    if ground_truth_tissues_provided == True:
        node_tis_df['correct'] = (node_tis_df['node_tissue'] == node_tis_df['prediction']).astype(int)
        accuracy = node_tis_df['correct'].sum() / len(node_tis_df)
        tree_accuracy[tree_name] = accuracy
    tree_accuracy_dfs[tree_name] = node_tis_df

if ground_truth_tissues_provided == True:
    accuracy_df = pd.DataFrame(list(tree_accuracy.items()), columns=['tree_name', 'internal_node_accuracy'])
    print(accuracy_df)
    print(accuracy_df['internal_node_accuracy'].mean())
    accuracy_df.to_csv('gbm_accuracy_test_data.csv', index = False)

combined_df = pd.concat(tree_accuracy_dfs.values(), axis=0, keys=tree_accuracy_dfs.keys())
combined_df.to_csv('gbm_raw_test_data.csv')