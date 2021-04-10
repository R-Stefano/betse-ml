import generate.configs as configs
import yaml
import random


with open(configs.defaultSimConfigFile, 'r') as stream:
	default_configs = yaml.safe_load(stream)

def init():
    default_configs['init time settings']['time step'] = configs.initialization_timestep
    default_configs['init time settings']['total time'] = configs.initialization_duration_s
    default_configs['init time settings']['sampling rate'] = configs.initialization_sampling_rate

    default_configs['sim time settings']['time step'] = configs.simulation_timestep
    default_configs['sim time settings']['total time'] = configs.simulation_duration_s
    default_configs['sim time settings']['sampling rate'] = configs.simulation_sampling_rate

    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)

def sample_seed_config():
    '''
    Called to sample different configs for the seed phase (phase 1)
    '''

    extracellularNaConcentration = 1.0 #random.randint(1, 200)
    extracellularKConcentration = 1.0 #random.randint(1, 200)
    cytosolicNaConcentrationRatio = 200.0
    cytosolicKConcentrationRatio = 1.0

    default_configs['general options']['customized ion profile']['extracellular Na+ concentration'] =  extracellularNaConcentration 
    default_configs['general options']['customized ion profile']['extracellular K+ concentration'] =  extracellularKConcentration
    default_configs['general options']['customized ion profile']['extracellular Cl- concentration'] =  1 #105.0 #random.randint(1, 200)
    default_configs['general options']['customized ion profile']['extracellular Ca2+ concentration'] =  1 #random.randint(1, 10)
    default_configs['general options']['customized ion profile']['extracellular protein- concentration'] =  80.0

    default_configs['general options']['customized ion profile']['cytosolic Na+ concentration'] = extracellularNaConcentration *  cytosolicNaConcentrationRatio
    default_configs['general options']['customized ion profile']['cytosolic K+ concentration'] = extracellularKConcentration * cytosolicKConcentrationRatio
    default_configs['general options']['customized ion profile']['cytosolic Cl- concentration'] = 1 #random.randint(1, 200)
    default_configs['general options']['customized ion profile']['cytosolic Ca2+ concentration'] = 1 #random.randint(1, 10)
    default_configs['general options']['customized ion profile']['cytosolic protein- concentration'] = 80.0

    with open('./generate/simulator/sim_config.yml', 'w') as outfile:
        yaml.dump(default_configs, outfile, default_flow_style=False)
        
def sample_init_config():
    '''
    Called to sample different configs for the init phase (phase 2)
    1. Sample default membran permeability parameter (1.0e-17 - 9.0e-18)
    2. Edit Na permeability to set different "background initial Vmems" for the whole population (50% - 90% of default value)
    3. Setup spot

    - Define the Spot for the simulation:
        1. Sample Spot shape from lists of available spots
        2. Assign by default the Mmembrane permeability params of the all population
        3. Sample the depolarization values
        4. Set the sampled depolarization value to the profile selected membrane type permeability
    '''

    defaultVmemPerm = sample_diffusion_parameter()
    defaultNaVmemPerm = defaultVmemPerm * 0.1 #* random.uniform(0.5, 0.9)
    defaultKVmemPerm = defaultVmemPerm  #* random.uniform(0.5, 0.9)
    default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_Na'] = defaultNaVmemPerm  # Na+ membrane diffusion constant [m2/s]
    default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_K'] =  defaultKVmemPerm    # K+ membrane diffusion constant [m2/s]
    default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_Cl'] = defaultVmemPerm    # Cl- membrane diffusion constant [m2/s]
    default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_Ca'] = defaultVmemPerm    # Ca2+ membrane diffusion constant [m2/s]
    default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_M'] =  defaultVmemPerm 
    default_configs['tissue profile definition']['tissue']['default']['diffusion constants']['Dm_P'] = 0         

    # ----------------------------------------------------
    # DEFINE SPOT & Polarization
    # ----------------------------------------------------
    spotShape = random.sample([
        'geo/circle/spot.png',
        'geo/circle/spot_1.png',
        'geo/circle/spot_2.png',
        'geo/circle/spot_3.png', 
    ], 1)[0]
    '''
    NOT USING YET. POTENTIALLY LATER ON
    'geo/circle/bottom_pole.png', 
    'geo/circle/mini_spot.png',
    'geo/circle/mini_wedge.png',
    'geo/circle/poles.png',
    'geo/circle/tissue_A.png',
    'geo/circle/tissue_B.png',
    'geo/circle/top_pole.png',
    'geo/circle/wedge.png'
    '''
    profile = {
        'name': 'Spot',
        'insular': False,
        'diffusion constants': {
            'Dm_Na': defaultNaVmemPerm,     # Na+ membrane diffusion constant [m2/s]
            'Dm_K':  defaultKVmemPerm,      # K+ membrane diffusion constant [m2/s]
            'Dm_Cl': defaultVmemPerm,     # Cl- membrane diffusion constant [m2/s]
            'Dm_Ca': defaultVmemPerm,     # Ca2+ membrane diffusion constant [m2/s]
            'Dm_M':  defaultVmemPerm,      # M- membrane diffusion constant [m2/s]
            'Dm_P': 0.0          # proteins membrane diffusion constant [m2/s]
        },
        'cell targets': {'type': 'image', 'color': 'ff0000', 'image': spotShape, 'indices': [3, 14, 15, 9, 265], 'percent': 50}
    }
    vmemState = "depolarization"
    multipliers = [i + 1 for i in range(20)]
    if (vmemState == "depolarization"):
        poolDepolarizations = []
        for membraneType in ['Dm_Cl']:#['Dm_Na', 'Dm_K']:
            for multiplier in multipliers:
                if (membraneType in ["Dm_K", 'Dm_Cl']):
                    #CLOSE
                    poolDepolarizations.append({
                        membraneType: profile['diffusion constants'][membraneType] / multiplier
                    })
                else:
                    #OPEN
                    poolDepolarizations.append({
                        membraneType: profile['diffusion constants'][membraneType] * multiplier
                    })
        sampledDepolarization = random.sample(poolDepolarizations, 1)[0]
        membraneType = list(sampledDepolarization.keys())[0]
        print("Membrane {} changed from {} -> {}".format(membraneType, profile['diffusion constants'][membraneType], sampledDepolarization[membraneType]))
        profile['diffusion constants'][membraneType] = sampledDepolarization[membraneType]

    default_configs['tissue profile definition']['tissue']['profiles'] = [profile]

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
        default_configs['change Na env']['change start'] = int_s            # sim time to start change [s]
        default_configs['change Na env']['change finish'] = int_end         # sim time to end change and return to original [s]
        default_configs['change Na env']['change rate'] = freq_change       # rate of change [s]
        default_configs['change Na env']['multiplier']=  change_multiplier   # factor to multiply base level
    default_configs['change Na env']['event happens'] = changeNa # turn the event on (True) or off (False)

    ## Change the environmental concentration of K+
    changeK = (sampledIntervantionType == 'K') and globalInterventions
    if (changeK and globalInterventions):
        int_s, int_end, freq_change, change_multiplier = sample_intervantion_params()
        default_configs['change K env']['change start'] = int_s         # time to start change [s]
        default_configs['change K env']['change finish'] = int_end        # time to end change and return to original [s]
        default_configs['change K env']['change rate'] = freq_change           # rate of change [s]
        default_configs['change K env']['multiplier'] = change_multiplier            # factor to multiply base level

    default_configs['change K env']['event happens'] = changeK # turn the event on (True) or off (False)

    # ----------------------------------------------------
    # TARGETED INTERVENTIONS
    # ----------------------------------------------------

    sampledIntervantionType = random.choice(configs.interventionTypes)

    ## Change Na Perm for Spot selected
    changeNa = (sampledIntervantionType == 'Na') and targetedInterventions
    if (changeNa):
        int_s, int_end, freq_change, change_multiplier = sample_intervantion_params()
        default_configs['change Na mem']['change start'] = int_s           # sim time to start change [s]
        default_configs['change Na mem']['change finish'] = int_end         # sim time to end change and return to original [s]
        default_configs['change Na mem']['change rate'] = freq_change            # rate of change [s]
        default_configs['change Na mem']['multiplier']= change_multiplier             # factor to multiply base level
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

    freq_change = random.sample([0.1, 0.5, 1.0], 1)[0]
    change_multiplier = random.sample([1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0], 1)[0]

    return int_s, int_end, freq_change, change_multiplier


def sample_diffusion_parameter():
    defaultDiffusion = 1.0e-18
    return defaultDiffusion