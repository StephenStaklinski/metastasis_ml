#!/bin/bash
source ~/anaconda3/etc/profile.d/conda.sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <sim_dir> <tree_size> <migration_matrix>"
    exit 1
fi

# Assign command-line arguments to variables
sim_dir="$1"
tree_size="$2"
migration_matrix="$3"

# sim_name="test"
# tree_size=100
# migration_matrix="migration_matrix/true_migration_prob_matrix.csv"

sim_name=$(echo "$sim_dir" | awk -F'/' '{print $NF}')
mkdir ${sim_dir}

# Simulate matched trees for test data
tree_dir="${sim_dir}/${sim_name}_trees"
mkdir ${tree_dir}
conda activate simulate
python scripts/internal_nodes/sim_leaf_and_all_labeled_matched_newicks.py ${tree_size} ${migration_matrix} ${tree_dir}
conda deactivate

# Run consensus tissue method on test trees
start_time=$(date +%s.%N)

consensus_dir="${sim_dir}/${sim_name}_consensus_tissue"
mkdir ${consensus_dir}
conda activate ete3
python scripts/consensus_tissue/run_consensus_tissue.py ${tree_dir}/only_leaf_tissue_labels.nwk ${consensus_dir}
conda deactivate

mv ${consensus_dir}/consensus_tissue_tree_all_tissue_labels.nwk ${sim_dir}/
rm -r ${consensus_dir}

end_time=$(date +%s.%N)
consensus_time=$(printf "%.2f" $(echo "$end_time - $start_time" | bc))


# # Run MACHINA on test trees
# # check if t1 exists as a leaf label otherwise MACHINA cannot run and exit 0 to discard the simulation
# if ! grep -q 't1' ${tree_dir}/only_leaf_tissue_labels.nwk; then
#     echo "Primary tissue label t1 not in leaf labels. MACHINA cannot run. Exit and remove ${sim_name}."
#     exit 0
# fi

# start_time=$(date +%s.%N)

# machina_dir="${sim_dir}/${sim_name}_machina"
# mkdir ${machina_dir}
# conda activate ete3
# python ./scripts/machina/prep_machina.py ${tree_dir}/only_leaf_tissue_labels.nwk ${machina_dir}
# conda deactivate

# conda activate machina
# ./scripts/machina/run_machina.sh --edges ${machina_dir}/*.tree --labels ${machina_dir}/*.labeling --colors ${machina_dir}/*_colors.txt --primary-tissue t1 --outdir ${machina_dir}
# conda deactivate

# conda activate ete3
# python ./scripts/machina/post_machina_to_tree.py ${tree_dir}/only_leaf_tissue_labels.nwk ${machina_dir}/T-t1-0.labeling ${machina_dir}
# conda deactivate

# mv ${machina_dir}/machina_tree_all_tissue_labels.nwk ${sim_dir}/
# rm -r ${machina_dir}

# end_time=$(date +%s.%N)
# machina_time=$(printf "%.2f" $(echo "$end_time - $start_time" | bc))
# # echo "${machina_time} seconds elapsed for MACHINA"

# Run GBM on test trees
start_time=$(date +%s.%N)

gbm_dir="${sim_dir}/${sim_name}_gbm"
mkdir ${gbm_dir}
conda activate simulate
python scripts/internal_nodes/leaf_labeled_newick_to_features_internal_nodes.py ${tree_dir}/only_leaf_tissue_labels.nwk t1,t2,t3 ${gbm_dir}/${sim_name}_features_leaf_tree.csv
conda deactivate

conda activate sklearn
python scripts/internal_nodes/test_gbm_model_internal_nodes.py trained_model/trained_gbm_model.joblib ${gbm_dir}/${sim_name}_features_leaf_tree.csv ${gbm_dir}
conda deactivate

conda activate ete3
python scripts/internal_nodes/post_gbm_to_tree.py ${tree_dir}/only_leaf_tissue_labels.nwk ${gbm_dir}/gbm_data.csv ${gbm_dir}
conda deactivate

mv ${gbm_dir}/gbm_tree_all_tissue_labels.nwk ${sim_dir}/
rm -r ${gbm_dir}

mv ${tree_dir}/all_tissue_labels.nwk ${sim_dir}/
rm -r ${tree_dir}

end_time=$(date +%s.%N)
gbm_time=$(printf "%.2f" $(echo "$end_time - $start_time" | bc))
# echo "${gbm_time} seconds elapsed for GBM"

# Compare accuracy of GBM and MACHINA trees against the ground truth tree
conda activate ete3
# python scripts/accuracy_gbm_machina.py ${sim_dir}/all_tissue_labels.nwk ${sim_dir}/gbm_tree_all_tissue_labels.nwk ${sim_dir}/machina_tree_all_tissue_labels.nwk ${sim_dir}/consensus_tissue_tree_all_tissue_labels.nwk ${sim_dir} ${migration_matrix}
python scripts/accuracy_gbm_machina.py ${sim_dir}/all_tissue_labels.nwk ${sim_dir}/gbm_tree_all_tissue_labels.nwk ${sim_dir}/consensus_tissue_tree_all_tissue_labels.nwk ${sim_dir} ${migration_matrix}
conda deactivate

mm=$(IFS='/' read -ra parts <<< "$migration_matrix" && echo "${parts[-1]}")

# echo "name,tree_size,migration_matrix,gbm_seconds,machina_seconds,consensus_seconds" > ${sim_dir}/time_gbm_machina.csv
# echo "${sim_name},${tree_size},${mm},${gbm_time},${machina_time},${consensus_time}" >> ${sim_dir}/time_gbm_machina.csv
echo "name,tree_size,migration_matrix,gbm_seconds,consensus_seconds" > ${sim_dir}/time_gbm_machina.csv
echo "${sim_name},${tree_size},${mm},${gbm_time},${consensus_time}" >> ${sim_dir}/time_gbm_machina.csv