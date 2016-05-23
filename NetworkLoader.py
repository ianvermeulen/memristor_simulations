from brian2.only import *
from NetworkConstants import *

def init_network(testing=False):
  """
  @param: testing - if set to true, no learning occurs. Weights are static.

  Initializes the network returns following 5 objects in order
  Input: input neurons, generate pulses according to rate value
  S: synapses connecting Input to Output. w (conductance) changes
     based on STDP learning rule based on memristor measurements
  Output: output neurons, leaky integrate and fire, spiking
     causes conductance change in associated synapse as well as
     lateral inhibition, i.e. discharges all other output neurons
  D_syn: Synapses used to form diffuser network for lateral inhibition
  D: Single neuron used to connect synapses in diffuser network
 
  The 'STDP_spike' event triggered by the Output neurons corresponds
  to an actual spike. Due to implementation details, the default spiking
  behavior in the output neurons is used to discharge the voltage.
 
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
    inhibit : boolean
  '''
  diffuse = '''
    inhibit = False
    v = 0
  '''
  Output = NeuronGroup(M, eqs, threshold = 'inhibit', 
                               events = {'STDP_spike' : 'v > v_th'},
                               reset = diffuse, 
                               refractory = T_INHIBIT)
  Output.run_on_event('STDP_spike', 'v=0')
  Output.inhibit = False

  ################################################################################
  # Setup Diffuser Network
  ################################################################################
  D = NeuronGroup(1, 'fire: boolean', threshold = 'fire', reset = 'fire = False')
  D.fire = False

  D_syn = Synapses(Output, D, pre = 'fire_post = True', 
                              post = 'inhibit_pre = True',
                              on_event = {'pre' : 'STDP_spike'},
                              connect = 'True')

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
  # normal learning rule
  post ='' if testing else '''
    w = clip(w + (v_pre)*(a_plus * exp(-b_plus*(w-w_min)/(w_max-w_min))) + (v_pre-1)*(a_minus * exp(-b_minus*(w_max-w)/(w_max-w_min))), w_min, w_max)
  ''' 
  # linear
  # post ='' if testing else '''
  #   w = clip(w + (v_pre)*((w_max-w_min)*.01) + (v_pre-1)*((w_max-w_min)*.01), w_min, w_max)
  # ''' 
  # very high learning rate
  # post ='' if testing else '''
  #   w = clip(w + (v_pre)*(a_plus * exp(-10*b_plus*(w-w_min)/(w_max-w_min))) + (v_pre-1)*(10*a_minus * exp(-b_minus*(w_max-w)/(w_max-w_min))), w_min, w_max)
  # ''' 

  S = Synapses(Input, Output, model = model, 
                              pre = pre, 
                              post = post, 
                              on_event = {'post' : 'STDP_spike'},
                              connect ='True')
  S.pre.delay = PULSE_LENGTH
  return Input, S, Output, D_syn, D
