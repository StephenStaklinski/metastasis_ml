#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh

if [[ $# -eq 0 ]] ; then
    echo "Usage: ./scripts/sim_tree_dataset_wrapper.sh --name <dataset_name | char> --num_trees <int> --tree_size <int> --migration_matrix_folder <folder_path | char> --cores <int>"
    exit 0
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -n|--name) NAME="$2"; shift ;;
        -t|--num_trees) NUM_TREES="$2"; shift ;;
        -s|--tree_size) TREE_SIZE="$2"; shift ;;
        -m|--migration_matrix_folder) MIGRATION="$2"; shift ;;
        -c|--cores) CORES="$2"; shift ;;


    *) echo "Unknown parameter passed: $1"; echo "Usage: ./scripts/sim_tree_dataset_wrapper.sh --num_trees <int> --tree_size <int> --migration_matrix_folder <folder_path>"; exit 1 ;;
    esac
    shift
done

conda activate simulate

echo "tree_name,l1_name,l2_name,mrca_name,l1_tissue,l2_tissue,total_nodes_leaves,total_num_leaves,total_num_nodes,proportion_leaves_l1_tissue,proportion_leaves_l2_tissue,l1_sis_tissue,l2_sis_tissue,num_nodes_prior_l1,num_nodes_prior_l2,tissues_matching,dist_l1_l2,mrca_proportion_children_root_tissue,mrca_proportion_children_l1_tissue,mrca_proportion_children_l2_tissue,mrca_tissue" > tree_dataset_${NAME}.csv

j=0
for migration_matrix in "$MIGRATION"/*; do
    for ((rep=0; rep<NUM_TREES; rep++))   ### Can set the amount of repeat simulations with the same parameters
    do
    output_name="batch_sim${j}.csv"
    cmd="python scripts/simulator_pairwise.py ${TREE_SIZE} ${migration_matrix} ${output_name}"
    data_cmd="tail -n +2 $output_name >> "tree_dataset_${NAME}.csv""
    clean_cmd="rm ${output_name}"
    commands+=("$cmd && $data_cmd && $clean_cmd")
    j=$((j+1))
    done
done

echo "There are ${#commands[@]} commands to be submitted."

for command in "${commands[@]}"
do
  echo "${command}" >> "parallel.txt"
done

parallel -j ${CORES} < "parallel.txt"
rm parallel.txt


conda deactivate

