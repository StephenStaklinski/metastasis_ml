#!/bin/bash

parallel_name="variableSizes_midMM_parallel_compare_gbm_consensus_11_14_23"

tree_size=(100 250 500 750)
migration_matrix="migration_matrix/mid_migration_prob_matrix.csv"

mkdir ${parallel_name}
touch ${parallel_name}/parallel.txt

# echo "name,accuracy_gbm,accuracy_machina,accuracy_consensus,num_nonprimary_nodes,accuracy_nonprimary_gbm,accuracy_machina_nonprimary,accuracy_consensus_nonprimary,tree_size,migration_matrix" > ${parallel_name}/accuracy_gbm_machina.csv
# echo "name,tree_size,migration_matrix,gbm_seconds,machina_seconds,consensus_seconds" > ${parallel_name}/time_gbm_machina.csv

echo "name,accuracy_gbm,accuracy_consensus,num_nonprimary_nodes,accuracy_nonprimary_gbm,accuracy_consensus_nonprimary,tree_size,migration_matrix" > ${parallel_name}/accuracy_gbm_machina.csv
echo "name,tree_size,migration_matrix,gbm_seconds,consensus_seconds" > ${parallel_name}/time_gbm_machina.csv


n_reps=100
j=0
for size in "${tree_size[@]}"; do
    for ((i=1; i<=n_reps; i++)); do
        sim_name="${parallel_name}/sim${j}"
        sim_cmd="./scripts/compare_gbm_machina.sh ${sim_name} ${size} ${migration_matrix}"
        accuracy_cmd="tail -n +2 ${sim_name}/accuracy_true_gbm_machina.csv >> ${parallel_name}/accuracy_gbm_machina.csv"
        time_cmd="tail -n +2 ${sim_name}/time_gbm_machina.csv >> ${parallel_name}/time_gbm_machina.csv"
        # clean_cmd="rm -r ${sim_name}"
        # echo "${sim_cmd} && ${accuracy_cmd} && ${time_cmd} && ${clean_cmd}" >> ${parallel_name}/parallel.txt
        echo "${sim_cmd} && ${accuracy_cmd} && ${time_cmd}" >> ${parallel_name}/parallel.txt
        ((j++))
    done
done


parallel -j 50 < "${parallel_name}/parallel.txt"
rm ${parallel_name}/parallel.txt
mkdir ${parallel_name}/data
mv ${parallel_name}/sim* ${parallel_name}/data/
