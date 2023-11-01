#!/usr/bin/env python3
import sys
import numpy as np
import pandas as pd
import math
import random
from ete3 import Tree
import cassiopeia as cas
from cassiopeia.data import CassiopeiaTree

def sim_chars(tree,mut_rate,num_cuts,sample_num):
    np.random.seed(seed=None)
    lt_sim = cas.sim.Cas9LineageTracingDataSimulator(
        number_of_cassettes = num_cuts,
        size_of_cassette = 1,
        mutation_rate = mut_rate, # can also be a list of rates of equal len to num_cuts
        state_generating_distribution = lambda: np.random.exponential(1e-5),
        number_of_states = sample_num,
        state_priors = None,
        heritable_silencing_rate = 0, #heritable_silencing_rate = 9e-4,
        stochastic_silencing_rate = 0, #stochastic_silencing_rate = 0.1,
        heritable_missing_data_state = -1,
        stochastic_missing_data_state = -1,
    )
    lt_sim.overlay_data(tree)
    character_matrix = tree.character_matrix
    return character_matrix

def assign_tissue_labels(cas_tree,trans_mat):
    tree = cas_tree
    tree_labeled = tree.copy()
    tissue_array = np.array(list(trans_mat.keys()))
    tis_labels = {}
    parent_nodes = {}
    parent_tissues = {}
    migration_labels = {}
    migration_scaling_boundary = 2.5
    migration_scaling_factor = 0.1
    
    # Set the root node label to the first tissue in the list
    root = tree.root
    tis_labels[root] = tissue_array[0]
    
    # Traverse the tree and assign tissue labels to each node
    for node in tree.nodes:
        # Skip the root node since it has already been labeled
        if node == root:
            continue

        # Determine the probability of changing tissue label
        prev_tissue = tis_labels[tree.parent(node)]
        prob_vec = np.array([trans_mat[prev_tissue][t] for t in tissue_array])

        # Make tissue label decision of the current node and assign the label
        if tree.is_leaf(node) == False:
            # Scale the migration probability to be less at earlier points in the tree
            age = tree.get_time(node)
            if age < migration_scaling_boundary:
                tissue_index = np.where(tissue_array == prev_tissue)
                prob_vec = prob_vec * migration_scaling_factor
                sum_except_index = np.sum(np.delete(prob_vec, tissue_index))
                prob_vec[tissue_index] = 1 - sum_except_index
                tis_labels[node] = np.random.choice(tissue_array, p=(prob_vec))
            else:
                tis_labels[node] = np.random.choice(tissue_array, p=prob_vec)
        # Label leaves not by probability but by their parent
        if tree.is_leaf(node) == True:
            tis_labels[node] = prev_tissue
        
        parent_nodes[node] = tree.parent(node)
        parent_tissues[node] = prev_tissue
        
        if tis_labels[node] == prev_tissue:
            migration_labels[node] = False
        if tis_labels[node] != prev_tissue:
            migration_labels[node] = True
    
    # Make a concatenated key and value dictionary to relabel nodes in copied tree
    node_tis_map = {}
    for key, value in tis_labels.items():
        new_value = key + "_" + value
        node_tis_map[key] = new_value
    
    tree_labeled.relabel_nodes(node_tis_map)

    # Add tissue labels to pandas df to add column labeling leaves
    tissues_df = pd.DataFrame.from_dict(tis_labels, orient='index', columns=['tissue'])
    tissues_df.index.names = ['node']
    tissues_df.reset_index(drop=False, inplace=True)
    tissues_df['leaves'] = [tree.is_leaf(x) for x in tissues_df['node'].values]
    tissues_df['parent_node'] = tissues_df['node'].map(parent_nodes)
    tissues_df['parent_tissue'] = tissues_df['node'].map(parent_tissues)
    tissues_df['migration_event'] = tissues_df['node'].map(migration_labels)

    # Change Casseiopeia tree to ETE tree to retain internal node labels when writing newick later
    connections = tree_labeled.edges
    tree_labeled = Tree.from_parent_child_table(connections)
    
    return tissues_df, tree_labeled


## PARAMETERS ##
sample_num = int(sys.argv[1])
migration_matrix_filepath = sys.argv[2]
output_name = sys.argv[3]
# sample_num = 100
# migration_matrix_filepath = "migration_matrix/true_migration_prob_matrix.csv"
# output_name = "test"

output_prefix = output_name.split(".")[0]

# num_cuts = 100
# m = [(0.6)] * num_cuts

if migration_matrix_filepath != 'NA':
    migration_matrix = pd.read_csv(migration_matrix_filepath, header=0, index_col=0).to_dict(orient='index')

# run until 10,000 leaves
bd_sim = cas.sim.BirthDeathFitnessSimulator(
        #experiment_time = 280
        birth_waiting_distribution = lambda scale: np.random.exponential(scale),
        initial_birth_scale = 0.5,
        num_extant = sample_num)

ground_truth_tree = bd_sim.simulate_tree()

if migration_matrix_filepath != 'NA':
    # overlay tissue labels for migration information
    tissue_labels_df, labeled_tree = assign_tissue_labels(ground_truth_tree,migration_matrix)

# # To simulate barcode mutations
# final_matrix = sim_chars(ground_truth_tree,m,num_cuts,sample_num)

# # To reconstruct tree from simulated barcodes
# reconstructed_tree = cas.data.CassiopeiaTree(character_matrix = final_matrix, missing_state_indicator = -1)
# greedy_solver = cas.solver.VanillaGreedySolver()
# greedy_solver.solve(reconstructed_tree)

# # Change Casseiopeia trees to ETE tree to calculate RF distance between ground truth tree and reconstructed tree
# gtt_connections = ground_truth_tree.edges
# gtt_ete = Tree.from_parent_child_table(gtt_connections)
# rt_connections = reconstructed_tree.edges
# rt_ete = Tree.from_parent_child_table(rt_connections)
# rf, max_rf, common_leaves, partitions_t1, partisionss_t2, set1, set2 = gtt_ete.robinson_foulds(rt_ete)
# print(1 - (rf/max_rf))

### Iterate through tree to make matrix of features and prediction is MRCA is a transition
# initialize dataframe to save training datasets
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
                                        'node_tissue'
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

tissue_order = np.array(list(migration_matrix.keys()))     # Assumed from migration matrix order

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
    node_name, node_tissue = node.name.split("_")
    node_tissue_index = np.where(tissue_order == node_tissue)[0][0] + 1
    if node.is_leaf() or node_name in used_nodes:
        continue
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
                continue
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
                'proportion_children_t3' : proportion_children_t3,
                'node_tissue': node_tissue_index}
        features_df = features_df.append(data, ignore_index = True)
        
        used_nodes.append(f'{node_name}')

features_df.to_csv(f'{output_name}', index=False)

