'''
This is the main file where the program starts

TODO:
    - simulation recording only 5.0s and 10.0s. Need 0.0s or something like that
    
    [FEATURES]
    - list of actions to execute. First ask all questions (like a config)
'''
import sys

sys.path.append("./betse/")

#ENV CONFIGURATIONS
import random, os
random.seed(0)

print(sys.argv)

##################à
#   CREATE FOLDERS
##################

if not os.path.exists('generate/simulator'):
    os.makedirs('generate/simulator')

if not os.path.exists('storage/raw'):
    os.makedirs('storage/raw')

#
# START
#

answer = "n"# input("Start Generate Data? (y/n)")
if (answer.lower() == "y" or 'generate' in sys.argv):
    import generate
    if ('test' in sys.argv):
        generate.test()
    else:
        generate.run()

answer = "n"# input("Start Prepare Data? (y/n)")
if (answer.lower() == "y" or 'prepare' in sys.argv):
    import prepare
    if ('analyze' in sys.argv):
        prepare.analyze()
    else:
        prepare.run()

answer = "n"# input("Start Training? (y/n)")
if (answer.lower() == "y" or 'train' in sys.argv):
    import train
    train.run()
    
answer = "n" #input("Start Visualize? (y/n)")
if (answer.lower() == "y" or 'visualize' in sys.argv):
    import train#.torch_model as model

    import analysis
    analysis.run()
    