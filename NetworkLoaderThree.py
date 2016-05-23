from brian2.only import *
from NetworkConstants import *

def init_network(testing=False):
  """
  @param: testing - if set to true, no learning occurs. Weights are static.

  Initializes the network returns following 10 objects in order
  Input: input neurons, generate pulses according to rate value
  S_IH: synapses connecting Input to Hidden layer. w (conductance) changes
     based on STDP learning rule based on memristor measurements
  Hidden: hidden neurons, leaky integrate and fire, spiking DOES NOT
     cause conductance change in associated synapse. There is still
     lateral inhibition, i.e. discharges all other hidden neurons, but no
     refractory period.
  D_H_syn: Synapses used to form hidden diffuser network for lateral inhibition
  D_H: Single neuron used to connect synapses in hidden diffuser network
  S_HO: synapses connecting Hidden to Output layer. w (conductance) changes
     based on STDP learning rule based on memristor measurements
  Output: Output neurons, leaky integrate and fire
  D_O_syn: Synapses used to form output diffuser network for lateral inhibition
  D_O: Single neuron used to connect synapses in output diffuser network
 
  The 'STDP_spike' event triggered by the Output neurons corresponds
  to an actual spike. Due to implementation details, the default spiking
  behavior in the output neurons is used to discharge the voltage.
 
  The rate values for the Input neurons are NOT set in this method.
  The parameters of all synapses are NOT set in this method. 
  The threshold voltages of the hidden and output neurons are NOT set in this method.
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
  # Setup Hidden Neurons
  ################################################################################
  eqs = '''
    dv/dt = (I-G*v)/TAU : 1
    I : 1
    v_th : 1
    v_output : 1
    STDP_reset_flag : boolean
  '''
  reset = '''
    v = 0
    v_output = 1
  '''
  diffuse = '''
    v = 0
    STDP_reset_flag = False
  '''
  Hidden = NeuronGroup(M, eqs, threshold = 'v > v_th',
                               events = {'STDP_reset' : 'STDP_reset_flag'},
                               reset = reset)
  Hidden.run_on_event('STDP_reset', diffuse)
  Hidden.v_output = 0
  Hidden.STDP_reset_flag = False

  ################################################################################
  # Setup Hidden Layer Diffuser Network
  ################################################################################
  D_H = NeuronGroup(1, 'fire: boolean', threshold = 'fire', reset = 'fire = False')
  D_H.fire = False

  D_H_syn = Synapses(Hidden, D_H, pre = 'fire_post = True', 
                                  post = 'STDP_reset_flag_pre = True',
                                  connect = 'True')

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
  Output = NeuronGroup(K, eqs, threshold = 'inhibit', 
                               events = {'STDP_spike' : 'v > v_th'},
                               reset = diffuse, 
                               refractory = T_INHIBIT)

  Output.run_on_event('STDP_spike', 'v=0')
  Output.inhibit = False

  ################################################################################
  # Setup Output Layer Diffuser Network
  ################################################################################
  D_O = NeuronGroup(1, 'fire: boolean', threshold = 'fire', reset = 'fire = False')
  D_O.fire = False

  D_O_syn = Synapses(Output, D_O, pre = 'fire_post = True', 
                              post = 'inhibit_pre = True',
                              on_event = {'pre' : 'STDP_spike'},
                              connect = 'True')

  ################################################################################
  # Setup Input to Hidden Synapses
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

  S_IH = Synapses(Input, Hidden, model = model, 
                                 pre = pre,
                                 connect ='True')
  S_IH.pre.delay = PULSE_LENGTH

  ################################################################################
  # Setup Hidden to Output Synapses
  ################################################################################
  model = '''
    w : 1
    w_min : 1 (constant)
    w_max : 1 (constant)
    a_plus: 1 (constant)
    a_minus: 1 (constant)
    b_plus: 1 (constant)
    b_minus: 1 (constant)
    I_post = w*v_output_pre : 1 (summed)
  '''
  pre = '''
    v_output_pre = 0
  '''

  # increments if input neuron is currently high, decrements otherwise
  post ='' if testing else '''
    w = clip(w + (v_output_pre)*(a_plus * exp(-b_plus*(w-w_min)/(w_max-w_min))) + (v_output_pre-1)*(a_minus * exp(-b_minus*(w_max-w)/(w_max-w_min))), w_min, w_max)
  ''' 

  S_HO = Synapses(Hidden, Output, model = model, 
                                  pre = pre, 
                                  post = post, 
                                  on_event = {'post' : 'STDP_spike'},
                                  connect ='True')
  S_HO.pre.delay = PULSE_LENGTH
  return Input, S_IH, Hidden, D_H_syn, D_H, S_HO, Output, D_O_syn, D_O
