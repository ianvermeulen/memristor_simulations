from brian2.only import *
from NetworkConstants import *

def init_network(N, M, testing=False):
  """
  Initializes the network returns following 3 objects in order
  Input: input neurons, generate pulses according to rate value
  S: synapses connecting Input to Output. w (conductance) changes
     based on SDTP learning rule based on memristor measurements
  Output: output neurons, leaky integrate and fire, spiking causes
     causes conductance change in associated synapse as well as
     lateral inhibition, i.e. discharges all other output neurons

  This method is very similar to the normal init_network, but slightly
  different due to lack of diffuser network
 
  The rate values for the Input neurons are NOT set in this method.
  The parameters of the main synapses are NOT set in this method. 
  The threshold voltages of the Output neurons are NOT set in this method.
  """

  ################################################################################
  # Setup input Neurons
  ################################################################################
  eqs = '''
    v : 1
    rate : Hz
  '''
  Input = NeuronGroup(N, eqs, threshold = 'rand()<rate*dt', 
                              reset = 'v=1', 
                              refractory = PULSE_LENGTH) 
  Input.v = 0

  ################################################################################
  # Setup Output Neurons
  ################################################################################
  eqs = '''
    dv/dt = (I-G*v)/TAU : 1 (unless refractory)
    I : 1
    v_th : 1
  '''
  SDTP_reset = '''
    v = 0
  '''
  Output = NeuronGroup(M, eqs, threshold = 'v > v_th',
                               reset = SDTP_reset, 
                               refractory = T_INHIBIT)

  ################################################################################
  # Setup Synapses
  ################################################################################
  model = '''
    w : 1
    w_min : 1 (constant)
    w_max : 1 (constant)
    a_plus: 1 (constant)
    a_minus: 1 (constant)
    b_plus: 1 (constant)
    b_minus: 1 (constant)
    I_post = w*v_pre : 1 (summed)
  '''
  pre = '''
    v_pre = 0
  '''

  # increments if input neuron is currently high, decrements otherwise
  post ='' if testing else '''
    w = clip(w + (v_pre)*(a_plus * exp(-b_plus*(w-w_min)/(w_max-w_min))) + (v_pre-1)*(a_minus * exp(-b_minus*(w_max-w)/(w_max-w_min))), w_min, w_max)
  ''' 

  S = Synapses(Input, Output, model = model, 
                              pre = pre, 
                              post = post, 
                              connect ='True')
  S.pre.delay = PULSE_LENGTH
  return Input, S, Output
