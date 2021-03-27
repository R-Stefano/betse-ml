import generate.configs as configs
import yaml
import random


with open(configs.defaultSimConfigFile, 'r') as stream:
	default_configs = yaml.safe_load(stream)

def init():
    default_configs['sim time settings']['time step'] = configs.simulation_timestep
    default_configs['sim time settings']['total time'] = configs.simulation_duration_s
    default_configs['sim time settings']['sampling rate'] = configs.simulation_sampling_rate

    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)

def sample_seed_config():
    '''
    Called to sample different configs for the seed phase (phase 1)
    '''

    default_configs['general options']['customized ion profile']['extracellular Na+ concentration'] =  random.randint(1, 200)
    default_configs['general options']['customized ion profile']['extracellular K+ concentration'] =  random.randint(1, 200)
    default_configs['general options']['customized ion profile']['extracellular Cl- concentration'] =  random.randint(1, 200)
    default_configs['general options']['customized ion profile']['extracellular Ca2+ concentration'] =  random.randint(1, 10)
    default_configs['general options']['customized ion profile']['extracellular protein- concentration'] =  random.randint(1, 100)

    default_configs['general options']['customized ion profile']['cytosolic Na+ concentration'] = random.randint(1, 200)
    default_configs['general options']['customized ion profile']['cytosolic K+ concentration'] = random.randint(1, 200)
    default_configs['general options']['customized ion profile']['cytosolic Cl- concentration'] = random.randint(1, 200)
    default_configs['general options']['customized ion profile']['cytosolic Ca2+ concentration'] = random.randint(1, 10)
    default_configs['general options']['customized ion profile']['cytosolic protein- concentration'] = random.randint(1, 200)

    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)
        
def sample_init_config():
    '''
    Called to sample different configs for the init phase (phase 2)
    '''

    #default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_Na'] = sample_diffusion_parameter()  # Na+ membrane diffusion constant [m2/s]
    #default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_K'] = sample_diffusion_parameter()  # K+ membrane diffusion constant [m2/s]
    #default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_Cl'] = sample_diffusion_parameter()  # Cl- membrane diffusion constant [m2/s]
    #default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_Ca'] = sample_diffusion_parameter()  # Ca2+ membrane diffusion constant [m2/s]
    #default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_M'] = sample_diffusion_parameter()  # M- membrane diffusion constant [m2/s]
    #default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_P'] = sample_diffusion_parameter()  # proteins- membrane diffusion constant [m2/s]

    # ----------------------------------------------------
    # DEFINE INTERVENTIONS SPOT
    # ----------------------------------------------------

    print("tissue profiles:")
    print(default_configs['tissue profile definition']['tissue']['profiles'])

    newProfiles = []
    for profile in default_configs['tissue profile definition']['tissue']['profiles']:
        if (profile['name'] == 'Spot'):
            newProfiles.append({
                'name': 'Spot',
                'insular': False,
                'diffusion constants': {
                    'Dm_Na': 1.0e-18,     # Na+ membrane diffusion constant [m2/s]
                    'Dm_K': 1.0e-18,      # K+ membrane diffusion constant [m2/s]
                    'Dm_Cl': 1.0e-18,     # Cl- membrane diffusion constant [m2/s]
                    'Dm_Ca': 1.0e-18,     # Ca2+ membrane diffusion constant [m2/s]
                    'Dm_M': 1.0e-18,      # M- membrane diffusion constant [m2/s]
                    'Dm_P': 0.0          # proteins membrane diffusion constant [m2/s]
                },
                'cell targets': {'type': 'image', 'color': 'ff0000', 'image': 'geo/circle/spot_3.png', 'indices': [3, 14, 15, 9, 265], 'percent': 50}
            })
        else:
            newProfiles.append(profile)
    default_configs['tissue profile definition']['tissue']['profiles'] = newProfiles

    print(default_configs['tissue profile definition']['tissue']['profiles'])


    '''
    profiles: # List of all non-default tissue profiles. Ignored if "profiles enabled" is False.
      # Example tissue profile for a depolarized patch of cells at the cell cluster centre.
    - 
    '''
    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)
    

def sample_sim_config():
    '''
    Called to sample different configs for the sim phase (phase 3)

    Global Interventions: 
     - Changes to globally-applied simulation variables such as membrane permeabilities, pump and gap junction function and environmental concentrations of ions

    '''
    globalInterventions = configs.globalInterventions
    targetedInterventions = configs.targetedInterventions

    # ----------------------------------------------------
    # GLOBAL INTERVENTIONS
    # ----------------------------------------------------

    sampledIntervantionType = random.choice(configs.interventionTypes)

    ## Change the environmental concentration of Na
    changeNa = (sampledIntervantionType == 'Na') and globalInterventions
    if (changeNa):
        print("\n\GLOBAL INTERVENTION NA\n\n")
        int_s, int_end, freq_change, change_multiplier = sample_intervantion_params()
        default_configs['change Na env']['change start'] = 1# int_s            # sim time to start change [s]
        default_configs['change Na env']['change finish'] = 9# int_end         # sim time to end change and return to original [s]
        default_configs['change Na env']['change rate'] = 1# freq_change       # rate of change [s]
        default_configs['change Na env']['multiplier']= 25# change_multiplier   # factor to multiply base level
    default_configs['change Na env']['event happens'] = changeNa # turn the event on (True) or off (False)

    '''
    ## Change the environmental concentration of K+
    changeK = random.choice([True, False])
    if (changeK and globalInterventions):
        int_s, int_end, freq_change, change_multiplier = sample_intervantion_params()
        default_configs['change K env']['change start'] = int_s         # time to start change [s]
        default_configs['change K env']['change finish'] = int_end        # time to end change and return to original [s]
        default_configs['change K env']['change rate'] = freq_change           # rate of change [s]
        default_configs['change K env']['multiplier'] = change_multiplier            # factor to multiply base level

    default_configs['change K env']['event happens'] = changeK # turn the event on (True) or off (False)

    ## Change the environmental concentration of Cl
    changeCl = random.choice([True, False])
    if (changeCl and globalInterventions):
        int_s, int_end, freq_change, change_multiplier = sample_intervantion_params()
        default_configs['change Cl env']['change start'] = int_s           # sim time to start change [s]
        default_configs['change Cl env']['change finish'] = int_end         # sim time to end change and return to original [s]
        default_configs['change Cl env']['change rate'] = freq_change            # rate of change [s]
        default_configs['change Cl env']['multiplier']= change_multiplier             # factor to multiply base level
    default_configs['change Cl env']['event happens'] = changeCl # turn the event on (True) or off (False)

    ## Change the environmental temperature
    changeTemp = random.choice([True, False])
    if (changeTemp and globalInterventions):
        int_s, int_end, freq_change, change_multiplier = sample_intervantion_params()
        default_configs['change temperature']['change start'] = int_s           # sim time to start change [s]
        default_configs['change temperature']['change finish'] = int_end         # sim time to end change and return to original [s]
        default_configs['change temperature']['change rate'] = freq_change            # rate of change [s]
        default_configs['change temperature']['multiplier']= change_multiplier             # factor to multiply base level
    default_configs['change temperature']['event happens'] = changeTemp # turn the event on (True) or off (False)

    ## Block Gap Junctions between cells
    blockGJ = random.choice([True, False])
    if (blockGJ and globalInterventions):
        int_s, int_end, freq_change, _ = sample_intervantion_params()
        default_configs['block gap junctions']['change start'] = int_s           # sim time to start change [s]
        default_configs['block gap junctions']['change finish'] = int_end         # sim time to end change and return to original [s]
        default_configs['block gap junctions']['change rate'] = freq_change            # rate of change [s]
        default_configs['block gap junctions']['random fraction']= random.randint(0,100)          # percentage of gap junctions randomly targeted
    default_configs['block gap junctions']['event happens'] = blockGJ # turn the event on (True) or off (False)

    ## Block cells NaKATP pump
    blockNaKATPPump = random.choice([True, False])
    if (blockNaKATPPump and globalInterventions):
        int_s, int_end, freq_change, _ = sample_intervantion_params()
        default_configs['block NaKATP pump']['change start'] = int_s           # sim time to start change [s]
        default_configs['block NaKATP pump']['change finish'] = int_end         # sim time to end change and return to original [s]
        default_configs['block NaKATP pump']['change rate'] = freq_change            # rate of change [s]
    default_configs['block NaKATP pump']['event happens'] = blockNaKATPPump # turn the event on (True) or off (False)
    '''
    # ----------------------------------------------------
    # TARGETED INTERVENTIONS
    # ----------------------------------------------------

    sampledIntervantionType = random.choice(configs.interventionTypes)

    ## Change Na Perm for Spot selected
    changeNa = (sampledIntervantionType == 'Na') and targetedInterventions
    if (changeNa):
        print("\n\nSPOT INTERVENTION NA\n\n")
        int_s, int_end, freq_change, change_multiplier = sample_intervantion_params()
        default_configs['change Na mem']['change start'] = 1 #int_s           # sim time to start change [s]
        default_configs['change Na mem']['change finish'] = 10# int_end         # sim time to end change and return to original [s]
        default_configs['change Na mem']['change rate'] = 1# freq_change            # rate of change [s]
        default_configs['change Na mem']['multiplier']= 10 #change_multiplier             # factor to multiply base level
    default_configs['change Na mem']['event happens'] = changeNa # turn the event on (True) or off (False)

    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)


# --------------------------------------
# INTERNAL FUNCTIONS
# --------------------------------------
def sample_intervantion_params():
    # function used to sample the interventions params fo rthe different configs
    int_s = random.sample([i for i in range(int(configs.simulation_duration_s))], 1)[0]
    max_duration = int(configs.simulation_duration_s) - int_s
    int_end = int_s + random.sample([i + 1 for i in range(max_duration)], 1)[0]

    freq_change = random.sample([0.1, 0.5, 1.0, 2.0], 1)[0]
    change_multiplier = random.sample([0.5, 1.0, 5.0, 10.0], 1)[0] #50.0, 100.0

    return int_s, int_end, freq_change, change_multiplier


def sample_diffusion_parameter():
    available_diffusions = [
        0.0,
        1.0e-18,
        2.0e-18,
        5.0e-18,
        1.0e-17
    ]
    return random.sample(available_diffusions, 1)[0]