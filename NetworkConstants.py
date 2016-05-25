from brian2.only import *

"""
  This file contains constants used for running simulations and
  instantiating the networks.
"""

N = 784                       # Size of input neuron group
M = 200                       # Size of second neuron group
K = 50                        # Size of third neuron group
DEV = 0.25                    # Std Dev of parameters in %
MAX_RATE = 20*Hz              # Maximum firing rate of input neurons
PER_DIGIT_TIME = 350*ms       # How long each digit is displayed for
ACTIVITY_TARGET = 1.0/M       # Used for homeostasis to get equal firing rates
ACTIVITY_TARGET_2 = 1.0/K       # Used for homeostasis to get equal firing rates
TAU = 10*ms                   # Time constant for leaky integrate and fire output neurons
G=1.                          # Multiplicative factor for leaky integrate and fire output neurons
GAMMA = 5.0                   # Multiplicative factor to increase threshold modifications for homeostasis
T_INHIBIT = 10*ms             # Length of time to keep output neurons discharged following lateral inhibition
PULSE_LENGTH = 25*ms          # Length of pulses from input neurons
MIN_VTH = 0.05                # Ensure that threshold voltages can't get to 0. 
                              #   In practice the thresholds don't come close to this value.
V_TH0 = 4.0                   # |
V_TH0_2 = 5.0                 # |           
W0 = 0.5                      # |         
W_MIN0 = 0.0001               # |
W_MAX0 =  1.0                 # | Mean values for parameters
A_PLUS0 = 0.01                # | original value = 0.010
A_MINUS0 = 0.005              # | original value = 0.005
B_PLUS0 = 3.0                 # | original value = 3.0
B_MINUS0 = 3.0                # | original value = 3.0
HOMEOSTASIS_LENGTH = 200      # How many digits are used to train before network is saved
                              #   and thresholds voltages are adjusted
SAVE_LENGTH = 2000            # How often the network should be automatically saved
                              #   This should be a multiple of HOMESTASIS_LENGTH
TRAINING_SIZE = 60000         # Size of training set
TRAINING_ROUNDS = 3           # How many rounds of training should be done
CLASSIFICATION_DIGITS = 1000  # Number of digits used to classify output neuron digits
TESTING_SIZE = 10000          # Size of testing set
