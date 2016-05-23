from brian2.only import *
from matplotlib.pyplot import *
from NetworkLoaderThree import *
from NetworkConstants import *
import numpy as np
import cPickle, gzip, os, sys, signal

start_scope()

Input,S_IH,Hidden,D_H_syn,D_H,S_HO,Output,D_O_syn,D_O = init_network(testing=True)

training_set = None
start_digit = 0
start_round = 0

def load_initial_network_for_training(file_name):
  """
  Load values from a complete training run into the initialized network.
  Synaptic parameters are loaded.
  Output thresholds are loaded.
  """
  try:
    with open (file_name, 'r') as f:
      w = np.load(f)
      w_min = np.load(f)
      w_max = np.load(f)
      a_plus = np.load(f)
      a_minus = np.load(f)
      b_plus = np.load(f)
      b_minus = np.load(f)
      v_th = np.load(f)

      Hidden.set_states({'v_th' : v_th})
      S_IH.set_states({
        'w' : w,
        'w_min' : w_min, 
        'w_max' : w_max, 
        'a_plus' : a_plus, 
        'a_minus' : a_minus, 
        'b_plus' : b_plus, 
        'b_minus' : b_minus
      })
  except IOError as e:
    print "error opening file: %s" % e.strerror
    sys.exit()

def load_network_for_training(file_name):
  """
  Load values from a complete training run into the initialized network.
  Synaptic parameters are loaded.
  Output thresholds are loaded.
  """
  global training_set, start_round, start_digit
  try:
    with open (file_name, 'r') as f:
      w = np.load(f)
      w_min = np.load(f)
      w_max = np.load(f)
      a_plus = np.load(f)
      a_minus = np.load(f)
      b_plus = np.load(f)
      b_minus = np.load(f)
      v_th = np.load(f)

      Hidden.set_states({'v_th' : v_th})
      S_IH.set_states({
        'w' : w,
        'w_min' : w_min, 
        'w_max' : w_max, 
        'a_plus' : a_plus, 
        'a_minus' : a_minus, 
        'b_plus' : b_plus, 
        'b_minus' : b_minus
      })

      w = np.load(f)
      w_min = np.load(f)
      w_max = np.load(f)
      a_plus = np.load(f)
      a_minus = np.load(f)
      b_plus = np.load(f)
      b_minus = np.load(f)
      v_th = np.load(f)

      Output.set_states({'v_th' : v_th})
      S_HO.set_states({
        'w' : w,
        'w_min' : w_min, 
        'w_max' : w_max, 
        'a_plus' : a_plus, 
        'a_minus' : a_minus, 
        'b_plus' : b_plus, 
        'b_minus' : b_minus
      })

      training_set = np.reshape(np.load(f), (TRAINING_SIZE, N))
      start_round = np.load(f)
      start_digit = np.load(f)
      print "starting round: %d" % start_round
      print "starting digit: %d" % start_digit
  except IOError as e:
    print "error opening file: %s" % e.strerror
    sys.exit()

def randomize_values():
  """
  Used to initialize parameters in the synapses and Output neurons.
  """
  Output.set_states({'v_th' : np.random.normal(V_TH0_2, V_TH0_2*DEV, M)})

  S_HO.set_states({
    'w' : np.random.normal(W0,W0*DEV,M*M),
    'w_min' : np.random.normal(W_MIN0, W_MIN0*DEV, M*M),
    'w_max' : np.random.normal(W_MAX0, W_MAX0*DEV, M*M), 
    'a_plus' : np.random.normal(A_PLUS0, A_PLUS0*DEV, M*M), 
    'a_minus' : np.random.normal(A_MINUS0, A_MINUS0*DEV, M*M),
    'b_plus' : np.random.normal(B_PLUS0, B_PLUS0*DEV, M*M),
    'b_minus' : np.random.normal(B_MINUS0, B_MINUS0*DEV, M*M)
  })

  # check to make sure all values are non negative and below max
  for i in range(0,M*M):
    if (S_HO.w[i] < S_HO.w_min[i]):
      S_HO.w[i] = S_HO.w_min[i]
    elif (S_HO.w[i] > S_HO.w_max[i]):
      S_HO.w[i] = S_HO.w_max[i]
    if (S_HO.a_plus[i] < 0):
      S_HO.a_plus[i] = 0
    if (S_HO.a_minus[i] < 0):
      S_HO.a_minus[i] = 0
    if (S_HO.b_plus[i] < 0):
      S_HO.b_plus[i] = 0
    if (S_HO.b_minus[i] < 0):
      S_HO.b_minus[i] = 0

def load_training_set():
  """
  Load the MNIST digits for training. Shuffles them as well.
  """
  global training_set
  f = gzip.open('mnist.pkl.gz', 'rb')
  train, valid, test = cPickle.load(f)
  [training_set, training_labels] = train
  [validation_set, validation_labels] = valid
  [testing_set, testing_labels] = test
  training_set = np.concatenate((training_set, validation_set))
  f.close()
  np.random.shuffle(training_set)

def save_network(save_file, training_round, digit):
  """
  save the current testing run due to an interrupt
  """
  with open(save_file, 'wb') as f:
    np.save(f, S_IH.w)
    np.save(f, S_IH.w_min)
    np.save(f, S_IH.w_max)
    np.save(f, S_IH.a_plus)
    np.save(f, S_IH.a_minus)
    np.save(f, S_IH.b_plus)
    np.save(f, S_IH.b_minus)
    np.save(f, Hidden.v_th)
    np.save(f, S_HO.w)
    np.save(f, S_HO.w_min)
    np.save(f, S_HO.w_max)
    np.save(f, S_HO.a_plus)
    np.save(f, S_HO.a_minus)
    np.save(f, S_HO.b_plus)
    np.save(f, S_HO.b_minus)
    np.save(f, Output.v_th)
    np.save(f, training_set.flatten())
    np.save(f, training_round)
    np.save(f, digit)

flag = True
perform_classification = True
while flag:
  should_load = raw_input('load entire 3 layer network [y/n]? ').strip().lower()
  if (should_load == 'y' or should_load == 'yes'):
    load_file = raw_input('enter file to load network from: ').strip()
    load_network_for_training(load_file)
    flag = False
  elif (should_load == 'n' or should_load == 'no'):
    load_file = raw_input('enter file to load initial weights from: ').strip()
    load_initial_network_for_training(load_file)
    randomize_values()
    load_training_set()
    flag = False

save_file = raw_input('enter file to save weights to: ').strip()

# hidden_mon = SpikeMonitor(Hidden)
event_mon = EventMonitor(Output, 'STDP_spike')

try:
  print 'starting simulation'
  for i in range(start_round, TRAINING_ROUNDS):
    j = start_digit
    while (j < TRAINING_SIZE):
      if (j%SAVE_LENGTH == 0):
        print 'saving network'
        s = signal.signal(signal.SIGINT, signal.SIG_IGN)
        save_network(save_file, i, j)
        signal.signal(signal.SIGINT, s)
      
      for x in range(0, HOMEOSTASIS_LENGTH-(j%HOMEOSTASIS_LENGTH)):
        print 'training digit %d' % (j+x) 
        Input.rate = training_set[j+x] * MAX_RATE
        run(PER_DIGIT_TIME)
        # spike_train = hidden_mon.spike_trains()
        # for k in range(0,M):
        #   print 'spikes for hidden neuron %d: %d' % (k, len(spike_train[k]))
        # del hidden_mon
        # hidden_mon = SpikeMonitor(Hidden)

      total_spikes = float(event_mon.num_events)
      event_train = event_mon.event_trains()
      if (total_spikes > 0):
        for k in range(0,M):
          # print 'total spikes: %d' % event_mon.num_events
          print 'total spikes for neuron %d: %d' % (k, len(event_train[k]))        
          # print 'spikes for neuron %d: %s' % (k, str(event_train[k]))    
          Output.v_th[k]+= GAMMA*(len(event_train[k])/total_spikes-ACTIVITY_TARGET)
          Output.v_th[k] = max(Output.v_th[k], MIN_VTH)
          # print 'change: %f, value: %f' % (GAMMA*(len(event_train[k])/total_spikes-ACTIVITY_TARGET), Output.v_th[k])
      else:
        print 'NO SPIKES in output'

      # reset spike counter
      del event_mon
      event_mon = EventMonitor(Output, 'STDP_spike')

      # increment j, but if we're continuing an interrupted simulation, re-align j with HOMEOSTASIS_LENGTH
      j = j + HOMEOSTASIS_LENGTH
      if (j%HOMEOSTASIS_LENGTH > 0):
        j -= j%HOMEOSTASIS_LENGTH

    np.random.shuffle(training_set)
    start_digit = 0

  print 'simulation ending, saving weights'
  save_network('DONE_'+save_file, TRAINING_ROUNDS, TRAINING_SIZE)

except(KeyboardInterrupt, SystemExit):
  s = signal.signal(signal.SIGINT, signal.SIG_IGN)
  save_network(save_file, i, j+x)
  signal.signal(signal.SIGINT, s)