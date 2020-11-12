import json
import os
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "../../../")))

from fedml_api.model.linear.lr import LogisticRegression

def batch_data(data, batch_size):
    '''
    data is in panda frames [f1, f2, f3, label]
    convert it into batches of (x, y)
    '''
    # randomly shuffle data
    data = data.sample(frac=1).reset_index(drop=True)

    # convert to numpy arrays
    data_x = data[['f1', 'f2', 'f3']].values.astype(np.float64)
    data_y = data[['label']].values.astype(np.int32).flatten()

    # loop through mini-batches
    batch_data = list()
    for i in range(0, len(data_x), batch_size):
        batched_x = data_x[i:i + batch_size]
        batched_y = data_y[i:i + batch_size]
        batched_x = torch.from_numpy(np.asarray(batched_x)).float()
        batched_y = torch.from_numpy(np.asarray(batched_y)).long()
        batch_data.append((batched_x, batched_y))
    return batch_data

def generate_data_sea(train_iteration, num_client, drift_together):

    data_path = "./../../../data/sea/"

    # We always use 500 samples per client in each training iteration
    # TODO: change to variable sample sizes
    # TODO: generate more clients than requested for client sampling
    sample_per_client_iter = 500

    # For now we only use the first two concepts
    df_con1 = pd.read_csv(data_path + 'concept1.csv')
    df_con2 = pd.read_csv(data_path + 'concept2.csv')

    # Randomly generate change point for each client
    if drift_together == 1:
        cp = np.random.random_sample() * train_iteration
        change_point = [cp for c in range(num_client)]
    else:
        change_point = [np.random.random_sample() * train_iteration
                        for c in range(num_client)]
        
    # Generate data for each client/iteration
    train_data = [[] for t in range(train_iteration + 1)]
    for it in range(train_iteration + 1):
        for c in range(num_client):
            train_df = pd.DataFrame(columns = list(df_con1.columns))
            # Get samples for the first concept
            if it < change_point[c]:
                num_sample = int(min(1.0, change_point[c] - it) *
                                 sample_per_client_iter)
                train_df = train_df.append(df_con1.sample(n=num_sample),
                                           ignore_index=True)
            # Get samples for the second concept
            if it + 1 > change_point[c]:
                num_sample = int(min(1.0, it + 1.0 - change_point[c]) *
                                 sample_per_client_iter)
                train_df = train_df.append(df_con2.sample(n=num_sample),
                                           ignore_index=True)
            # Save the data as files
            train_df.to_csv(data_path +
                            'client_{}_iter_{}.csv'.format(c, it),
                            index = False)
            
    # Write change points for debugging
    with open(data_path + 'change_points', 'w') as cpf:
        for c in range(num_client):
            cpf.write('{}\n'.format(change_point[c]))
    

def load_partition_data_sea(batch_size, current_train_iteration,
                            num_client):
    data_path = "./../../../data/sea/"

    # Load the data from generated CSVs
    train_data = [pd.DataFrame() for c in range(num_client)]
    test_data = []
    
    # We use all the data until the current iteration as training data
    # TODO: change it to an option for other methods
    for it in range(current_train_iteration + 1):
        for c in range(num_client):
            train_df = pd.read_csv(data_path +
                                   'client_{}_iter_{}.csv'.format(c, it))
            train_data[c] = train_data[c].append(train_df,
                                                 ignore_index=True)
            
    # Use the data in the next training iteration as the test data
    for c in range(num_client):
        test_df = pd.read_csv(data_path +
                              'client_{}_iter_{}.csv'.format(
                                  c, current_train_iteration + 1))
        test_data.append(test_df)                    
    
    # Prepare data into multiple training iterations
    train_data_num = 0
    test_data_num = 0
    train_data_local_dict = dict()
    test_data_local_dict = dict()
    train_data_local_num_dict = dict()
    train_data_global = list()
    test_data_global = list()

    for c in range(num_client):
        train_data_num += len(train_data[c].index)
        test_data_num += len(test_data[c].index)
        train_data_local_num_dict[c] = len(train_data[c].index)

        # transform to batches
        train_batch = batch_data(train_data[c], batch_size)
        test_batch = batch_data(test_data[c], batch_size)

        # put batched data into the arrays
        train_data_local_dict[c] = train_batch
        test_data_local_dict[c] = test_batch

        train_data_global += train_batch
        test_data_global += test_batch
    
    client_num = num_client
    class_num = 2

    return client_num, train_data_num, test_data_num, train_data_global, \
        test_data_global, train_data_local_num_dict, train_data_local_dict, \
        test_data_local_dict, class_num


def main():

    np.random.seed(0)
    torch.manual_seed(10)

    generate_data_sea(5, 10, 0)
    
    client_num, train_data_num, test_data_num, train_data_global, \
    test_data_global, train_data_local_num_dict, train_data_local_dict, \
    test_data_local_dict, class_num = \
    load_partition_data_sea(10, 3, 10)

    print(client_num)
    print(train_data_num)
    print(test_data_num)    
    print(train_data_local_num_dict)
    print(class_num)
    print(test_data_global[0])
    
    

if __name__ == '__main__':
    main()