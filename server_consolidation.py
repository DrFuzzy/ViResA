#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 16:56:08 2015
Edited on Fri May 25 01:01:50 2018

@author: Dr. Kyriakos M. Deliparaschos
@author: Evagoras Makridis
"""

import mimo_model
import metrics
import os
from time import sleep

# Global experiment parameters: 
duration = 250 # seconds
delay = 1  # first measurement of cpu usage is always 0 (Xen)
qos = 0.5  # QoS in seconds
total_exps = 2
control_interval = 5
samples = float(duration) / control_interval
ans = True

while ans:
    menulist = '''\nChoose a controller from the menu ('q' to quit).
      1  - Kalman MIMO
      2  - Hinf MIMO
      3  - MCC-KF MIMO
      q  - Quit'''
    print menulist
    ans = raw_input('\033[93m' + '#? ' + '\033[0m')
    
    # initialize variables
    if ans == '1' or ans == '2' or ans == '3':
      if not (os.path.isdir('./experiments')):
        os.makedirs('./experiments')
      os.system("/root/start_workload.sh ")
      print "\nGenerating workload..."
      sleep(20)
      mimo_model.mimo(ans, total_exps, duration, delay, qos, control_interval)
      metrics.export_figs_mimo(ans, duration, int(samples))

    elif ans == 'q':
      print('\nGood bye!')
      ans = None

    else:
      print('\033[91m' + '\nInvalid option. Try another one!\n' + '\033[0m')
      ans = True