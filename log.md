# Scope

We are trying to use ML to simulate a multiphysics engine simulator. 

## Requirements
- data
- model
- evaluation

## Data

The task is going to be a supervised task. The model has a input and a output.

The input is a Vmem pattern and the simulation configuration settings. 

The output is going to be a new Vmem pattern after some time in the future.

### Data Collection

Data we need:
- Initial Vmem
- Configuration file
- Final Vmem 

The BETSE simulation results are saved in a folder called `sample_sim`. 

#### Vmem
The Vmem values for each cell at each timestep are stored in the folder 
`sample_sim/RESULTS/sim_1/Vmem2D_TextExport/`

We need the csv file at timestep 0 and at the final timestep

#### Configuration file
The configuration file is available in `sample_sim/sample_sim.yaml`

### Script
The script for collecting data will run BETSE N times in order to generate a dataset of N examples.
Each example will consists of Vmem at T=0, Vmem at final timestep and the simulation configuration.

So the script, at the end of each simulation it has to extract the above data and save it somewhere.

However using the default settings by calling 
```
betse -v try
```

BETSE required 79.72 s for one run which consists of seed, init and a simulation of 0.04 s real-time with timestemps of size 0,001. 
Resulting in an average of  2.4 s per timestep.

We need to find a way to reduce the time required for one run.

#### Script optimization
In order to customize the simulation, we have to generate a custom config file by runnning the command
```
betse config my_sim/sim_config.yml
```

This will generate a sim_config.yml file in my_sim folder. 

BETSE allow to run the seed, init and sim processes separatly. Maybe, we can reuse some of these processes for some runs
in this way reducing the run time. 


- Disable plots
- Disable not essential write on disk: writing on disk only at the end. Set config timestep equal to simulation length. Write on disk only essential: Vmem
- Reuse initialization when possible (IS THIS POSSIBLE AT ALL?)

# Journey
## Before
- script to auto-extract data for training
- Speed up: remove parts of the simulation we don't care

*How to sample from the simulation the Vmems?*
Set `sampling rate` 0.1s less than the simulation time, allows to write on disk only at the beginning of the sim and and the end. Reducing write on disks which slow down sim time.

*How do we build a dataset with enough variance?*
We have to change the BETSE configs file at each run. By avoiding to run  *seed* and *init* steps at each run but only editing the sim configs. We can increase variance and reduce simulation time.

## 30/11
- Was missing sampled data at timestep 0. Had to go throught the code base and add it manually because the simulation doesn't allow it. 
- Added logic for editing BETSE config file only before simulation phase.  

*What params can be edited at the sim phase without affecting seed and init phases and so breaking BETSE?*
- **Targeted Interventions:** Targeted interventions are scheduled changes that can be applied to SPECIFIC cells in the cluster by linking to a defined tissue profile.
- **Global Interventions:** Schedule changes to globally-applied simulation variables such as membrane permeabilities, pump and gap junction function and environmental concentrations of ions.

*What params to tune at each run is better to start with?*
Probably global interventions. Probably environmental concentrations of ions simulating drugs intervations 

## 01/12
- Check if sim is deterministic. Yes it is. Running two times the simulation phase with the same settings returns the same results. 
- Logic to edit global interventions between runs
- Logic to edit targeted interventations ( TO BE TESTED YET)

*Comments*
I have noticed that by applying global interventions to K concentration, the K change across the simulation is very small compared to the initial conditions. 
Maybe the intervention prevents the concentration to change due to the wounden. Same when there is no intervantion. The change in average concentration is very small. Probably, due to the simulation time??
Does it really matter? Because still the cells Vmems at the end of the simulation differs a lot although the simulationssays that the average concentration remains basically the same.

## 02/12
- Design dataset generation: extracted Vmems. Created Data Loader: batch & shuffle already

*Design dataset generation*
Folders structure
```
data/
|-- raw/
|-- processed/
    |-- train/
    |-- validation/
```

At the moment, the simulations failed are skipped and not added to the processed folder.

## 03/12
- Add BETSE configs values. Basics like simulation duration + global intervention configs (ones used)
- Padded Vmem lists
- Design a first ML model

*How should I handle when event is false?*
Should I feed the values in the config file or should I set them to 0 or -1?
At the moment keep the values. The event is active entry: 1/0 tells the model if considering the data already

*How should I handle the event start and finish?*
SHould I use the default values or set them relative to the duration of the simulation?
atm start with default values

*comments*
- Model on all the examples can overfit. Probably due to the error type. Consider to move from MSE to CrossEntropy
- Need validation set to when interrupting training. Need to update the raw data generation process and add the dataset to the training file
- Design the post training. Analysis in Jupyter probably. Check on google cool analysis. Ask questions  

## 07/12
- Split data between training and validation. Use folders names as splitter. 

## TODAY
- Display Vmem as in the simulation for later testing

**SimPhase Obj** Where do I get it? Probably the pickle file saved at the end of the simulation. Just pass it to the function
**SimConfExportPlotCells** Is a config file containing, in this case only the color min and max values. So basically useless CAN BE REMOVED once found those values

*Is it possible to remove dependency from the pickle file?*
Hardcoding all values except the Vmems which are coming from the sim and the model

Need to setup a comparison between the real end Vmem and the one predicted. 
In order to do it, I need the geometry of the cells in the simulation which is availabel in the pickle .beste file. 
So, I have to 
1) Save the pickle betse during the data mining process
2) Some intermediary Vmems as well (like every second?)
3) Develop the code to show side by side the final Vmem and the final Vmem predicted

The only information that is missing in the Vmem csvs is the cells geometry. So, I may extract only the cells geometry from the pickle file in order to avoid to save MBs for each simulation

# TODO
- Change initial concentrations. This can be done before init phase only
- Investigate why and how exactly should we treat the problem as a classification one: predicts a discrete probability distribution

#
### Notes:
- The number of cells in the Vmem.csv file is not constant. It changes every run -> check max number of cells in vmem file
- What shapes we should simulate on, worm?? -> To start I woudl do it on hexagon size
- Does the sim_1 results refers to the wounden simulation??? Looks like
- The change in concentration, for example K, over a simulation of 10s. Is very small even with intervention. Is it a problem?
- Consider to extract multiple Vmems from the simulation to test for eadvanced networks that "reason"
- Consider saving the betse file. It contains the Vmems and many more info that can be used for the plots for example
- Handle when simulaiton becomes instable. It generates an incomplete datapoint. Maybe use it as well??