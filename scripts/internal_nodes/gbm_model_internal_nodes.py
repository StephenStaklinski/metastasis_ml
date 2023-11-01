import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

# input_csv_train = sys.argv[1]
# input_csv_test = sys.argv[2]
input_csv_train = "tree_dataset_TRAIN.csv"
input_csv_test = "tree_dataset_TEST.csv"

df_train = pd.read_csv(input_csv_train)
df_train = df_train.sample(frac=1)
y_train = df_train['node_tissue'].values

df = df_train.drop(columns=['tree_name', 'node_name', 'node_tissue'])
x_train = df.values

# Train GBM model
clf = GradientBoostingClassifier().fit(x_train, y_train)

# Import test data and group by trees to quanitfy tree level accuracy of internal node labels for each tree predictions
df_test_all = pd.read_csv(input_csv_test)
df_test_all = df_test_all.groupby('tree_name')
tree_accuracy = {}
tree_accuracy_dfs = {}
for tree_name, df_test in df_test_all:
    df_test = df_test.sample(frac=1)
    y_test = df_test['node_tissue'].values

    node_tis_df = df_test[['node_name', 'node_tissue']]
    node_tis_df.reset_index(drop=True, inplace=True)
    df = df_test.drop(columns=['tree_name', 'node_name', 'node_tissue'])
    x_test = df.values

    # Test GBM model
    # score = clf.score(x_test, y_test)
    results = clf.predict(x_test)
    # unique_values, counts = np.unique(results, return_counts=True)

    node_tis_df['prediction'] = results

    node_tis_df['correct'] = (node_tis_df['node_tissue'] == node_tis_df['prediction']).astype(int)
    accuracy = node_tis_df['correct'].sum() / len(node_tis_df)
    tree_accuracy[tree_name] = accuracy
    tree_accuracy_dfs[tree_name] = node_tis_df

accuracy_df = pd.DataFrame(list(tree_accuracy.items()), columns=['tree_name', 'internal_node_accuracy'])
combined_df = pd.concat(tree_accuracy_dfs.values(), axis=0, keys=tree_accuracy_dfs.keys())
print(accuracy_df)
print(accuracy_df['internal_node_accuracy'].mean())
accuracy_df.to_csv('accuracy_test_data.csv', index = False)
combined_df.to_csv('raw_test_data.csv')