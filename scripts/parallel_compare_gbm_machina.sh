#!/bin/bash

parallel_name="parallel_compare_gbm_machina"

tree_size=100
migration_matrix="migration_matrix/true_migration_prob_matrix.csv"

mkdir ${parallel_name}
touch ${parallel_name}/parallel.txt

echo "name,accuracy_gbm,accuracy_machina,num_nonprimary_nodes,accuracy_nonprimary_gbm,accuracy_machina_nonprimary" > ${parallel_name}/accuracy_gbm_machina.csv
echo "name,gbm_seconda,machina_seconds" > ${parallel_name}/time_gbm_machina.csv


n_reps=1
for ((i=1; i<=n_reps; i++)); do
    sim_name="${parallel_name}/sim${i}"
    sim_cmd="./scripts/compare_gbm_machina.sh ${sim_name} ${tree_size} ${migration_matrix}"
    accuracy_cmd="tail -n +2 ${sim_name}/accuracy_true_gbm_machina.csv >> ${parallel_name}/accuracy_gbm_machina.csv"
    time_cmd="tail -n +2 ${sim_name}/time_gbm_machina.csv >> ${parallel_name}/time_gbm_machina.csv"
    clean_cmd="rm -r ${sim_name}"
    echo "${sim_cmd} && ${accuracy_cmd} && ${time_cmd} && ${clean_cmd}" >> ${parallel_name}/parallel.txt

done


parallel -j 10 < "${parallel_name}/parallel.txt"
rm ${parallel_name}/parallel.txt
