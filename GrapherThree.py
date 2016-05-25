from brian2.only import *
from matplotlib.pyplot import *
from NetworkConstants import *
import numpy as np
import cPickle, gzip, os, sys, signal

"""
A quick script to visualize the synaptic weights for the second layer
of the network.
"""

def graph_synapses(file_name, to_graph=None):
  """
  Graph the synapses given in to_graph using colormaps
  if no to_graph list is given, graph everything
  """
  try:
    with open (file_name, 'r') as f:
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      v_th_H = np.load(f)
      w = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      _ = np.load(f)
      v_th_O = np.load(f)
      m = len(v_th_H)
      k = len(v_th_O)

      if (to_graph == None):
        to_graph = range(0, k)

      transposed_weights = np.reshape(w, (m, k)).T

      height = 2
      width = 4
      total = height*width

      # MAKE SURE THESE ARE DEFINED CORRECTLY FOR NUMBER OF WEIGHTS
      color_plot_height = 10
      color_plot_width = 5
      if (color_plot_width*color_plot_height != m):
        print('\nERROR: plot size not equal to number of synaptic weights, should be %d, is %d\n' % (m, color_plot_width*color_plot_height))
      else:
        for i in range(0, len(to_graph)):
          if (i%total == 0):
            figure(i/total + 1, figsize=(4*width,4*height))
          subplot(height,width,(i%total)+1)
          imshow(np.reshape(transposed_weights[i], (color_plot_height, color_plot_width)), interpolation='nearest')
          title('synapse: %s' % (i))
          colorbar()
        show()
  except IOError as e:
    print "error opening file: %s" % e.strerror
    sys.exit()

load_file = raw_input('enter file to load weights from: ').strip()
graph_synapses(load_file)

