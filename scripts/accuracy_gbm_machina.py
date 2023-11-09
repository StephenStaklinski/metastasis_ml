import sys
import ete3
import pandas as pd

true_tree_file = sys.argv[1]
gbm_tree_file = sys.argv[2]
machina_tree_file = sys.argv[3]
outdir = sys.argv[4]

# true_tree_file = "parallel_compare_gbm_machina/sim1/all_tissue_labels.nwk"
# gbm_tree_file = "parallel_compare_gbm_machina/sim1/gbm_tree_all_tissue_labels.nwk"
# machina_tree_file = "parallel_compare_gbm_machina/sim1/machina_tree_all_tissue_labels.nwk"
# outdir = "parallel_compare_gbm_machina/sim1"

outname = outdir.split("/")[-1]

true_tree = ete3.Tree(true_tree_file, format = 8)
true_tree.get_tree_root().name = '0_t1'
gbm_tree = ete3.Tree(gbm_tree_file, format = 8)
gbm_tree.get_tree_root().name = '0_t1'
machina_tree = ete3.Tree(machina_tree_file, format = 8)
machina_tree.get_tree_root().name = '0_t1'

true_nodes = [node.name for node in true_tree.traverse() if node.is_leaf() == False]
gbm_nodes = [node.name for node in gbm_tree.traverse() if node.is_leaf() == False]
machina_nodes = [node.name for node in machina_tree.traverse() if node.is_leaf() == False]

true_split = [node.split('_') for node in true_nodes]
gbm_split = [node.split('_') for node in gbm_nodes]
machina_split = [node.split('_') for node in machina_nodes]

true_df = pd.DataFrame(true_split, columns=['node', 'true'])
gbm_df = pd.DataFrame(gbm_split, columns=['node', 'gbm'])
machina_df = pd.DataFrame(machina_split, columns=['node', 'machina'])

true_df = true_df.sort_values(by='node')
gbm_df = gbm_df.sort_values(by='node')
machina_df = machina_df.sort_values(by='node')

combined_df = pd.concat([true_df.set_index('node'), gbm_df.set_index('node'), machina_df.set_index('node')], axis=1)

accuracy_gbm = (combined_df['true'] == combined_df['gbm']).mean()
accuracy_machina = (combined_df['true'] == combined_df['machina']).mean()

subset_nonprimary = combined_df[combined_df['true'] != 't1']
num_nonprimary_nodes = len(subset_nonprimary)
if num_nonprimary_nodes != 0:
    accuracy_gbm_nonprimary = (subset_nonprimary['true'] == subset_nonprimary['gbm']).mean()
    accuracy_machina_nonprimary = (subset_nonprimary['true'] == subset_nonprimary['machina']).mean()
else:
    accuracy_gbm_nonprimary = 1.0
    accuracy_gbm_nonprimary = 1.0

result = {'name' : outname, 
          'accuracy_gbm' : accuracy_gbm, 
          'accuracy_machina' : accuracy_machina,
          'num_nonprimary_nodes' : num_nonprimary_nodes,
          'accuracy_gbm_nonprimary' : accuracy_gbm_nonprimary,
          'accuracy_machina_nonprimary' : accuracy_machina_nonprimary}
result_df = pd.DataFrame([result])

result_df.to_csv(f'{outdir}/accuracy_true_gbm_machina.csv', index=False)