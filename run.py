'''
This is the main file where the program starts

TODO:
    - 
    
    [FEATURES]
    - list of actions to execute. First ask all questions (like a config)
'''
import generate
import train

answer = input("Start Generate Data? (y/n)")
if (answer.lower() == "y"):
    generate.run()

answer = input("Start Training? (y/n)")
if (answer.lower() == "y"):
    train.run()
    