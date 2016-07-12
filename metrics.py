#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 23:52:18 2015

@author: Dr. Fuzzy
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import numpy as np
import matplotlib.pyplot as plt

class Metrics(object):
    """ Class that contains all metrics """

    def __init__(self, time, gamma, phi, c, archive_K, archive_D, archive_a, archive_u):
        self.time = time
        self.gamma = gamma
        self.phi = phi 
        self.c = c
        self.archive_K = archive_K
        self.archive_D = archive_D
        self.archive_a = archive_a
        self.archive_u = archive_u
        self.mrt = None

    def calc_metric(self, metric_name):
        """ Calculate chosen metric. """
#        print("%s", _metrics.keys())        
        
        if metric_name == 'mrt':
            # sanity check
            if len(self.archive_D) != len(self.archive_a):
                raise ValueError("Archives with different length: <%r>, <%r>" % (self.archive_D, self.archive_a))
            # local names (if you care for speed, you'd better avoid attribute lookups in inner loops!)
            gamma, phi, archive_D, archive_a = self.gamma, self.phi, self.archive_D, self.archive_a
            self.mrt = mrt = np.zeros_like(archive_D, dtype=np.float)
            # main algorithm
            for i, (a, D) in enumerate(zip(archive_a, archive_D)):
                g = D / a if a != 0 else 1000
                k = gamma * (g - phi)
                mrt[i] = np.exp(k) if g < 0.8 else 1 + k
            return mrt
        elif metric_name == 'rms':
            return np.sqrt(np.linalg.norm(self.archive_u - self.c * self.archive_a)**2 / self.time)
        else:
            msg = "Not known metric '%s'!" % metric_name
            raise ValueError(msg)            

    def plot_metric(self, metric_name, x_label = None, y_label = None, marker = None, line_width = None):
        """ Plot chosen metric. """
        _metrics = {
        'mrt': {'val': [self.mrt], 'xlabel': 'time interval', 'ylabel': 'mRT (s)', 'marker': ['b'], 'linewidth': 1.5},
        'cpu': {'val': [self.archive_a, self.archive_u], 'xlabel': 'time interval', 'ylabel': 'CPU (%)', 'marker': ['b', 'k'], 'linewidth': 1.5}, 
        'gain': {'val': [self.archive_K], 'xlabel': 'time interval', 'ylabel': 'gain', 'marker': ['b'], 'linewidth': 1.5}
        };
        
        if x_label is None:
            x_label = _metrics[metric_name]['xlabel']
        if y_label is None:
            y_label = _metrics[metric_name]['ylabel']
        if marker is None:
            marker = _metrics[metric_name]['marker']
        if line_width is None:
            line_width = _metrics[metric_name]['linewidth']            
        
        plot_val = _metrics[metric_name]['val']

        if metric_name is 'mrt' and self.mrt is None:
            msg = "mRT cost has not been calculated. Call <calc_mrt_cost()> and try again!"
            raise ValueError(msg)
        
        if metric_name is 'cpu' and len(marker) is not 2:
            msg = "<plot_metric()> for '%s' requires exactly 2 markers (%d defined)!" % (metric_name, len(marker))
            raise ValueError(msg)

        for count in range(0,len(plot_val)):
            plt.plot(plot_val[count], marker[count], linewidth=line_width)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        #plt.box(on=True)
        plt.show() # force plot now and then return to main code

#    def calc_mrt_cost(self):
#        """ Calculate the mRT cost """
#        # sanity check
#        if len(self.archive_D) != len(self.archive_a):
#            raise ValueError("Archives with different length: <%r>, <%r>" % (archive_D, archive_a))
#        # local names (if you care for speed, you'd better avoid attribute lookups in inner loops!)
#        gamma, phi, archive_D, archive_a = self.gamma, self.phi, self.archive_D, self.archive_a
#        self.mrt = mrt = np.zeros_like(archive_D, dtype=np.float)
#        # main algorithm
#        # XXX I don't like how I named the variables here, but I don't know the topic so
#        # I can't come up with better ones!
#        for i, (a, D) in enumerate(zip(archive_a, archive_D)):
#            g = D / a if a != 0 else 1000
#            k = gamma * (g - phi)
#            mrt[i] = np.exp(k) if g < 0.8 else 1 + k
#        return mrt
#
#    def calc_rms_error(self):
#        """ Return RMS error. """
#        return np.sqrt(np.linalg.norm(self.archive_u - self.c * self.archive_a)**2 / self.time)

#    def plot_mrt(self):
#        """ Plot the mRT cost. """
#        if self.mrt is None:
#            msg = "mRT cost has not been calculated. Call <calc_mrt_cost()> and try again!"
#            raise ValueError(msg)
#        plt.plot(self.mrt, '-b', linewidth=1.5)
#        plt.xlabel('time interval')
#        plt.ylabel('mRT (s)')
#        #plt.box(on=True)
#        plt.show() # force plot now and then return to main code
#
#    @staticmethod
#    def plot_cpu(archive_a, archive_u):
#        """ Plot the CPU (%) allocation. """
#        plt.plot(archive_a, '-b', linewidth=1.5)
#        plt.plot(archive_u, 'k', linewidth=1.5)
#        plt.xlabel('time interval')
#        plt.ylabel('CPU (%)')
#        #set(gca,'FontSize',14);
#        #plt.box(on=True)
#        plt.show() # force plot now and then return to main code
#
#    @staticmethod
#    def plot_gain(archive_K):
#        """ Plot the gain. """
#        plt.xlabel('time interval')
#        plt.ylabel('gain')
#        plt.plot(archive_K, '-b*')
#        #set(gca,'FontSize',12);
#        #plt.box(on=True)
#        plt.show() # force plot now and then return to main code
      
#x = metrics.calc_mrt_cost(np.array(range(8)).T, np.array(range(8, 16)).T)
#metrics.plot_mrt()
#metrics = Metrics(100, 10, 0.8, 0.95, np.array(range(10)).T, np.array(range(8)).T, np.array(range(8)).T, np.array(range(8)).T)
#x = metrics.calc_metric('mrt') # compute mRT cost
#metrics.plot_metric('mrt', 'time interval', 'mRT (s)', None, 1) # plot mRT cost
#metrics.plot_metric(metric_name = 'cpu', x_label = 'time interval', y_label = 'CPU (%)', marker = ['go', 'r'], line_width = 1) # plot gain
#metrics.plot_metric('gain', 'time interval', 'Gain', ['g--'], 1) # plot gain
