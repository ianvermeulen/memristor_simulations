from brian2.only import *
from matplotlib.pyplot import *
from NetworkConstants import *
import numpy as np
import cPickle, gzip, os, sys, signal

"""
A quick script to visualize the synaptic weights for the first layer
of synapses.
"""

def graph_synapses(file_name, to_graph=None):
  """
  Graph the synapses given in to_graph using colormaps
  if no to_graph list is given, graph everything
  """
  try:
    with open (file_name, 'r') as f:
      w = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      v_th = np.load(f)
      m = len(v_th)
      n = len(w)/m

      if (to_graph == None or len(to_graph) > m):
        to_graph = range(0, m)

      transposed_weights = np.reshape(w, (n, m)).T
      height = 2
      width = 3
      total = height*width

      for i in range(0, len(to_graph)):
        if (i%total == 0):
          figure(i/total + 1, figsize=(5*width,5*height))
        subplot(height,width,(i%total)+1)
        imshow(np.reshape(transposed_weights[i], (28, 28)), interpolation='nearest')
        title('synapse: %s' % (i))
        colorbar()
      show()
  except IOError as e:
    print "error opening file: %s" % e.strerror
    sys.exit()

to_graph = range(0, 54)

load_file = raw_input('enter file to load weights from: ').strip()
graph_synapses(load_file, to_graph)
