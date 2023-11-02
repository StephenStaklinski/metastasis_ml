#!/usr/bin/env python3
import sys
import numpy as np
import pandas as pd
import math
import random
from ete3 import Tree
import cassiopeia as cas
from cassiopeia.data import CassiopeiaTree

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
    
    # convert cassiopeia tree to ete3 tree
    connections = tree_labeled.edges
    tree_labeled = Tree.from_parent_child_table(connections)

    # make seperate copies of tree to have one with labeled leaves and the other with all nodes and leaves labeled
    tree_labeled_all = tree_labeled.copy()
    tree_labeled_leaves = tree_labeled.copy()

    # Make a concatenated key and value dictionary to relabel nodes and leaves in copied tree
    node_tis_map = {}
    for key, value in tis_labels.items():
        new_value = key + "_" + value
        node_tis_map[key] = new_value
    
    for node in tree_labeled_all.traverse():
        current_name = node.name
        replacement_name = node_tis_map[current_name]
        node.name = replacement_name
    
    # Make a concatenated key and value dictionary to relabel only leaves in copied tree
    leaf_tis_map = {}
    labeled_leaves = [label.name for label in tree_labeled.get_leaves()]
    tis_labels_leaves = {key: tis_labels[key] for key in labeled_leaves if key in tis_labels}
    for key, value in tis_labels_leaves.items():
        new_value = key + "_" + value
        leaf_tis_map[key] = new_value
    
    for leaf in tree_labeled_leaves.iter_leaves():
        current_name = leaf.name
        replacement_name = leaf_tis_map[current_name]
        leaf.name = replacement_name
    
    return tree_labeled_all, tree_labeled_leaves


## PARAMETERS ##
sample_num = int(sys.argv[1])
migration_matrix_filepath = sys.argv[2]
output_name = sys.argv[3]

# sample_num = 100
# migration_matrix_filepath = "migration_matrix_train/true_migration_prob_matrix.csv"
# output_name = "test"


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


# overlay tissue labels for migration information to tree leaves only
labeled_tree_all, labeled_tree_leaves = assign_tissue_labels(ground_truth_tree,migration_matrix)

labeled_tree_all.write(format=8, outfile = f'{output_name}_all_tissue_labels.nwk')
labeled_tree_leaves.write(format=8, outfile = f'{output_name}_only_leaf_tissue_labels.nwk')
