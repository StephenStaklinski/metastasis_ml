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

echo "tree_name,node_name,num_total_nodes,num_total_leaves,proportion_children_tree_t1,\
proportion_children_tree_t2,proportion_children_tree_t3,num_leaves_below,proportion_leaves_below,\
dist_to_root,avg_dist_to_leaves,num_nodes_to_root,num_nodes_below,proportion_children_t1,\
proportion_children_t2,proportion_children_t3,node_tissue" > tree_dataset_${NAME}.csv

j=0
for migration_matrix in "$MIGRATION"/*; do
    for ((rep=0; rep<NUM_TREES; rep++))   ### Can set the amount of repeat simulations with the same parameters
    do
    output_name="batch_sim${j}.csv"
    cmd="python scripts/internal_nodes/simulator_internal_nodes.py ${TREE_SIZE} ${migration_matrix} ${output_name}"
    data_cmd="tail -n +2 ${output_name} >> "tree_dataset_${NAME}.csv""
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

