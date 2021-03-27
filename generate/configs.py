import os

defaultSimConfigFile = "./generate/default.sim_config.yml"
bucketName = "betse-ml"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './generate/generate-worker.json'

SIM_RUNS = 500
MIN_SIM_RUNS = 1
MAX_SIM_RUNS = 5
useCloud = True

simulation_timestep = 1.0e-3
simulation_duration_s = 60.01 # 60.01
simulation_sampling_rate = 5 #simulation_duration_s - 0.01

sampleSeedPhase = True
sampleInitPhase = True
globalInterventions = False
targetedInterventions = True
interventionTypes = ['Na', 'Cl', 'K', 'temperature', 'blockGJ', 'blockNaKATP']
