from brian2.only import *
from matplotlib.pyplot import *
from NetworkLoader import *
from NetworkConstants import *
import numpy as np
import cPickle, gzip, os, sys, signal

start_scope()

Input,S,Output,D_syn,D = init_network(testing=True)
testing_set = None
testing_labels = None
validation_set = None
validation_labels = None
start_digit = 0
correct = 0
incorrect = 0
classifications = np.zeros(M)

def load_network_for_testing(file_name):
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
  except IOError as e:
    print "error opening file: %s" % e.strerror
    sys.exit()

def load_network_from_interrupted_testing(file_name):
  """
  Load values from an incomplete classification run into the initialized network.
  Synaptic parameters are loaded.
  Output thresholds are loaded.
  current training digit is loaded.
  current state of the training set is loaded.
  """
  global testing_set, testing_labels, classifications, start_digit, correct, incorrect
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
      testing_set = np.reshape(np.load(f), (TESTING_SIZE, N))
      testing_labels = np.load(f)
      classifications = np.load(f)
      start_digit = np.load(f)
      correct = np.load(f)
      incorrect = np.load(f)

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

      print 'starting at digit %d' % start_digit
      for i in range(0, M):
        print 'digit %i classified as %d' % (i, classifications[i])

  except IOError as e:
    print "error opening file: %s" % e.strerror
    sys.exit()

def load_testing_set():
  global testing_set, testing_labels, validation_set, validation_labels
  f = gzip.open('mnist.pkl.gz', 'rb')
  _, validation, test = cPickle.load(f)
  [testing_set_temp, testing_labels_temp] = test
  [validation_set_temp, validation_labels_temp] = validation

  validation_set = []
  validation_labels = []
  f.close()
  random_ordering = np.arange(len(validation_set_temp))
  np.random.shuffle(random_ordering)
  for i in range(len(random_ordering)):
    validation_set.append(validation_set_temp[random_ordering[i]])
    validation_labels.append(validation_labels_temp[random_ordering[i]])

  testing_set = []
  testing_labels = []
  f.close()
  random_ordering = np.arange(len(testing_set_temp))
  np.random.shuffle(random_ordering)
  for i in range(len(random_ordering)):
    testing_set.append(testing_set_temp[random_ordering[i]])
    testing_labels.append(testing_labels_temp[random_ordering[i]])
  testing_set = np.array(testing_set)
  testing_labels = np.array(testing_labels)

def save_interrupted_testing_run(save_file, digit):
  """
  save the current testing run due to an interrupt
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
    np.save(f, testing_set.flatten())
    np.save(f, testing_labels)
    np.save(f, classifications)
    np.save(f, digit)
    np.save(f, correct)
    np.save(f, incorrect)

def save_results(save_file):
  print 'testing complete'
  print 'number correctly classified: %d' % correct
  print 'number incorrectly classified: %d' % incorrect
  print 'accuracy: %f' % (float(correct) / float(correct+incorrect))
  with open(save_file, 'wb') as f:
    f.write('testing complete\n')
    f.write('number correctly classified: %d\n' % correct)
    f.write('number incorrectly classified: %d\n' % incorrect)
    f.write('accuracy: %f\n' % (float(correct) / float(correct+incorrect)))
  f.close()

flag = True
perform_classification = True
while flag:
  should_load = raw_input('load from interrupted test run [y/n]? ').strip().lower()
  if (should_load == 'n' or should_load == 'np'):
    load_file = raw_input('enter data file to load weights from: ').strip()
    load_network_for_testing(load_file)
    load_testing_set()
    flag = False
  elif (should_load == 'y' or should_load == 'yes'):
    load_file = raw_input('enter file to interrupted testing data from: ').strip()
    load_network_from_interrupted_testing(load_file)
    flag = False
    perform_classification = False

classification_counts = np.tile(np.zeros(10), (M, 1))
event_mon = EventMonitor(Output, 'STDP_spike')

if perform_classification:
  # Classify output neuron digits
  print "starting classification"
  for i in range (0,CLASSIFICATION_DIGITS):
    print 'classifying digit %d' % i
    Input.rate = validation_set[i] * MAX_RATE
    run(PER_DIGIT_TIME)

    event_train = event_mon.event_trains()

    # sum spiking activity for the current neuron according to displayed digit
    for k in range(0, M):
      classification_counts[k][validation_labels[i]] += len(event_train[k])
    
    # reset spike counter
    del event_mon
    event_mon = EventMonitor(Output, 'STDP_spike')

  # perform classification based on results of classification rounds
  for i in range(0, M):
    max_count = -1
    max_label = -1
    for k in range(0, 10):
      if (classification_counts[i][k] > max_count):
        max_count = classification_counts[i][k]
        max_label = k
    classifications[i] = max_label
    print "neuron %d classified as %d" % (i, max_label)

save_file = raw_input('enter file to save to in case of interrupt: ').strip()
event_mon = EventMonitor(Output, 'STDP_spike')

# begin testing
try:
  print 'starting testing simulation'
  for i in range(start_digit, TESTING_SIZE):
    Input.rate = testing_set[i] * MAX_RATE
    run(PER_DIGIT_TIME)

    event_train = event_mon.event_trains()

    max_neuron = -1
    max_spikes = -1
    # determine which neuron had the most spiking activity
    for k in range(0, M):
      if (len(event_train[k]) > max_spikes):
        max_spikes = len(event_train[k])
        max_neuron = k

    if (classifications[max_neuron] == testing_labels[i]):
      print 'digit %d classfied correctly as %d' % (i, testing_labels[i])
      correct += 1
    else:
      print 'digit %d classfied INCORRECTLY as %d instead of %d' % (i, classifications[max_neuron], testing_labels[i])
      sums = np.zeros(10)
      for k in range(0, M):
        sums[classifications[k]] += len(event_train[k])
      for k in range(0, 10):
        print '\tspikes for digit %d: %d' % (k, sums[k])
      incorrect += 1

    # reset spike counter
    del event_mon
    event_mon = EventMonitor(Output, 'STDP_spike')
  save_results('RESULTS_' + save_file)

except(KeyboardInterrupt, SystemExit):
  s = signal.signal(signal.SIGINT, signal.SIG_IGN)
  save_interrupted_testing_run(save_file, i)
  signal.signal(signal.SIGINT, s)
  