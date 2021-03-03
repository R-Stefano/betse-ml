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

#ENV CONFIGURATIONS
import random
random.seed(0)


answer = "n"# input("Start Generate Data? (y/n)")
if (answer.lower() == "y"):
    generate.run()

answer = "n"# input("Start Prepare Data? (y/n)")
if (answer.lower() == "y"):
    prepare.run()

answer = "n"# input("Start Training? (y/n)")
if (answer.lower() == "y"):
    train.run()
    
answer = "y" #input("Start Visualize? (y/n)")
if (answer.lower() == "y"):
    analysis.visualize()
    