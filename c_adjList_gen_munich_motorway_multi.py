# Import modules.
from multiprocessing import Process, Manager, cpu_count
from itertools import permutations
import pandas as pd
import numpy as np

# Functions to be processed with multiple cores.
def gen_adjList (in_dict_in, in_dict_out, in_int_proc_num):
    
    # Retrieve inputs.
    df_edge_base = in_dict_in["df_edge_base"]
    lst_chu_arr_perm_edge_id = in_dict_in["lst_chu_arr_perm_edge_id"]
    lst_tup_perm_edge_id = lst_chu_arr_perm_edge_id[in_int_proc_num].tolist()
    
    # Set up dict_out.
    lst_out_tmp = []
    
    # Loop calc to append output list when tup elements are connected.
    for tup_perm_edge_id in lst_tup_perm_edge_id:
        
        str_edge_id_from = tup_perm_edge_id[0]
        str_edge_id_to= tup_perm_edge_id[1]
        
        str_node_to_of_edge_from = df_edge_base[df_edge_base.edge_id == str_edge_id_from]["edge_to"].values[0]
        str_node_from_of_edge_to = df_edge_base[df_edge_base.edge_id == str_edge_id_to]["edge_from"].values[0]
        
        if str_node_to_of_edge_from == str_node_from_of_edge_to:
            int_idx_edge_id_from = df_edge_base[df_edge_base.edge_id == str_edge_id_from].index.values[0]
            int_idx_edge_id_to = df_edge_base[df_edge_base.edge_id == str_edge_id_to].index.values[0]
            lst_out_tmp.append([int_idx_edge_id_from, int_idx_edge_id_to])
        else:
            continue
    
    in_dict_out[in_int_proc_num] = lst_out_tmp            
    print(f"Proc_{in_int_proc_num} task completed.")

# Execution part.
if __name__ == '__main__':
    
    int_n_cpu = cpu_count()                 # Retrive core numbers.
    int_n_proc = round(int_n_cpu * 0.7)     # Use only 70% of available cores.
    
    # Import base dataframe for edges.
    # df_edge_base = pd.read_csv("munich_motorway_v3/df_edge_base.csv", index_col=0)
    df_edge_base = pd.read_pickle("munich_motorway_v3/df_edge_seg_ordered.pkl")
    
    # Extract edge_id column into list and make list of permutation tuples.
    lst_edge_id = list(df_edge_base["edge_id"].unique())
    lst_tup_perm_edge_id = list()
    for tup_perm_edge_id in permutations(lst_edge_id, 2):
        lst_tup_perm_edge_id.append(tup_perm_edge_id)
        
    # Make process number chunked permutation list.
    # Element inside of 
    lst_chu_arr_perm_edge_id = np.array_split(lst_tup_perm_edge_id, int_n_proc)
    
    # Make empty list to store the result.
    # lst_store_adjList = []
    dict_store_adjList = dict()
    
    # Execute multi processing with shared memory.
    with Manager() as mng:
        
        # Set input variables into shared memory.
        dict_in = mng.dict()
        dict_in["df_edge_base"] = df_edge_base
        dict_in["lst_chu_arr_perm_edge_id"] = lst_chu_arr_perm_edge_id
        
        # Set output list from multiprocessing.
        # lst_out = mng.list()
        dict_out = mng.dict()        
        
        # Define list of processors and update.
        lst_procs = []
        for proc_num in range(int_n_proc):
            proc = Process(target= gen_adjList, args=(dict_in, dict_out, proc_num))
            lst_procs.append(proc)
            
        # Execute processors.
        for proc in lst_procs:
            proc.start()
            
        # Wait & Close of processors.
        for proc in lst_procs:
            proc.join()
            
        # Store output list.
        dict_store_adjList = dict_out._getvalue()
        
    lst_out_from_dict = []
    for idx in range(int_n_proc):
        lst_out_from_dict = [*lst_out_from_dict, *dict_store_adjList[idx]]
    
    arr_adjcency = np.array(lst_out_from_dict)
    np.save("./munich_motorway_v3/arr_adj_multi_seg_edge_proc.npy", arr_adjcency)
    print("Done.")