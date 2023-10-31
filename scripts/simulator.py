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
# num_cuts = int(sys.argv[4])
# m = sys.argv[5]

num_cuts = 100
m = [(0.3)] * num_cuts

# try:
#     float(m)
#     m = [float(m)] * num_cuts
# except:
#     if len(m.split(",")) == num_cuts:
#         m = m.split(",")
#         m = [float(i) for i in m]
#     else:
#         print("Comma-separated list of mutation rates was not of len 1 or equal to len of num_cuts. Exiting!")
#         sys.exit()


if sample_num > 10000:
    print("Sample size is over 10,000 - this is too large. Exiting!")
    sys.exit()

if migration_matrix_filepath != 'NA':
    migration_matrix = pd.read_csv(migration_matrix_filepath, header=0, index_col=0).to_dict(orient='index')

# run until 10,000 leaves
bd_sim = cas.sim.BirthDeathFitnessSimulator(
        #experiment_time = 280
        birth_waiting_distribution = lambda scale: np.random.exponential(scale),
        initial_birth_scale = 0.5,
        num_extant = 10000
    )
ground_truth_tree = bd_sim.simulate_tree()
# downsample leaves
ground_truth_tree = cas.sim.UniformLeafSubsampler(number_of_leaves=sample_num).subsample_leaves(ground_truth_tree)

# To simulate barcode mutations
final_matrix = sim_chars(ground_truth_tree,m,num_cuts,sample_num)

# To reconstruct tree from simulated barcodes
reconstructed_tree = cas.data.CassiopeiaTree(character_matrix = final_matrix, missing_state_indicator = -1)
greedy_solver = cas.solver.VanillaGreedySolver()
greedy_solver.solve(reconstructed_tree)

if migration_matrix_filepath != 'NA':
    # overlay tissue labels for migration information
    tissue_labels_df, labeled_tree = assign_tissue_labels(ground_truth_tree,migration_matrix)

# Change Casseiopeia trees to ETE tree to calculate RF distance between ground truth tree and reconstructed tree
gtt_connections = ground_truth_tree.edges
gtt_ete = Tree.from_parent_child_table(gtt_connections)
rt_connections = reconstructed_tree.edges
rt_ete = Tree.from_parent_child_table(rt_connections)
rf, max_rf, common_leaves, partitions_t1, partisionss_t2, set1, set2 = gtt_ete.robinson_foulds(rt_ete)
print(1 - (rf/max_rf))

### Iterate through tree to make matrix of features and prediction is MRCA is a transition
# initialize dataframe to save training datasets
features_df = pd.DataFrame(columns = ['tree_name',
                                        'l1_name', 
                                        'l2_name', 
                                        'mrca_name',
                                        'l1_tissue',
                                        'l2_tissue',
                                        'total_nodes_leaves',
                                        'total_num_leaves', 
                                        'total_num_nodes', 
                                        'proportion_leaves_l1_tissue',
                                        'proportion_leaves_l2_tissue',
                                        'l1_sis_tissue',
                                        'l2_sis_tissue',
                                        'num_nodes_prior_l1',
                                        'num_nodes_prior_l2',
                                        'tissues_matching', 
                                        'dist_l1_l2',
                                        'mrca_proportion_children_root_tissue',
                                        'mrca_proportion_children_l1_tissue',
                                        'mrca_proportion_children_l2_tissue',
                                        'mrca_tissue'])

# make all branch lengths 1 for relative mrca dist calculations
for node in labeled_tree.traverse():
    node.dist = 1

used_pairs = []
total_nodes_leaves = 0
total_num_leaves = 0
total_num_nodes = 0
for x in labeled_tree.traverse():
    if x.is_root():
        continue
    elif x.is_leaf():
        total_num_leaves += 1
        total_nodes_leaves += 1
    else:
        total_num_nodes += 1
        total_nodes_leaves += 1

tissue_counts = tissue_labels_df[tissue_labels_df['leaves']==True]['tissue'].value_counts()
total_count = tissue_counts.sum()
tissue_proportions = {key: value / total_count for key, value in tissue_counts.items()}
root = labeled_tree.get_tree_root()
root_name, root_tissue = root.name.split("_")

for leaf1 in labeled_tree.iter_leaves():
    l1_name, l1_tissue = leaf1.name.split("_")
    proportion_leaves_l1_tissue = tissue_proportions[l1_tissue]
    l1_parent = leaf1.up
    l1_parent_children = l1_parent.children
    # l1_sis_tissue_match = False
    for child in l1_parent_children:
        child_name, child_tissue = child.name.split("_")
        if child_name == l1_name:
            continue
        else:
            l1_sis_tissue = child_tissue
        # elif child_tissue == l1_tissue:
        #     l1_sis_tissue_match = True
    num_nodes_prior_l1 = 0
    current_node = leaf1
    while current_node.up:
        current_node = current_node.up
        num_nodes_prior_l1 += 1
    for leaf2 in labeled_tree.iter_leaves():
        l2_name, l2_tissue = leaf2.name.split("_")
        if l2_name == l1_name or f'{l2_name}_{l1_name}' in used_pairs or f'{l1_name}_{l2_name}' in used_pairs:
            pass
        else:
            proportion_leaves_l2_tissue = tissue_proportions[l2_tissue]
            l2_parent = leaf2.up
            l2_parent_children = l2_parent.children
            # l2_sis_tissue_match = False
            for child in l2_parent_children:
                child_name, child_tissue = child.name.split("_")
                if child_name == l2_name:
                    continue
                else:
                    l2_sis_tissue = child_tissue
                # elif child_tissue == l2_tissue:
                #     l2_sis_tissue_match = True
            num_nodes_prior_l2 = 0
            current_node = leaf2
            while current_node.up:
                current_node = current_node.up
                num_nodes_prior_l2 += 1
            tissues_matching = l1_tissue == l2_tissue
            dist_l1_l2 = leaf1.get_distance(leaf2)
            mrca = labeled_tree.get_common_ancestor(leaf1, leaf2)
            mrca_name, mrca_tissue = mrca.name.split("_")
            if mrca.is_root() == True:
                mrca_migration_event = False
                mrca_proportion_children_root_tissue = tissue_proportions[root_tissue]
            else:
                mrca_children_leaves = [name.split("_")[1] for name in mrca.get_leaf_names()]
                total_children = len(mrca_children_leaves)
                mrca_proportion_children_root_tissue = mrca_children_leaves.count(root_tissue) / total_children
                mrca_proportion_children_l1_tissue = mrca_children_leaves.count(l1_tissue) / total_children
                mrca_proportion_children_l2_tissue = mrca_children_leaves.count(l2_tissue) / total_children
                # mrca_parent = mrca.up
                # mrca_parent_name, mrca_parent_tissue = mrca_parent.name.split("_")
                # if mrca_parent_tissue != mrca_tissue:
                #     mrca_migration_event = True
                # else:
                #     mrca_migration_event = False
                

            data = {'tree_name' : output_name,
                    'l1_name' : l1_name, 
                    'l2_name' : l2_name, 
                    'mrca_name' : mrca_name,
                    'l1_tissue' : l1_tissue,
                    'l2_tissue' : l2_tissue,
                    'total_nodes_leaves' : total_nodes_leaves,
                    'total_num_leaves' : total_num_leaves, 
                    'total_num_nodes' : total_num_nodes, 
                    'proportion_leaves_l1_tissue' : proportion_leaves_l1_tissue,
                    'proportion_leaves_l2_tissue' : proportion_leaves_l2_tissue,
                    'l1_sis_tissue' : l1_sis_tissue,
                    'l2_sis_tissue' : l2_sis_tissue,
                    'num_nodes_prior_l1' : num_nodes_prior_l1,
                    'num_nodes_prior_l2' : num_nodes_prior_l2,
                    'tissues_matching' : tissues_matching, 
                    'dist_l1_l2' : dist_l1_l2,
                    'mrca_proportion_children_root_tissue' : mrca_proportion_children_root_tissue,
                    'mrca_proportion_children_l1_tissue' : mrca_proportion_children_l1_tissue,
                    'mrca_proportion_children_l2_tissue': mrca_proportion_children_l2_tissue,
                    'mrca_tissue' : mrca_tissue}
            features_df = features_df.append(data, ignore_index = True)
            
            used_pairs.append(f'{l2_name}_{l1_name}')

features_df.to_csv(f'{output_name}.csv', index=False)

