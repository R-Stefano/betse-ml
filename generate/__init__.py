import os, yaml,random, time, gzip, pickle, uuid
import generate.simApi as simApi
import generate.configs as configs
from google.cloud import storage
storage_client = storage.Client()
bucket = storage_client.bucket(configs.bucketName)

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
     - Cycle through samples for init phase as well -> What configs can we change in the init phase?
    '''
    BETSE_SIM_RESULTS_PATH = "generate/simulator/"
    BETSE_SIM_VMEM_RESULTS = BETSE_SIM_RESULTS_PATH + "RESULTS/sim_1/Vmem2D_TextExport/"
    RUNS = configs.SIM_RUNS
    RESULTS_DIR = "storage/raw/"
    NEXT_RUN_IDX = len(os.listdir(RESULTS_DIR))
    MIN_SIM_RUNS = configs.MIN_SIM_RUNS
    MAX_SIM_RUNS = configs.MAX_SIM_RUNS

    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    print("Starting from run", NEXT_RUN_IDX)
    while (RUNS > 0):
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
            _sim_runs = random.sample([i for i in range(MIN_SIM_RUNS, MAX_SIM_RUNS + 1)], 1)[0]
            print("RUN {} SIMULATIONS WITH SAME INITIALIZATION".format(_sim_runs))
            for i in range(_sim_runs):
                print("\n\nRUN {} | LEFT {}\n\n".format(NEXT_RUN_IDX, RUNS))
                sim_start = time.time()
                simApi.sample_sim_config()

                try:
                    os.system('betse sim generate/simulator/sim_config.yml')
                    os.system('betse plot sim generate/simulator/sim_config.yml') # Save sim results
                except:
                    print("\n\nHELLOOO SIMUATION FAILED PORCODIO\n\n")
                #
                # Generate folder to store data for the current ended Run.
                #
                run_directory = RESULTS_DIR + str(uuid.uuid4()) + "/"
                os.makedirs(run_directory)

                ### 1. Move Simulation data to the run folder just created 
                for sample_filename in os.listdir(BETSE_SIM_VMEM_RESULTS):
                    _save(BETSE_SIM_VMEM_RESULTS + sample_filename, run_directory + sample_filename)
                ### 2. Save Config yaml file
                _save(BETSE_SIM_RESULTS_PATH + 'sim_config.yml', run_directory + 'configs.yml')
                ### 3. Save cells verts
                with gzip.open(BETSE_SIM_RESULTS_PATH + "SIMS/sim_1.betse.gz", "rb") as f:
                    sim, cells, params = pickle.load(f)

                with open(BETSE_SIM_RESULTS_PATH + 'SIMS/cells.pkl', 'wb') as fp:
                    pickle.dump({'cell_verts': cells.cell_verts, 'xmin': cells.xmin, 'xmax': cells.xmax, 'ymin': cells.ymin, 'ymax': cells.ymax}, fp)
                _save(BETSE_SIM_RESULTS_PATH + 'SIMS/cells.pkl', run_directory + 'cells.pkl')

                logger.write(">>SIMU: took: {:.2f} s\n".format(time.time() - sim_start))

                RUNS -= 1
                NEXT_RUN_IDX += 1

                if (RUNS <= 0):
                    break


def _save(source_filename, destination_filename):
    useCloud = True
    if (useCloud):
        blob = bucket.blob(destination_filename)
        blob.upload_from_filename(source_filename)
    else:
        os.replace(source_filename, destination_filename)