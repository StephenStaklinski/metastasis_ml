#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh

if [[ $# -eq 0 ]] ; then
    echo "Usage: ./scripts/sim_tree_dataset_wrapper.sh --name <dataset_name | char> --num_trees <int> --migration_matrix_folder <folder_path | char> --cores <int>"
    exit 0
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -n|--name) NAME="$2"; shift ;;
        -t|--num_trees) NUM_TREES="$2"; shift ;;
        -m|--migration_matrix_folder) MIGRATION="$2"; shift ;;
        -c|--cores) CORES="$2"; shift ;;


    *) echo "Unknown parameter passed: $1"; echo "Usage: ./scripts/sim_tree_dataset_wrapper.sh --num_trees <int> --migration_matrix_folder <folder_path>"; exit 1 ;;
    esac
    shift
done

if [ ! -f "./scripts/simulator.py" ]
then
    echo "Script ./scripts/simulator.py not found. Exiting!"
    exit
fi

conda activate simulate

j=0
for migration_matrix in "$MIGRATION"/*; do
    for ((rep=0; rep<NUM_TREES; rep++))   ### Can set the amount of repeat simulations with the same parameters
    do
    output_name="batch_sim${j}"
    tree_size=100
    cmd="python scripts/simulator.py ${tree_size} ${migration_matrix} ${output_name}"
    commands+=("$cmd")
    j=$((j+1))
    done
done

echo "There are ${#commands[@]} commands to be submitted."

echo "tree_name,l1_name,l2_name,mrca_name,l1_tissue,l2_tissue,total_nodes_leaves,total_num_leaves,total_num_nodes,proportion_leaves_l1_tissue,proportion_leaves_l2_tissue,l1_sis_tissue,l2_sis_tissue,num_nodes_prior_l1,num_nodes_prior_l2,tissues_matching,dist_l1_l2,mrca_proportion_children_root_tissue,mrca_proportion_children_l1_tissue,mrca_proportion_children_l2_tissue,mrca_tissue" > tree_dataset_${NAME}.csv

batch_size=${CORES}
num_batches=$(((${#commands[@]} / $batch_size) + 1))

echo "Beginning submission of all combinations in parallel batches of ${batch_size}..."
for ((i=0; i<$num_batches; i++))
do
  echo "Submitting batch $((i+1))/$((num_batches)):"
  # Calculate the range of commands to submit in this batch
  start_index=$((i * batch_size))
  end_index=$((start_index + batch_size - 1))

  # Check if the end index is greater than or equal to the length of the commands array
  if [ $end_index -ge ${#commands[@]} ]; then
    batch_commands=("${commands[@]:${start_index}}") # Slice from start index to end of commands array
  else
    batch_commands=("${commands[@]:${start_index}:${batch_size}}") # Slice from start index to batch_size
  fi

  for command in "${batch_commands[@]}"
  do
    echo "${command}" >> "${i}.cmd"
    echo "${command}"
  done
  # Print the ParaFly command to the console
  ParaFly -CPU ${batch_size} -c ${i}.cmd
  rm ${i}.cmd
  rm ${i}.cmd.completed
  # for f in batch_sim*; do tail -n +2 "$f" | cut -f3- -d"," >> "tree_dataset_${NAME}.csv"; done
    for f in batch_sim*; do tail -n +2 "$f" >> "tree_dataset_${NAME}.csv"; done


  rm batch_sim*
done

echo "All batches are done."

conda deactivate

