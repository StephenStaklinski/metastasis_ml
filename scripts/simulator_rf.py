#!/usr/bin/env python3
import sys
import time
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

## PARAMETERS ##
samples = 100
sites_range = np.arange(1, 101, 1)
m_range = np.arange(0.01, 1.01, 0.01)
results = pd.DataFrame(columns = ['sample_num', 'num_sites', 'mutrate', 'rf_normalized'])

for sites in sites_range:
    for mutrate in m_range:
        sites = int(sites)
        mutrate = float(mutrate)
        print(sites,mutrate)
        # start = time.time()
        # run until 10,000 leaves
        bd_sim = cas.sim.BirthDeathFitnessSimulator(
                #experiment_time = 280
                birth_waiting_distribution = lambda scale: np.random.exponential(scale),
                initial_birth_scale = 0.5,
                num_extant = samples
            )
        ground_truth_tree = bd_sim.simulate_tree()

        # To simulate barcode mutations
        final_matrix = sim_chars(ground_truth_tree,mutrate,sites,samples)

        # To reconstruct tree from simulated barcodes
        reconstructed_tree = cas.data.CassiopeiaTree(character_matrix = final_matrix, missing_state_indicator = -1)
        greedy_solver = cas.solver.VanillaGreedySolver()
        greedy_solver.solve(reconstructed_tree)

        # Change Casseiopeia trees to ETE tree to calculate RF distance between ground truth tree and reconstructed tree
        gtt_connections = ground_truth_tree.edges
        gtt_ete = Tree.from_parent_child_table(gtt_connections)
        rt_connections = reconstructed_tree.edges
        rt_ete = Tree.from_parent_child_table(rt_connections)
        rf, max_rf, common_leaves, partitions_t1, partisionss_t2, set1, set2 = gtt_ete.robinson_foulds(rt_ete, unrooted_trees=True)
        rf_norm = 1 - (rf/max_rf)
        data = {'sample_num':samples,
                'num_sites':sites,
                'mutrate':mutrate,
                'rf_normalized': rf_norm
                }
        new_df = pd.DataFrame(data, index=[0])
        results = pd.concat([results, new_df], ignore_index=True)
        # end = time.time()
        # elapsed = end - start
        # print(f'{elapsed} seconds')
        
