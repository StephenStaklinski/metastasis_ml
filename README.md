# Gradient Boosting Classifier for labeling metastasis events on clonal tree
Machine learning approach to add tissue labels to internal nodes of a tree given a cell phylogeny with labeled leaves. A gradient boosting classifier is trained from simulated data where clonal trees are simulated with ground truth tissue labels for internal nodes, and then features from the tree are retained into a vector for training the gradient boosting classifier.

To run the simulations, train the model, and/or predict on different simulated data, you will need to first install the necessary conda environments:

```
conda create -f env/simulate.yaml
conda create -f env/sklearn.yaml
```

Then, if you want to simulate training data:
```
./scripts/internal_nodes/sim_wrapper_internal_nodes.sh --name TRAIN --num_trees 100 --tree_size 100 --migration_matrix_folder ./migration_matrix --cores 40
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
conda activate sklearn
python scripts/internal_nodes/leaf_labeled_newick_to_features_internal_nodes.py test_only_leaf_tissue_labels.nwk 1,2,3 test_features_leaf_tree.csv
python scripts/internal_nodes/test_gbm_model_internal_nodes.py trained_gbm_model.joblib test_features_leaf_tree.csv
conda deactivate
```

The `test_only_leaf_tissue_labels.nwk` file should be replaced with your newick file path, the `1,2,3` corresponds to the tissue names and is the default 3 tissue setting or should otherwise match the tissues used in the migration matrix for training, and the `test_features_leaf_tree.csv` is the output file path which is then fed into the gbm model for training.

If one would like to simulate a tree with only leaf labels, then do the following:
```
conda activate simulate
python scripts/internal_nodes/sim_leaf_and_all_labeled_matched_newicks.py 100 migration_matrix/true_migration_prob_matrix.csv test
conda deactivate
```

This will output two newick files that are matched with one that only has the leaves labeled and the other that has the leaves and internal nodes labeled. Both of these newick files can be processed into features csv files for testing the gbm based on similar commands as above for option 2 using either the `scripts/internal_nodes/leaf_labeled_newick_to_features_internal_nodes.py` script for a newick file with only leaf labels or the `scripts/internal_nodes/all_labeled_newick_to_features_internal_nodes.py` script for a newick file with all node and leaf labels.
