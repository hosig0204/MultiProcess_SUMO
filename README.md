# Multiprocessing SUMO (Simulation of Urban MObility)

## 1. Introduction
This repository is aimed to execute the transport simulator SUMO (Simulation of Urban MObility) in multiple CPU cores parallelly <a href= "https://sumo.dlr.de/docs/index.html"> (LINK for SUMO)</a>. You may save simulation time by utilizing many logical cores in your CPU. Munich mortorway network (post-processed) is provided as an example.

## 2. Workflow
All notebooks and python files are labelled by alphabets, you should follow those orders for workflow execution. It is assumed that you are already familiar essential prerequisites such as the SUMO, Python-Multiprocessing, Pandas and Numpy.
+ Workflow [ a ]: In here, you should edit your SUMO network file and produce edge information dataframe file. Influx and outlux edges must be separated!
+ Workflow [ b ]: In here, duplicated edge ids in the edge_info dataframe are cleaned up.
+ Workflow [ c ]: | Multiprocessing | By using 70% of your CPU logical cores, adjacency list is created from the edge_info dataframe.
+ Workflow [ d ]: In here, your edges will be aggregated if possible. Some connected interim edges will be grouped so that they can be considered as one edge. Then, possible OD (Origin-Destination) pairs will be recorded by pathfinder logic.  
+ Workflow [ e ]: In here, sample OD matrices are populated in random manner.
+ Workflow [ f ]: | Multiprocessing | With defined core numbers, multiple SUMO simulations are conducted parallelly. This multiprocessing task stops once all sample OD matrices are simulated.