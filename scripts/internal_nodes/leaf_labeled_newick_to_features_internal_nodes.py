#!/usr/bin/env python3
import sys
import numpy as np
import pandas as pd
import math
import random
from ete3 import Tree

labeled_newick_path = sys.argv[1]
tissues = str(sys.argv[2]).split(",")
output_name = sys.argv[3]

# labeled_newick_path = "test_only_leaf_tissue_labels.nwk"
# tissues = str("1,2,3").split(",")
# output_name = "test_features_leaf_tree.csv"

output_file = output_name.split("/")[-1]
output_prefix = output_file.split("_")[0]

with open(labeled_newick_path, "r") as file:
    newick_string = file.read()

labeled_tree = Tree(newick_string, format=8)
labeled_tree.get_tree_root().name = '0'

features_df = pd.DataFrame(columns = ['tree_name',
                                        'node_name',
                                        'num_total_nodes',
                                        'num_total_leaves',
                                        'proportion_children_tree_t1',
                                        'proportion_children_tree_t2',
                                        'proportion_children_tree_t3',
                                        'num_leaves_below',
                                        'proportion_leaves_below',
                                        'dist_to_root',
                                        'avg_dist_to_leaves',
                                        'num_nodes_to_root',
                                        'num_nodes_below',
                                        'proportion_children_t1',
                                        'proportion_children_t2',
                                        'proportion_children_t3',
                                        ])

# make all branch lengths 1 for relative mrca dist calculations
for node in labeled_tree.traverse():
    node.dist = 1

num_total_leaves = len(labeled_tree.get_leaves())
num_total_nodes = 0
for x in labeled_tree.traverse():
    if x.is_root() or x.is_leaf():
        continue
    else:
        num_total_nodes += 1

tissue_order = np.array(tissues)     # Assumed from tissue input

# # Use to print tissue labels for string to numerical value if needed
# tissue_labels = [f'{tissue} is tissue {i+1}' for i,tissue in enumerate(tissue_order)]
# for label in tissue_labels:
#     print(label)

root = labeled_tree.get_tree_root()
leaves_below = root.get_leaves()
leaves_below_tissues = [leaf.name.split("_")[1] for leaf in leaves_below]
tissue_proportions = [len([leaf for leaf in leaves_below_tissues if leaf == tissue]) / num_total_leaves for tissue in tissue_order]
proportion_children_tree_t1 = tissue_proportions[0]
proportion_children_tree_t2 = tissue_proportions[1]
proportion_children_tree_t3 = tissue_proportions[2]


used_nodes = []

for node in labeled_tree.traverse():
    node_name = node.name
    if node.is_leaf() or node_name in used_nodes:
        pass
    else:
        leaves_below = node.get_leaves()
        num_leaves_below = len(leaves_below)
        proportion_leaves_below = num_leaves_below / num_total_leaves
        dist_to_root = node.get_distance(root)
        dist_to_leaf = np.zeros(num_leaves_below)
        for i, leaf in enumerate(node.get_leaves()):
            dist_to_leaf[i] = node.get_distance(leaf)
        avg_dist_to_leaves = dist_to_leaf.mean()
        leaves_below_tissues = [leaf.name.split("_")[1] for leaf in leaves_below]
        leaves_below_tissues_proportions = [len([leaf for leaf in leaves_below_tissues if leaf == tissue]) / num_total_leaves for tissue in tissue_order]
        proportion_children_t1 = leaves_below_tissues_proportions[0]
        proportion_children_t2 = leaves_below_tissues_proportions[1]
        proportion_children_t3 = leaves_below_tissues_proportions[2]
        num_nodes_below = 0
        for x in node.traverse():
            if x.is_root() or x.is_leaf():
                pass
            else:
                num_nodes_below += 1
        num_nodes_to_root = 0
        current_node = node
        while current_node.up:
            current_node = current_node.up
            num_nodes_to_root += 1

        data = {'tree_name' : output_prefix,
                'node_name' : node_name,
                'num_total_nodes' : num_total_nodes,
                'num_total_leaves' : num_total_leaves,
                'proportion_children_tree_t1' : proportion_children_tree_t1,
                'proportion_children_tree_t2' : proportion_children_tree_t2,
                'proportion_children_tree_t3' : proportion_children_tree_t3,
                'num_leaves_below' : num_leaves_below,
                'proportion_leaves_below' : proportion_leaves_below,
                'dist_to_root' : dist_to_root,
                'avg_dist_to_leaves' : avg_dist_to_leaves,
                'num_nodes_to_root' : num_nodes_to_root,
                'num_nodes_below' : num_nodes_below,
                'proportion_children_t1' : proportion_children_t1,
                'proportion_children_t2' : proportion_children_t2,
                'proportion_children_t3' : proportion_children_t3}
        features_df = features_df.append(data, ignore_index = True)
        
        used_nodes.append(f'{node_name}')

features_df.to_csv(f'{output_name}', index=False)

