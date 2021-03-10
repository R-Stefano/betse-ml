'''
This is the main file where the program starts

TODO:
    - 
    
    [FEATURES]
    - list of actions to execute. First ask all questions (like a config)
'''
import generate
import prepare
import train
import analysis
import sys

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
    generate.run()

answer = "n"# input("Start Prepare Data? (y/n)")
if (answer.lower() == "y" or 'prepare' in sys.argv):
    prepare.run()

answer = "n"# input("Start Training? (y/n)")
if (answer.lower() == "y" or 'train' in sys.argv):
    train.run()
    
answer = "n" #input("Start Visualize? (y/n)")
if (answer.lower() == "y" or 'visualize' in sys.argv):
    analysis.visualize()
    