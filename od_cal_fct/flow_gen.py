# Import necessary modules.
import os
import pandas as pd
from od_cal_fct.graph_gen import *
from od_cal_fct.user_utill import *

# Function to create tazRel.xml file.
def createTazRel (
    in_str_path_sumo_tmp, in_str_id_tazRel,
    in_str_sim_st, in_str_sim_end, in_df_od: pd.DataFrame
):
    
    str_path_output_tmp = in_str_path_sumo_tmp + "/tmp_tazRel.tazRel.xml"
    
    with open(str_path_output_tmp, "w") as tazRel:
        
        print(
            "<data>"
            , file= tazRel
        )

        # Define interval information. 
        print(
            "    <interval id=\"{}\" begin=\"{}\" end=\"{}\">".format(in_str_id_tazRel, in_str_sim_st, in_str_sim_end)
            , file= tazRel
        )
        
        # Loop calculation for each origin and destination pair.
        # Row index stands for origin and Column index stands for destination.
        tup_dim_tmp = in_df_od.shape
        for i_row in range(tup_dim_tmp[0]):
            for i_col in range(tup_dim_tmp[1]):
                val_tmp = in_df_od.iat[i_row, i_col]            # Flow value.
                name_row_tmp = in_df_od.iloc[i_row,:].name      # Name of Origin.
                name_col_tmp = in_df_od.iloc[:,i_col].name      # Name of Destination.
                # If there is no flow given to certain OD pair or diagonal elements.
                # Trip definition will not be updated.
                if (
                    (name_row_tmp != name_col_tmp) &
                    (val_tmp != 0)
                ):
                    print(
                        "        <tazRelation from=\"{}\" to=\"{}\" count=\"{}\"/>".format(name_row_tmp, name_col_tmp, val_tmp)
                        , file= tazRel
                    )                
                else:
                    continue
        
        # Interval closing.
        print(
            "    </interval>"
            , file= tazRel
        )    
        
        print(
            "</data>"
            , file= tazRel
        )
    
    return str_path_output_tmp

# Function to create odtrips.xml file.
def createOdTrips(
    in_str_path_sumo_tmp, in_str_path_taz, in_str_path_tazRel
):
    
    str_path_output_tmp = in_str_path_sumo_tmp + "/tmp_OD_trips.odtrips.xml"
    
    str_command_tmp = "od2trips " + "-n {} -z {} -o {} --no-step-log True --no-warnings True".format(
        in_str_path_taz, in_str_path_tazRel, str_path_output_tmp
    )
    #--no-step-log True
    
    lv_suc_tmp = os.system(str_command_tmp)
    
    return lv_suc_tmp, str_path_output_tmp

# Function to create rou.xml file.
def createRoute(
    in_str_path_sumo_tmp, in_str_path_net, 
    in_str_path_odtrips, in_str_path_vType 
):
    
    str_path_output_tmp = in_str_path_sumo_tmp + "/tmp_od_routes.rou.xml"
    
    str_command_tmp = "duarouter -n {} --route-files {} -o {} --additional-files {} --no-step-log True --no-warnings True".format(
        in_str_path_net, in_str_path_odtrips, str_path_output_tmp, in_str_path_vType
    )
    #--no-step-log True
    
    lv_suc_tmp = os.system(str_command_tmp)
    
    return lv_suc_tmp, str_path_output_tmp

# Function to create tmp_edgeInfo.additional.xml file
def createAddEdgeInfo(
    in_str_path_sumo_tmp, in_str_edgeInfo_id, in_str_path_edgeInfo
):
    str_path_output_tmp = in_str_path_sumo_tmp + "/tmp_edgeInfo.additional.xml"
    
    with open(str_path_output_tmp, "w") as edgeInfoAdd:
        
        print(
            "<additional>"
            , file= edgeInfoAdd
        )
        
        print(
            "    <edgeData id=\"{}\" file=\"{}\"/>".format(in_str_edgeInfo_id, in_str_path_edgeInfo)
            , file= edgeInfoAdd
        )
        
        print(
            "</additional>"
            , file= edgeInfoAdd
        )
        
    return str_path_output_tmp

# Function to simulate SUMO and generate flow data.
def sim_sumo_get_flow_munich (
    in_int_iter_cur_opti:int, in_int_iter_cur_gradi:int, in_df_perturbed_od:pd.DataFrame, in_df_edge_seg_ordered:pd.DataFrame,
    in_str_id_tazRel:str = "car", in_str_sim_st:str = "0", in_str_sim_end:str = "2:0:0",
    in_fl_sim_step:float = 1.0, in_str_path_net:str = "data_sumo/mmv3.net.xml",
    in_str_path_taz:str = "data_sumo/taz_edges.taz.xml", in_str_path_vType:str = "./data_sumo/vehicleType.vType.xml",
    in_str_dir_sumo_tmp = "./data_sumo/tmp", in_str_dir_edgeInfo:str = "./data_sumo/tmp_edgeInfo"
) -> pd.DataFrame:
    
    # Initialize temporary folders.
    delAllInDir(in_str_dir_sumo_tmp)
    delAllInDir(in_str_dir_edgeInfo)
    
    # Adjust input argument. 
    if in_int_iter_cur_gradi == 999:
        in_int_iter_cur_gradi = "Minimization"
    
    # Create tazRel file in temporary directory.
    str_path_tazRel = createTazRel(
        in_str_dir_sumo_tmp, in_str_id_tazRel, in_str_sim_st,
        in_str_sim_end, in_df_perturbed_od
    )
    # Create odtrips.xml file.
    lv_suc_odtrips, str_path_odtrips = createOdTrips(
        in_str_dir_sumo_tmp, in_str_path_taz, str_path_tazRel
    )
    # Check if odtrips file has been successfully created.
    if lv_suc_odtrips != 0:
        print(f"        Error on odtrips generation! Iteration_{in_int_iter_cur_opti}_{in_int_iter_cur_gradi}.")
        return None
    
    # Create rou.xml (Route) file.
    lv_suc_rou, str_path_rou = createRoute(
        in_str_dir_sumo_tmp, in_str_path_net, str_path_odtrips, in_str_path_vType
    )
    
    # Check if route file has been successfully created.
    if lv_suc_rou != 0:
        print(f"        Error on route generation! Iteration_{in_int_iter_cur_opti}_{in_int_iter_cur_gradi}.")
        return None
    
    # Define link flow output file path.
    str_edgeInfo_id = "edgeInfo"
    str_edgeInfo_fName = "edgeInfo.xml"
    str_path_edgeInfo = os.path.join(os.path.abspath(in_str_dir_edgeInfo), str_edgeInfo_fName)
    
    # Define edgeInfo.additional.xml file.
    str_path_edgeInfoAdd = createAddEdgeInfo(in_str_dir_sumo_tmp, str_edgeInfo_id, str_path_edgeInfo)
    print(f"        All temporary files are ready for simulation. Iteration_{in_int_iter_cur_opti}_{in_int_iter_cur_gradi}.")
    
    # Run simulation.
    str_command_sim_tmp = "sumo -n {} -r {} -b 0 --step-length {} -v False --no-step-log True --no-warnings True --additional-files {}".format(
        in_str_path_net, str_path_rou, in_fl_sim_step, str_path_edgeInfoAdd
    )
    lv_suc_sim = os.system(str_command_sim_tmp)
    
    if lv_suc_sim != 0:
        print(f"        Error on SUMO simulation! Iteration_{in_int_iter_cur_opti}_{in_int_iter_cur_gradi}.")
        return None
    
    print(f"        SUMO Simulation done! Iteration_{in_int_iter_cur_opti}_{in_int_iter_cur_gradi}.")
    
    # Read output edgeInfo file and convert it into dataframe format.
    df_flow_raw = xml2df_edge_flow_v2(str_path_edgeInfo)
    df_flow = seg_edge_ordered_flow(in_df_edge_flow_raw= df_flow_raw, in_df_edge_seg_ordered= in_df_edge_seg_ordered)
    tup_dim_df_out_sim = df_flow.shape
    print(f"        Simulation output is available! Dimension: {tup_dim_df_out_sim[0]} by {tup_dim_df_out_sim[1]}.")
    print(f"        Iteration_{in_int_iter_cur_opti}_{in_int_iter_cur_gradi}.")
            
    # Initialize temporary folders.
    delAllInDir(in_str_dir_sumo_tmp)
    delAllInDir(in_str_dir_edgeInfo)
    
    # Return output dataframe.
    return df_flow

# MULTIPROCESS: Function to simulate SUMO and generate flow data.
def sim_sumo_get_flow_munich_multi (
    in_int_proc_num:int, in_int_iter:int,
    in_df_perturbed_od:pd.DataFrame, in_df_edge_seg_ordered:pd.DataFrame,
    in_str_id_tazRel:str = "car", in_str_sim_st:str = "0", in_str_sim_end:str = "2:0:0",
    in_fl_sim_step:float = 1.0, in_str_path_net:str = "data_sumo/mmv3.net.xml",
    in_str_path_taz:str = "data_sumo/taz_edges.taz.xml", in_str_path_vType:str = "./data_sumo/vehicleType.vType.xml",
    in_str_dir_sumo_tmp = "./data_sumo/tmp", in_str_dir_edgeInfo:str = "./data_sumo/tmp_edgeInfo"
) -> pd.DataFrame:
    
    # Initialize temporary folders.
    delAllInDir(in_str_dir_sumo_tmp)
    delAllInDir(in_str_dir_edgeInfo)
    
    # Create tazRel file in temporary directory.
    str_path_tazRel = createTazRel(
        in_str_dir_sumo_tmp, in_str_id_tazRel, in_str_sim_st,
        in_str_sim_end, in_df_perturbed_od
    )
    # Create odtrips.xml file.
    lv_suc_odtrips, str_path_odtrips = createOdTrips(
        in_str_dir_sumo_tmp, in_str_path_taz, str_path_tazRel
    )
    # Check if odtrips file has been successfully created.
    if lv_suc_odtrips != 0:
        print(f"    Error on odtrips generation! Proc_{in_int_proc_num}_Iter_{in_int_iter}")
        return None
    
    # Create rou.xml (Route) file.
    lv_suc_rou, str_path_rou = createRoute(
        in_str_dir_sumo_tmp, in_str_path_net, str_path_odtrips, in_str_path_vType
    )
    
    # Check if route file has been successfully created.
    if lv_suc_rou != 0:
        print(f"    Error on route generation! Proc_{in_int_proc_num}_Iter_{in_int_iter}")
        return None
    
    # Define link flow output file path.
    str_edgeInfo_id = "edgeInfo"
    str_edgeInfo_fName = "edgeInfo.xml"
    str_path_edgeInfo = os.path.join(os.path.abspath(in_str_dir_edgeInfo), str_edgeInfo_fName)
    
    # Define edgeInfo.additional.xml file.
    str_path_edgeInfoAdd = createAddEdgeInfo(in_str_dir_sumo_tmp, str_edgeInfo_id, str_path_edgeInfo)
    print(f"    All temporary files are ready for simulation. Proc_{in_int_proc_num}_Iter_{in_int_iter}")
    
    # Run simulation.
    str_command_sim_tmp = "sumo -n {} -r {} -b 0 --step-length {} -v False --no-step-log True --no-warnings True --additional-files {}".format(
        in_str_path_net, str_path_rou, in_fl_sim_step, str_path_edgeInfoAdd
    )
    lv_suc_sim = os.system(str_command_sim_tmp)
    
    if lv_suc_sim != 0:
        print(f"    Error on SUMO simulation! Proc_{in_int_proc_num}_Iter_{in_int_iter}")
        return None
    
    print(f"    SUMO Simulation done! Proc_{in_int_proc_num}_Iter_{in_int_iter}")
    
    # Read output edgeInfo file and convert it into dataframe format.
    df_flow_raw = xml2df_edge_flow_v2(str_path_edgeInfo)
    df_flow = seg_edge_ordered_flow(in_df_edge_flow_raw= df_flow_raw, in_df_edge_seg_ordered= in_df_edge_seg_ordered)
    
    # Initialize temporary folders.
    delAllInDir(in_str_dir_sumo_tmp)
    delAllInDir(in_str_dir_edgeInfo)
    
    # Return output dataframe.
    return df_flow