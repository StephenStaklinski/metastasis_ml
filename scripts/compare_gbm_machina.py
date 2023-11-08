### Take in tsv output labels from gbm and machina and report performance statistics
import pandas as pd
import sys
import ete3

# true_tree = sys.argv[1]
# gbm_output = sys.argv[2]
# machina_output = sys.argv[3]

true_tree = "test_all_tissue_labels.nwk"
gbm_output = "gbm_raw_test_data.csv"
machina_output = "machina_results/T-t1-0.labeling"

gbm_df = pd.read_csv(gbm_output)
gbm_df = gbm_df[['node_name', 'prediction']]
colname_dict = {'node_name':'node', 'prediction': 'gbm'}
gbm_df.rename(colname_dict, axis = 'columns', inplace = True)
machina_df = pd.read_csv(machina_output, delim_whitespace = True, names = ['node','tissue'])
colname_dict = {'node':'node', 'tissue': 'machina'}
machina_df.rename(colname_dict, axis = 'columns', inplace = True)

internal_node_list = gbm_df['node'].to_list()
machina_df = machina_df[machina_df['node'].isin(internal_node_list)]
machina_df['machina'] = machina_df['machina'].str.replace('t', '')
merged_df = pd.merge(gbm_df, machina_df, on='node', how='inner')
merged_df['true'] = 'NA'

tree = ete3.Tree(true_tree, format = 8)
tree.get_tree_root().name = '0_t1'

for node in tree.traverse():
    if node.is_leaf() == False:
        name, tissue = node.name.split("_")
        print(name,tissue)
        merged_df.loc[merged_df['node'] == int(name), 'true'] = tissue

merged_df['true'] = merged_df['true'].str.replace('t', '')

