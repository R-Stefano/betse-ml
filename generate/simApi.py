import generate.configs as configs
import yaml



with open(configs.defaultSimConfigFile, 'r') as stream:
	default_configs = yaml.safe_load(stream)
        
def sample_seed_config():
    '''
    Called to sample different configs for the seed phase (phase 1)
    '''
    default_configs['sim time settings']['time step'] = configs.simulation_timestep
    default_configs['sim time settings']['total time'] = configs.simulation_duration_s
    default_configs['sim time settings']['sampling rate'] = configs.simulation_sampling_rate

    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)
        
def sample_init_config():
    '''
    Called to sample different configs for the init phase (phase 2)
    '''
    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)
    

def sample_sim_config():
    '''
    Called to sample different configs for the sim phase (phase 3)
    '''
    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)


'''
    
########## INTERNAL FUNCTIONS
def sample_intervantion_params():
    # function used to sample the interventions params fo rthe different configs
    int_s = random.sample([i for i in range(int(configs.simulation_duration_s))], 1)[0]
    max_duration = int(configs.simulation_duration_s) - int_s
    int_end = int_s + random.sample([i + 1 for i in range(max_duration)], 1)[0]

    freq_change = random.sample([0.1, 0.5, 1.0, 5.0], 1)[0]
    change_multiplier = random.sample([0.5, 1.0, 5.0, 10.0, 20.0, 50.0, 100.0], 1)[0]

    return int_s, int_end, freq_change, change_multiplier

'''