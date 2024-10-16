# Gradient Boosting Classifier for labeling metastasis events on clonal cancer tree with known tissue labels at the tips
Machine learning approach to add tissue labels to internal nodes of a tree given a cell phylogeny with labeled leaves. A gradient boosting classifier is trained from simulated data where clonal trees are simulated with ground truth tissue labels for internal nodes, and then features from the tree are retained into a vector for training the gradient boosting classifier.

To run the simulations, train the model, and/or predict on different simulated data, you will need to first install the necessary conda environments:

```
conda create -f env/simulate.yaml
conda create -f env/sklearn.yaml
```

Then, if you want to simulate training data:
```
./scripts/internal_nodes/sim_wrapper_internal_nodes.sh --name TRAIN --num_trees 100 --tree_size 1000 --migration_matrix_folder ./migration_matrix/training_set --cores 40
```

To then train the model:
```
conda activate sklearn
python scripts/internal_nodes/train_gbm_model_internal_nodes.py tree_dataset_TRAIN.csv 
conda deactivate
```

There are two ways to run the model on test data:

1. Simulate test data with known matching ground truth tissue labels to automatically calculate accuracy of predictions.
2. Use an input newick file for a tree with labeled leaves but no known ground truth for the node labels.

To perform option 1:
```
./scripts/internal_nodes/sim_wrapper_internal_nodes.sh --name TEST --num_trees 100 --tree_size 100 --migration_matrix_folder ./migration_matrix --cores 40
conda activate sklearn
python scripts/internal_nodes/test_gbm_model_internal_nodes.py trained_gbm_model.joblib tree_dataset_TEST.csv
conda deactivate
```

To perform option 2:
```
conda activate simulate
python scripts/internal_nodes/leaf_labeled_newick_to_features_internal_nodes.py test_only_leaf_tissue_labels.nwk t1,t2,t3 test_features_leaf_tree.csv
conda deactivate
conda activate sklearn
python scripts/internal_nodes/test_gbm_model_internal_nodes.py trained_gbm_model.joblib test_features_leaf_tree.csv
conda deactivate
```

The `test_only_leaf_tissue_labels.nwk` file should be replaced with your newick file path, the `t1,t2,t3` corresponds to the tissue names and is the default 3 tissue setting or should otherwise match the tissues used in the migration matrix for training, and the `test_features_leaf_tree.csv` is the output file path which is then fed into the gbm model for training.

If one would like to simulate a tree with only leaf labels, then do the following:
```
conda activate simulate
python scripts/internal_nodes/sim_leaf_and_all_labeled_matched_newicks.py 100 migration_matrix/true_migration_prob_matrix.csv test
conda deactivate
```

This will output two newick files that are matched with one that only has the leaves labeled and the other that has the leaves and internal nodes labeled. Both of these newick files can be processed into features csv files for testing the gbm based on similar commands as above for option 2 using either the `scripts/internal_nodes/leaf_labeled_newick_to_features_internal_nodes.py` script for a newick file with only leaf labels or the `scripts/internal_nodes/all_labeled_newick_to_features_internal_nodes.py` script for a newick file with all node and leaf labels.


To run MACHINA on leaf labeled tree to get internal node labels:
```
conda activate ete3
./scripts/machina/prep_machina.sh test_only_leaf_tissue_labels.nwk
conda deactivate
```

```
conda activate machina
./scripts/machina/run_machina.sh --edges test_only_leaf_tissue_labels.tree --labels test_only_leaf_tissue_labels.labeling --colors test_only_leaf_tissue_labels_colors.txt --primary-tissue t1 --outdir machina_results/
conda deactivate
```

# Motivation and Results

This approach was largely inspired by the cell lineage machine learning approach using a gradient boost machine to predict cell lineage relationships from a feature vector of barcode information. This tool was named [AMbeRland-TR](https://academic.oup.com/nargab/article/5/3/lqad077/7246553) and was the best performing method in a cell lineage reconstruction [DREAM challenge](https://www.sciencedirect.com/science/article/pii/S2405471221001940).

This repo mimics this feature vector approach to training a classifier, but it is fairly underdeveloped since the performance of this method was seen to be on par with the best existing combinatorial optimization based method [MACHINA](https://github.com/raphael-group/machina) on relatively simple simulations of metastasis:

![Alt text](/results/range_sizes_trueMM_parallel_compare_gbm_machina_11_14_23/accuracy_gbm_machina.png?raw=true "Performance of this GBM approach compared to MACHINA.")

Scalability of this type of approach is promising, but a more serious artificial neural network approach and larger training datasets (real data if eventually possible) are likely necessary to improve performance significantly.

![Alt text](/results/range_sizes_trueMM_parallel_compare_gbm_machina_11_14_23/time_plot.png?raw=true "Runtime for this GBM approach compared to MACHINA as a function of the number of tips in the clone tree.")



