import ete3
import pandas as pd
import sys

leaf_tree = sys.argv[1]
gbm_labels = sys.argv[2]
outdir = sys.argv[3]

# leaf_tree = "test_only_leaf_tissue_labels.nwk"
# gbm_labels = "gbm_raw_test_data.csv"

tree = ete3.Tree(leaf_tree, format=8)
tree.get_tree_root().name = '0'
gbm_df = pd.read_csv(gbm_labels)
gbm_df.drop(columns = ['Unnamed: 0', 'Unnamed: 1'], inplace = True)
gbm_df.set_index('node_name', inplace = True)

for node in tree.traverse():
    if node.is_leaf() == False:
        node_name = int(node.name)
        tissue = gbm_df.loc[node_name, 'prediction']
        new_name = str(node_name) + "_t" + str(tissue)
        node.name = new_name

tree.write(format=8, outfile = f'{outdir}/gbm_tree_all_tissue_labels.nwk')