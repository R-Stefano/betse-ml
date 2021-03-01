import os 
import yaml
import generate.simApi as simApi
import random
import time

def run():
    '''
    1. Load configs
    2. RUN N Times 

    For each run:
        1. Sample configs seed phase 
        2. Run sim phase using command line
        3. Sample configs for init phase
        4. Run init phase using command line
        5. Sample configs for sim phase
        6. Run simulation phase using command line
        7. Run plot using command line
        8. Move simulation results data to storage folder
        
    TODO:
     - Move these to a config file and pass it line run(configs):
    '''
    BETSE_SIM_RESULTS_PATH = "generate/simulator/"
    BETSE_SIM_VMEM_RESULTS = BETSE_SIM_RESULTS_PATH + "RESULTS/sim_1/Vmem2D_TextExport/"
    RUNS = 10
    RESULTS_DIR = "storage/raw/"
    NEXT_RUN_IDX = len(os.listdir(RESULTS_DIR))
    MIN_SIM_RUNS = 5
    MAX_SIM_RUNS = 20

    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)


    print("Starting from run", NEXT_RUN_IDX)
    for runIdx in range(RUNS):
        with open("log.txt", "a") as logger:
            logger.write("RUN {}\n".format(NEXT_RUN_IDX))
            # 
            # Config BETSE Simulation Environment (seed phase)
            #
            run_start = time.time()
            simApi.sample_seed_config()
            os.system('betse seed generate/simulator/sim_config.yml')
            logger.write(">>SEED: took {:.2f} s\n".format(time.time() - run_start))

            #
            # INITIALIZATION
            #
            init_start = time.time()
            simApi.sample_init_config()
            os.system('betse init generate/simulator/sim_config.yml')
            logger.write(">>INIT: took {:.2f} s\n".format(time.time() - init_start))

            #
            # SIMULATION
            #
            _sim_runs = random.sample([i for i in range(MIN_SIM_RUNS, MAX_SIM_RUNS)], 1)[0]
            print("RUN {} SIMULATIONS WITH SAME INITIALIZATION".format(_sim_runs))
            for i in range(_sim_runs):

                sim_start = time.time()
                simApi.sample_sim_config()

                os.system('betse sim generate/simulator/sim_config.yml')
                os.system('betse plot sim generate/simulator/sim_config.yml') # Save sim results

                #
                # Generate folder to store data for the current ended Run.
                #
                run_directory = RESULTS_DIR + str(NEXT_RUN_IDX) + "/"
                os.makedirs(run_directory)

                ### 1. Move Simulation data to the run folder just created 
                for sample_filename in os.listdir(BETSE_SIM_VMEM_RESULTS):
                    os.replace(BETSE_SIM_VMEM_RESULTS + sample_filename, run_directory + sample_filename)
                ### 2. Save Config yaml file
                os.system('cp ' + BETSE_SIM_RESULTS_PATH + 'sim_config.yml' + ' ' + run_directory + 'configs.yml')

                logger.write(">>SIMU: took: {:.2f} s\n".format(time.time() - sim_start))

                NEXT_RUN_IDX += 1