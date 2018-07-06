#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 23:52:18 2015
Edited on Tue Jan 25 14:40:24 2018

@author: Dr. Kyriakos M. Deliparaschos
@author: Mr. Evagoras Makridis
"""

from __future__ import division
import numpy as np
from itertools import imap
import math
import matplotlib.ticker as mtick
import decimal
import os
import subprocess
import csv
import matplotlib.pyplot as plt

# Function definitions

# This function plots the real mRT
def real_mrt_plot(controller,total_duration,date,avg_cpu,var,cov,qos,control_interval):
  total_response = 0
  response_frequency = 0
  mrt = 0
  avg_mrt = 0
  mrts = []
  control_interval = control_interval * 1000 # control interval * 1000 ms
  CR = 0 # number of completed requests
  NR = 0.0 # ratio of mrt <= 1
  file_directory = '/root/viresa/response.txt'

  # read the last timestamp from file
  with open (file_directory,"r") as response_file:
    lines = response_file.readlines()
    first_timestamp = int((lines[0]).split(',', 1)[0]) # check if true
    # last_timestamp = int((lines[len(lines)-1]).split(',', 1)[0])
    period = first_timestamp + control_interval
    CR =  len(lines)

    timestamps = np.genfromtxt(file_directory, usecols=(0), delimiter=',', dtype=None)
    response_times = np.genfromtxt(file_directory, usecols=(1), delimiter=',', dtype=None)
  
  response_file.close()

  for i,timestamp in enumerate(timestamps):
    if timestamp < period:
      total_response += response_times[i]
      response_frequency += 1
    else:
      mrt = float(total_response) / response_frequency
      mrts.append(mrt)
      mrt = 0
      total_response = response_times[i]
      period = timestamp + control_interval

  mrts[:] = [x / 1000 for x in mrts] # divides each list element (mrt) by 1000 
  NR = sum(1 for i in mrts if i < qos) / len(mrts) # ratio of mRTs < QoS target
  avg_mrt = sum(mrts)/(total_duration/control_interval)

  if controller == '1' or controller == '2' or controller == '3':
    with open("stats_mimo.txt", "a") as stats_file:
      stats_file.write("%s,%s,%s,%s,%s,%s,%.3f,%d,%.2f\n" %(date, avg_cpu[0], avg_cpu[1], var[0], var[1], cov, avg_mrt, CR, NR))
    stats_file.close()
    
  return mrts


def export_figs_mimo(ans, duration, samples):
  if ans == '1':
    fig_label = '$\mathit{Kalman}\/_\mathit{(MIMO)}$'
  if ans == '2':
    fig_label = '$\mathcal{H}_{\infty}\/_\mathit{(MIMO)}$'
  if ans == '3':
    fig_label = '$\mathit{MCC-KF}\/_\mathit{(MIMO)}$'

  directory = os.path.join("experiments/")
  for root,dirs,files in os.walk(directory):
    for file in files:
      timelist = []
      timelist.extend(range(0, samples))
       
      if file.startswith("log_sp"):
        file_log = open("%s%s" %(directory,file), 'r')
        log_file = directory + file
        cpu_id = file[3:-4] # removes from string log.txt

        archive_u1 = np.genfromtxt(log_file, usecols=(1), delimiter=',', dtype=None)
        archive_u2 = np.genfromtxt(log_file, usecols=(2), delimiter=',', dtype=None)
        archive_a1 = np.genfromtxt(log_file, usecols=(3), delimiter=',', dtype=None)
        archive_a2 = np.genfromtxt(log_file, usecols=(4), delimiter=',', dtype=None)
        archive_K1 = np.genfromtxt(log_file, usecols=(5), delimiter=',', dtype=None)
        archive_K2 = np.genfromtxt(log_file, usecols=(6), delimiter=',', dtype=None)
        archive_var1 = np.genfromtxt(log_file, usecols=(7), delimiter=',', dtype=None)
        archive_var2 = np.genfromtxt(log_file, usecols=(8), delimiter=',', dtype=None)
        # archive_cov = np.genfromtxt(log_file, usecols=(9), delimiter=',', dtype=None)

        qerr1 = np.sqrt(archive_var1)
        qerr2 = np.sqrt(archive_var2)
           
        fig1 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        plt.xticks(range(0,samples+1,5))
        plt.ylim((0, 100))
        plt.xlim((0, samples))
        plt.errorbar(timelist,archive_u1,yerr=qerr1,ecolor='k',linestyle="None", alpha = 0.2)
        plt.plot(archive_a1, 'r', linestyle='-', marker='+', label='$\mathit{allocation}$', linewidth=1.0)
        plt.plot(archive_u1, 'k', linestyle='-', label='$\mathit{usage}$', linewidth=1.0)
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{CPU}$ $\mathit{(\%)}$')
        plt.legend(fancybox=True, framealpha=True, loc='upper left', shadow=False)
        fig1.savefig('%sweb_cpu%s.pdf' %(directory,cpu_id))

        fig2 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        plt.xticks(range(0,samples+1,5))
        plt.ylim((0, 100))
        plt.xlim((0, samples))
        plt.errorbar(timelist,archive_u2,yerr=qerr2,ecolor='k',linestyle="None", alpha = 0.2)
        plt.plot(archive_a2, 'r', linestyle='-', marker='+', label='$\mathit{allocation}$', linewidth=1.0)
        plt.plot(archive_u2, 'k', linestyle='-', label='$\mathit{usage}$', linewidth=1.0)
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{CPU}$ $\mathit{(\%)}$')
        plt.legend(fancybox=True, framealpha=True, loc='upper left', shadow=False)
        fig2.savefig('%sdb_cpu%s.pdf' %(directory,cpu_id))

        fig3 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.ylim((0, 1.5+0.1))
        plt.xlim((0, samples))
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{gain}$')
        plt.plot(archive_K1, '-b*', label = fig_label)
        plt.legend(fancybox = True,framealpha=True, loc = 'lower right', shadow = False)
        fig3.savefig('%sweb_gain%s.pdf' %(directory,cpu_id))

        fig4 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.ylim((0, 1.5+0.1))
        plt.xlim((0, samples))
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{gain}$')
        plt.plot(archive_K2, '-b*', label = fig_label)
        plt.legend(fancybox = True,framealpha=True, loc = 'lower right', shadow = False)
        fig4.savefig('%sdb_gain%s.pdf' %(directory,cpu_id))
        file_log.close()

      if file.startswith("mrt"):
        file_mrt = open("%s%s" %(directory,file), 'r')
        mrt_file = directory + file
        mrt_id = file[3:-4] # removes from string log.txt

        mrts = np.genfromtxt(mrt_file, usecols=(0), delimiter=',', dtype=None)

        fig5 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.plot(mrts,'-b', label = fig_label, linewidth=1.0)
        plt.yticks(np.arange(0, 3.1, 0.5))
        plt.xticks(range(0,samples+1,5))        
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{mRT}$ $\mathit{(s)}$')
        plt.ylim((0,3.1))
        plt.xlim((0,samples+1))
        plt.axhline(y=0.5, color='k', linestyle='--', linewidth=0.5, alpha = 0.8)
        plt.legend(fancybox = True,framealpha=True, loc = 'upper right', shadow = False)
        fig5.savefig('%smrt%s.pdf' %(directory,mrt_id))
        file_mrt.close()
