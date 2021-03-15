import os

defaultSimConfigFile = "./generate/default.sim_config.yml"
bucketName = "betse-ml"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './generate/generate-worker.json'

simulation_timestep = 1.0e-3
simulation_duration_s = 60.01 # 60.01
simulation_sampling_rate = 5 #simulation_duration_s - 0.01

SIM_RUNS = 500
MIN_SIM_RUNS = 1
MAX_SIM_RUNS = 5