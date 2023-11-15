import sys
import ete3
import pandas as pd
from collections import Counter
import random

leaf_labeled_tree = sys.argv[1]
output_dir = sys.argv[2]

# leaf_labeled_tree = "test/only_leaf_tissue_labels.nwk"
# output_dir = "test"

tree = ete3.Tree(leaf_labeled_tree, format=8)
tree.get_tree_root().name = '0'

for node in tree.traverse():
    if node.is_leaf():
        pass
    else:
        node_name = node.name
        children = [leaf.name.split("_")[1] for leaf in node.get_leaves()]
        counts = Counter(children)
        most_common_elements = counts.most_common(2)
        if len(most_common_elements) > 1 and most_common_elements[0][1] == most_common_elements[1][1]:
            t1_in_common_elements = any('t1' in elem for elem in most_common_elements)
            if t1_in_common_elements:
                consensus_tissue = 't1'
            else:
                tied_elements = [elem[0] for elem in most_common_elements]
                consensus_tissue = random.choice(tied_elements)
        else:
            consensus_tissue = most_common_elements[0][0]
        new_node_name = f"{node_name}_{consensus_tissue}"
        node.name = new_node_name

tree.write(format=8, outfile = f'{output_dir}/consensus_tissue_tree_all_tissue_labels.nwk')
        
