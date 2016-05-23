from brian2.only import *
from matplotlib.pyplot import *
from NetworkLoader import *
from NetworkConstants import *
import numpy as np
import cPickle, gzip, os, sys, signal

start_scope()

Input,S,Output,D_syn,D = init_network()

start_digit = 0
start_round = 0
training_set = None

def load_network_for_training(file_name):
  """
  Load values from a previous training run into the initialized network.
  Synaptic parameters are loaded.
  Output thresholds are loaded.
  current digit and round from the last training round are loaded.
  The training set is reloaded to ensure it is in the same shuffled order.

  The synapses are also displayed prior to training.
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
      training_set = np.reshape(np.load(f), (TRAINING_SIZE, N))
      start_round = np.load(f)
      start_digit = np.load(f)

      Output.set_states({'v_th' : v_th})
      S.set_states({
        'w' : w,
        'w_min' : w_min, 
        'w_max' : w_max, 
        'a_plus' : a_plus, 
        'a_minus' : a_minus, 
        'b_plus' : b_plus, 
        'b_minus' : b_minus
      })
      print start_round
      print start_digit
      print v_th
  except IOError as e:
    print "error opening file: %s" % e.strerror
    sys.exit()

def randomize_values():
  """
  Used to initialize parameters in the synapses and Output neurons.
  """
  Output.set_states({'v_th' : np.random.normal(V_TH0, V_TH0*DEV, M)})

  S.set_states({
    'w' : np.random.normal(W0,W0*DEV,N*M),
    'w_min' : np.random.normal(W_MIN0, W_MIN0*DEV, N*M),
    'w_max' : np.random.normal(W_MAX0, W_MAX0*DEV, N*M), 
    'a_plus' : np.random.normal(A_PLUS0, A_PLUS0*DEV, N*M), 
    'a_minus' : np.random.normal(A_MINUS0, A_MINUS0*DEV, N*M),
    'b_plus' : np.random.normal(B_PLUS0, B_PLUS0*DEV, N*M),
    'b_minus' : np.random.normal(B_MINUS0, B_MINUS0*DEV, N*M)
  })

  # check to make sure all values are non negative and below max
  for i in range(0,N*M):
    if (S.w[i] < S.w_min[i]):
      S.w[i] = S.w_min[i]
    elif (S.w[i] > S.w_max[i]):
      S.w[i] = S.w_max[i]
    if (S.a_plus[i] < 0):
      S.a_plus[i] = 0
    if (S.a_minus[i] < 0):
      S.a_minus[i] = 0
    if (S.b_plus[i] < 0):
      S.b_plus[i] = 0
    if (S.b_minus[i] < 0):
      S.b_minus[i] = 0

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
  Save the current network values as well as training state
  """
  with open(save_file, 'wb') as f:
    np.save(f, S.w)
    np.save(f, S.w_min)
    np.save(f, S.w_max)
    np.save(f, S.a_plus)
    np.save(f, S.a_minus)
    np.save(f, S.b_plus)
    np.save(f, S.b_minus)
    np.save(f, Output.v_th)
    np.save(f, training_set.flatten())
    np.save(f, training_round)
    np.save(f, digit)

flag = True
while flag:
  should_load = raw_input('load from file [y/n]? ').strip().lower()
  if (should_load == 'y' or should_load == 'yes'):
    load_file = raw_input('enter file to load weights from: ').strip()
    load_network_for_training(load_file)
    flag = False
  elif (should_load == 'n' or should_load == 'no'):
    randomize_values()
    load_training_set()
    flag = False

save_file = raw_input('enter file to save weights to: ').strip()

# Don't enable these monitors during long training runs
# It will eat up enormous amounts of memory and stop the simulation
# after ~2400 digits
# out_mon = StateMonitor(Output, ['I','v'], record=True)
# in_mon = StateMonitor(Input, 'v', record=True)
# syn_mon = StateMonitor(S, 'w', record=True)
# out_spikes = SpikeMonitor(Output)
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
        # figure(figsize=(8,8))
        # subplot(221)
        # plot(out_mon.t/ms, out_mon.v[0], '-b', label='voltage[0]')
        # for t in  event_mon.values('t')[0]:
        #   axvline(t/ms, ls='--', c='r', lw='3')
        # xlim(0,100)
        # subplot(222)
        # #plot(syn_mon.t/ms, syn_mon.w[2], '-g', label='post weights 2')
        # subplot(223)
        # plot(out_mon.t/ms, out_mon.I[0], '-b', label='post current0')
        # subplot(224)
        # plot(in_mon.t/ms, in_mon.v[0], '-bo', label='voltage[0]')
        # plot(in_mon.t/ms, in_mon.v[1], '-ro', label='voltage[1]')
        # plot(in_mon.t/ms, in_mon.v[2], '-go', label='voltage[2]')
        # show()   

      total_spikes = float(event_mon.num_events)
      event_train = event_mon.event_trains()
      for k in range(0,M):
        # print 'total spikes: %d' % event_mon.num_events
        print 'total spikes for neuron %d: %d' % (k, len(event_train[k]))
        # print 'neuron %d, activity:' % i
        Output.v_th[k]+= GAMMA*(len(event_train[k])/total_spikes-ACTIVITY_TARGET)
        Output.v_th[k] = max(Output.v_th[k], MIN_VTH)
        # print 'change: %f, value: %f' % (GAMMA*(len(event_train[k])/total_spikes-ACTIVITY_TARGET), Output.v_th[k])
      
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

  # print out_spikes.t
  # print out_spikes.i
  # print event_mon.t
  # print event_mon.i

  # plot(in_mon.t/ms, in_mon.v[0], '-bo', label='voltage[0]')
  # plot(in_mon.t/ms, in_mon.v[1], '-ro', label='voltage[1]')
  # plot(in_mon.t/ms, in_mon.v[2], '-go', label='voltage[2]')
  # plot(out_mon.t/ms, out_mon.v[0], '-b', label='voltage[0]')
  # plot(out_mon.t/ms, out_mon.v[1], '-r', label='voltage[1]')
  # plot(out_mon.t/ms, out_mon.v[2], '-g', label='voltage[2]')
  # plot(out_mon.t/ms, out_mon.I[0], '-b', label='post current0')
  # plot(out_mon.t/ms, out_mon.I[1], '-r', label='post current1')
  # plot(out_mon.t/ms, out_mon.I[2], '-g', label='post current2')
  # plot(syn_mon.t/ms, syn_mon.w[0], '-b', label='post weights 0')
  # plot(syn_mon.t/ms, syn_mon.w[1], '-r', label='post weights 1')
  # plot(syn_mon.t/ms, syn_mon.w[2], '-g', label='post weights 2')
  # for i in range(0,N*M):
  #   plot(syn_mon.t/ms, syn_mon.w[i], '-b')
  # for t in event_mon.t:
  #    axvline(t/ms, ls='--', c='r', lw='3')
  # xlabel('Time (ms)')
  # ylabel('v')
  # legend(loc='best')
  
except (KeyboardInterrupt, SystemExit):
  s = signal.signal(signal.SIGINT, signal.SIG_IGN)
  save_network(save_file, i, j+x)
  signal.signal(signal.SIGINT, s)













