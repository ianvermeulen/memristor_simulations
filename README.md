# Overview

The simulations use the brian2 simulator. Documentation is available here: https://brian2.readthedocs.io/en/2.0rc1/. 

I used Anaconda to manage python details, it makes it pretty easy to setup the simulator along with all the othe python dependencies and also works on mac and PC. Most important is that I used python 2.7 instead of python 3.x. I found that using the older version is more stable with libraries such as brian2. The code will throw errors if being run in 3.x. If you are like me and normally run python3, look into anaconda environments (http://conda.pydata.org/docs/using/envs.html). I set up an environment to run python 2.7 while working with this project. I also run the code using ipython, but this is not necessary.

I store simulation data using a ".dat" extension. Since these files are very large, they are ignored by git as specified in ".gitignore". Alternatively, ".npy" would also make sense as a file extension as the network data is stored to a binary file using the NumPy.save function.

# Files

## NetworkConstants.py
This is where all the constants are stored for the network such as layer sizes, threshold voltages, etc.

## Simulation.py
This is the main simulator for a 2-layer network. An interrupted simulation (using ctrl+c in the shell) will be saved to the filename provided by the user so it can be restored later. The simulation also automatically saves its progress every so often based on a constant in NetworkConstants.py. This file can be provided when the simulator starts up and asks, "load from file [y/n]?". When execution is complete the resulting network is saved to a file with the name provided by the user with "DONE_" prepended

## SimulatorThree.py
This is the main simulator for a 3-layer network. Just like the 2-layer network, the simulation can be interrupted and all the data will be saved to a file. When beginning with a new training run, weights must be provided from a run of Simulation.py and the resulting results file.

## Tester.py
This is the testing program to classify and measure how well the 2-layer network has learned. No learning rules are applied in this program. After a results file is provided, classification beings. This consists of feeding 1000 digits throught the network. Each output neuron is classified as the digit to which it responds to the most. After that testing begins. Testing consists of feeding a digit into the network and then finding which output neuron spikes the most. The label for the digit is compared to the output neuron's classification. In the case of an interrupted test run, the intermediate state and results will be saved to a file provided by the user following the classification stage. This program prompts the user for this file when execution begins.

## TesterThree.py
This works basically the same as for Tester.py except for a 3-layer network.

## Grapher.py
This program is used to graph synaptic weights for a 2-layer network. Any list of weights can be graphed, though by default all the weights will. Edit the scripts bottom lines to change what is being graphed.

## GrapherThree.py
This program is used to graph synaptic weights for a 3-layer network. It's behavior is very similar to Grapher.py.

#mnist.pkl.gz
The MNIST digit set in pickled form.