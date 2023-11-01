# Gradient Boosting Classifier for labeling metastasis events on clonal tree
Machine learning approach to add tissue labels to internal nodes of a tree given a cell phylogeny with labeled leaves. A gradient boosting classifier is trained from simulated data where clonal trees are simulated with ground truth tissue labels for internal nodes, and then features from the tree are retained into a vector for training the gradient boosting classifier.

To run the simulations, train the model, and predict on different simulated data, need to first install conda environments:

```
conda create -f env/simulate.yaml
conda create -f env/sklearn.yaml
```

Then, generate the training and testing data:
```
./scripts/internal_nodes/sim_wrapper_internal_nodes.sh --name TRAIN --num_trees 100 --tree_size 100 --migration_matrix_folder ./migration_matrix_train --cores 40
./scripts/internal_nodes/sim_wrapper_internal_nodes.sh --name TEST --num_trees 100 --tree_size 100 --migration_matrix_folder ./migration_matrix_test --cores 40
```

Then, fit the model and find the prediction accuracy for internal node tissue labels:
```
conda activate sklearn
python scripts/internal_nodes/gbm_model_internal_nodes.py tree_dataset_TRAIN.csv tree_dataset_TEST.csv
conda deactivate
```