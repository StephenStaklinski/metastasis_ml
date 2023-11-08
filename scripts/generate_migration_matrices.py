import numpy as np
import pandas as pd

# Function to generate a random matrix
def generate_random_matrix(size):
    global min_prob_stay

    matrix = np.zeros((size, size))

    for i in range(size):
        last_value = None
        max_value = np.random.uniform(min_prob_stay, 1)
        for j in range(size):
            if i == j:
                matrix[i, j] = max_value
            else:
                # Random value up to the max value
                if last_value == None:
                    matrix[i, j] = np.random.uniform(0, 1 - max_value)
                    last_value = (1 - max_value) - matrix[i, j]
                else:
                    matrix[i,j] = last_value
                
    return matrix

# Number of matrices to generate

num_matrices = 1000
matrix_size = 3

min_prob_stay = 0.70
outdir = "migration_matrix/training_set/"

for i in range(1, num_matrices + 1):
    matrix = generate_random_matrix(matrix_size)
    df = pd.DataFrame(matrix, columns=[f't{i}' for i in range(1, matrix_size + 1)], index=[f't{i}' for i in range(1, matrix_size + 1)])
    df.to_csv(f'{outdir}matrix_{i}.csv', float_format='%.2f')
