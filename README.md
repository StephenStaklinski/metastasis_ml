# metastasis_ml
Machine learning approach to add tissue labels to internal nodes of a tree given a cell phylogeny with labeled leaves.

Example to simulate dataset of tree features and ground truth migration events:
`./scripts/sim_tree_dataset_wrapper.sh --name TEST --num_trees 2 --migration_matrix_folder ./migration_matrix --cores 2`