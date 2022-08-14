# Import modules.
from multiprocessing import Process, Manager, cpu_count
from itertools import permutations
from od_cal_fct.flow_gen import *
from od_cal_fct.user_utill import *
import pandas as pd
import numpy as np
import time
import os

# Function to wrap simulation part for multiprocess.

def sim_sumo_multiProc(in_dict_in, in_int_proc_num):
    
    df_edge_seg_ordered = in_dict_in["df_edge_seg_ordered"]
    lst_chu_path_df_od_sample = in_dict_in["lst_chu_path_df_od_sample"]
    lst_path_df_od_sample = lst_chu_path_df_od_sample[in_int_proc_num]    
    idx_proc = in_int_proc_num + 1
    
    str_dir_proc = f"./data_sumo/proc_{idx_proc}"
    str_dir_sumo_tmp = os.path.join(str_dir_proc, "tmp") 
    str_dir_edgeInfo = os.path.join(str_dir_proc, "tmp_edgeInfo")    
    str_dir_flow_sample = "./data_tabular/flow_samples_mmv3"
    
    idx_iter = 0
    for str_path_df_od_sample in lst_path_df_od_sample:
        
        idx_iter += 1        
        str_flow_nName_tmp1 = str_path_df_od_sample.split("/")[-1].replace("_od_", "_flow_")
        str_path_flow_tmp1 = os.path.join(str_dir_flow_sample, str_flow_nName_tmp1)
        
        df_od_sample_tmp1 = pd.read_pickle(str_path_df_od_sample)
        
        df_flow_tmp1 = sim_sumo_get_flow_munich_multi(
            in_int_proc_num= idx_proc, in_int_iter= idx_iter,
            in_df_perturbed_od= df_od_sample_tmp1,
            in_df_edge_seg_ordered= df_edge_seg_ordered,
            in_str_dir_sumo_tmp= str_dir_sumo_tmp,
            in_str_dir_edgeInfo= str_dir_edgeInfo,
        )
        
        df_flow_tmp1.to_pickle(str_path_flow_tmp1)
        print(f"Simulated flow data is saved. Proc_{idx_proc}_Iter_{idx_iter}")


# Execution part.
if __name__ == '__main__':
    
    start_time = time.time()
    
    # int_n_cpu = cpu_count()                 # Retrive core numbers.
    # int_n_proc = round(int_n_cpu * 0.7)     # Use only 70% of available cores.    
    int_n_proc = 15 # Let's use this number of processors.
    
    # Import edge info dataframe segmented ordered.
    df_edge_seg_ordered = pd.read_pickle("munich_motorway_v3/df_edge_seg_ordered.pkl")
    # Import list of file paths for od samples.
    lst_path_df_od_sample = fileListCreator("data_tabular/od_samples_mmv3", lv_flt= True, ext_flt= "pkl")
    
    # Make process number chuncked OD sample lists.
    lst_chu_path_df_od_sample = np.array_split(lst_path_df_od_sample, int_n_proc)
    
    # Execute multi processing with shared memory.
    with Manager() as mng:
        
        # Set input variables into shared memory.
        dict_in = mng.dict()
        dict_in["df_edge_seg_ordered"] = df_edge_seg_ordered
        dict_in["lst_chu_path_df_od_sample"] = lst_chu_path_df_od_sample
        
        # Define list of processors and update.
        lst_procs = []
        for proc_num in range(int_n_proc):
            proc = Process(target= sim_sumo_multiProc, args=(dict_in, proc_num))
            lst_procs.append(proc)
            
        # Execute processors.
        for proc in lst_procs:
            proc.start()
            
        # Wait & Close of processors.
        for proc in lst_procs:
            proc.join()
            
    time_epoch = time.time() - start_time
    
    print(f"Done. Time elapsed: {int(time_epoch/60):04d} [min]")