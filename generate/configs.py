import os

defaultSimConfigFile = "./generate/default.sim_config.yml"
bucketName = "betse-ml"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './generate/generate-worker.json'

SIM_RUNS = 50000
MIN_SIM_RUNS = 2
MAX_SIM_RUNS = 5
useCloud = True

initialization_timestep = 1.0e-3
initialization_duration_s = 10.01 # 60.01
initialization_sampling_rate = 5 #simulation_duration_s - 0.01

simulation_timestep = 1.0e-3
simulation_duration_s = 30.01 # 60.01
simulation_sampling_rate = 5 #simulation_duration_s - 0.01

sampleConcentrations = True
sampleMemPermeabilities = True
possibleSpotStatus = ['normal', 'hyperpolarized', 'depolarized']
interventionTypes = ['Na', 'K'] #['Na', 'Cl', 'K', 'temperature', 'blockGJ', 'blockNaKATP']
globalInterventions = False
targetedInterventions = True
