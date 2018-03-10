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

# This function computes the mRT cost 
def mrt_cost(archive_D, archive_a, f, gamma):
    #(N,o) = archive_D.shape
    #(M,o) = archive_a.shape
    N = len(archive_D)
    M = len(archive_a)
    
    if M == N:
        mrt = np.zeros([N, 1])

        for i in range(0, N):
            if archive_a[i] == 0:
                g = 1000
            else:
                g = archive_D[i]/archive_a[i]

            if g < 0.8:
                mrt_tmp = np.exp(gamma*(g-f))
            else:
                mrt_tmp = 1+gamma*(g-f)      

            mrt[i] = mrt_tmp
        
        return mrt/1000    
    else:
        print("What is going wrong with you?")
        return

# This function plots the mRT model
def mrt_model():
    import matplotlib.pyplot as plt
    # define parameters
    archive_D = np.arange(0,1.001,0.001)    
    u = np.arange(0,1.001,0.001)
    archive_a = np.ones(len(archive_D))
    x = np.arange(0,1.01,0.01)
    f = 0.8
    gamma = 10
    
    # call function
    mrt = mrt_cost(archive_D, archive_a, f, gamma)
    
    # plot
    plt.plot(u, mrt, linewidth=1.0)
    plt.xlabel('$\mathit{CPU}$ $\mathit{Demand}$$\mathit{/}$$\mathit{CPU}$ $\mathit{allocation}$')
    plt.ylabel('$\mathit{mRT}$ $\mathit{(s)}$')
    # dotted region    
    plt.plot(u[0:800], np.ones(800), 'k--')
    plt.plot(0.8*np.ones(101), x, 'k--')

    return

# This function plots the real mRT
def real_mrt_plot(controller,total_time,date,avg_cpu,var1,var2,cov,qos,ca):
  import csv
  import matplotlib.pyplot as plt
  total = 0
  time = 0
  start = 0
  counter = 0
  mrt = 0
  avg_mrt = 0
  limit = 0
  currenttime = 0
  resptime = 0 
  cntr = 0
  mrt_list = [0]*2000
  ca = ca*1000 # control action * 1000 ms
  CR = 0 # number of completed requests
  NR = 0.0 # ratio of mrt <= 1
  if controller == '2' or controller == '4' or controller == '6':
    avg_cpu1 = avg_cpu[0]
    avg_cpu2 = avg_cpu[1]

  # read the last timestamp from file
  with open ('/root/viresa/response.txt',"r") as f1:
    data1 = f1.readlines()
    end = data1[len(data1)-1]
    last = int(end.split(',', 1)[0])
  
  with open ('/root/viresa/response.txt') as f:
    # calculate the number of completed requests
    CR =  len(f.readlines())
    #print "Completed Requests (CR): %d" %CR 

  with open ('/root/viresa/response.txt',"r") as f:
    time = 0
    resp = 0
    # read the first timestamp from file to begin start and limit
    data = f.readline()
    start = int(data.split(',', 1)[0])
    limit = start + ca 
    # read every line and split them to currenttime and resptime
    for line in f:
        currenttime , resptime = map(int,(item.strip() for item in line.split(',')))
        if currenttime < limit:
          total = total + resptime
          counter = counter + 1    
        else:
          mrt = total / counter
          cntr = cntr + 1
          mrt_list[cntr] = mrt
          counter = 1
          mrt = 0
          total = resptime
          limit = currenttime + ca
  f.close()

  mrts=[0]*(cntr)
  for i in range(cntr):
    if i > 1:
      mrts[i-1] = (mrt_list[i-1])/1000

  # number of requests with response time <= 1
  less1 = sum(1 for i in mrts if i < qos)
  tot = len(mrts)
  NR = less1/tot
  #print "Ratio of requests with mRT < QoS target: %f" %NR

  # average mrt for all the duration
  avg_mrt = sum(mrts)/(total_time/ca)

  if controller == '1' or controller == '3' or controller == '5' or controller == '7':
    with open("stats_siso.txt", "a") as att_file:
      att_file.write("%s,%.2f,%.3f,%.3f,%.3f,%.3f,%d,%.2f\n" %(date, avg_cpu, var1, var2, cov, avg_mrt, CR, NR))
  if controller == '2' or controller == '4' or controller == '6':
    with open("stats_mimo.txt", "a") as att_file:
      att_file.write("%s,%.2f,%.2f,%.3f,%.3f,%.3f,%.3f,%d,%.2f\n" %(date, avg_cpu1, avg_cpu2, var1, var2, cov, avg_mrt, CR, NR))

  return mrts

def export_figs_siso(ans, vm_name):

  if ans == '1':
    fig_label = '$\mathit{Kalman}\/_\mathit{(SISO)}$'
  if ans == '3':
    fig_label = '$\mathcal{H}_{\infty}\/_\mathit{(SISO)}$'
  if ans == '5':
    fig_label = '$\mathit{MCC-KF}\/_\mathit{(SISO)}$'

  if vm_name == 'Tomcat':
    directory = os.path.join("experiments/web/")
  if vm_name == 'MySQL':
    directory = os.path.join("experiments/db/")

  for root,dirs,files in os.walk(directory):
    for file in files:
      timelist = []
      timelist.extend(range(0, 50))
      time = 50
      qerr = []
       
      if file.startswith("log_sp"):
        f=open("%s%s" %(directory,file), 'r')
        log_file = directory + file
        cpu_id = file[3:-4] # removes from string log.txt

        archive_u = np.genfromtxt(log_file, usecols=(1), delimiter=',', dtype=None)
        archive_a = np.genfromtxt(log_file, usecols=(2), delimiter=',', dtype=None)
        archive_K = np.genfromtxt(log_file, usecols=(3), delimiter=',', dtype=None)
        var = np.genfromtxt(log_file, usecols=(4), delimiter=',', dtype=None)

        qerr = np.sqrt(var)
          
        fig1 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        plt.xticks(range(0,time+1,10))
        plt.ylim((0, 100))
        plt.xlim((0, time))
        plt.errorbar(timelist,archive_u,yerr=qerr,ecolor='k',linestyle="None", alpha = 0.2)
        plt.plot(archive_a, 'r', linestyle='-', marker='+', label='$\mathit{allocation}$', linewidth=1.0)
        plt.plot(archive_u, 'k', linestyle='-', label='$\mathit{usage}$', linewidth=1.0)
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{CPU}$ $\mathit{(\%)}$')
        legend = plt.legend(fancybox=True, framealpha=True, loc='upper left', shadow=False)
        fig1.savefig('%scpu%s.pdf' %(directory,cpu_id))

        fig2 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.ylim((0, 1.5+0.1))
        plt.xlim((0, time))
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{gain}$')
        plt.plot(archive_K, '-b*', label = fig_label)
        legend = plt.legend(fancybox = True,framealpha=True, loc = 'lower right', shadow = False)
        fig2.savefig('%sgain%s.pdf' %(directory,cpu_id))
        f.close()

      if file.startswith("mrt"):
        f=open("%s%s" %(directory,file), 'r')
        mrt_file = directory + file
        mrt_id = file[3:-4] # removes from string log.txt

        mrts = np.genfromtxt(mrt_file, usecols=(0), delimiter=',', dtype=None)

        fig3 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.plot(mrts,'-b', label = fig_label, linewidth=1.0)
        plt.yticks(np.arange(0, 3.1, 0.5))
        plt.xticks(range(0,time+1,10))        
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{mRT}$ $\mathit{(s)}$')
        plt.ylim((0,3.1))
        plt.xlim((0,time+1))
        plt.axhline(y=0.5, color='k', linestyle='--', linewidth=0.5, alpha = 0.8)
        legend = plt.legend(fancybox = True,framealpha=True, loc = 'upper right', shadow = False)
        fig3.savefig('%smrt%s.pdf' %(directory,mrt_id))
        f.close()


def export_figs_mimo(ans):

  if ans == '2':
    fig_label = '$\mathit{Kalman}\/_\mathit{(MIMO)}$'
  if ans == '4':
    fig_label = '$\mathcal{H}_{\infty}\/_\mathit{(MIMO)}$'
  if ans == '6':
    fig_label = '$\mathit{MCC-KF}\/_\mathit{(MIMO)}$'

  directory = os.path.join("experiments/")
  for root,dirs,files in os.walk(directory):
    for file in files:
      timelist = []
      timelist.extend(range(0, 50))
      time = 50
      qerr = []
       
      if file.startswith("log_sp"):
        f=open("%s%s" %(directory,file), 'r')
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
        archive_cov = np.genfromtxt(log_file, usecols=(9), delimiter=',', dtype=None)

        qerr1 = np.sqrt(archive_var1)
        qerr2 = np.sqrt(archive_var2)
           
        fig1 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        plt.xticks(range(0,time+1,5))
        plt.ylim((0, 100))
        plt.xlim((0, time))
        plt.errorbar(timelist,archive_u1,yerr=qerr1,ecolor='k',linestyle="None", alpha = 0.2)
        plt.plot(archive_a1, 'r', linestyle='-', marker='+', label='$\mathit{allocation}$', linewidth=1.0)
        plt.plot(archive_u1, 'k', linestyle='-', label='$\mathit{usage}$', linewidth=1.0)
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{CPU}$ $\mathit{(\%)}$')
        legend = plt.legend(fancybox=True, framealpha=True, loc='upper left', shadow=False)
        fig1.savefig('%sweb_cpu%s.pdf' %(directory,cpu_id))

        fig2 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        plt.xticks(range(0,time+1,5))
        plt.ylim((0, 100))
        plt.xlim((0, time))
        plt.errorbar(timelist,archive_u2,yerr=qerr2,ecolor='k',linestyle="None", alpha = 0.2)
        plt.plot(archive_a2, 'r', linestyle='-', marker='+', label='$\mathit{allocation}$', linewidth=1.0)
        plt.plot(archive_u2, 'k', linestyle='-', label='$\mathit{usage}$', linewidth=1.0)
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{CPU}$ $\mathit{(\%)}$')
        legend = plt.legend(fancybox=True, framealpha=True, loc='upper left', shadow=False)
        fig2.savefig('%sdb_cpu%s.pdf' %(directory,cpu_id))

        fig3 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.ylim((0, 1.5+0.1))
        plt.xlim((0, time))
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{gain}$')
        plt.plot(archive_K1, '-b*', label = fig_label)
        legend = plt.legend(fancybox = True,framealpha=True, loc = 'lower right', shadow = False)
        fig3.savefig('%sweb_gain%s.pdf' %(directory,cpu_id))

        fig4 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.ylim((0, 1.5+0.1))
        plt.xlim((0, time))
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{gain}$')
        plt.plot(archive_K2, '-b*', label = fig_label)
        legend = plt.legend(fancybox = True,framealpha=True, loc = 'lower right', shadow = False)
        fig4.savefig('%sdb_gain%s.pdf' %(directory,cpu_id))
        f.close()

      if file.startswith("mrt"):
        f=open("%s%s" %(directory,file), 'r')
        mrt_file = directory + file
        mrt_id = file[3:-4] # removes from string log.txt

        mrts = np.genfromtxt(mrt_file, usecols=(0), delimiter=',', dtype=None)

        fig5 = plt.figure(figsize=(9, 4.5), dpi=100)
        plt.plot(mrts,'-b', label = fig_label, linewidth=1.0)
        plt.yticks(np.arange(0, 3.1, 0.5))
        plt.xticks(range(0,time+1,5))        
        plt.xlabel('$\mathit{sample}$ $\mathit{point}$')
        plt.ylabel('$\mathit{mRT}$ $\mathit{(s)}$')
        plt.ylim((0,3.1))
        plt.xlim((0,time+1))
        plt.axhline(y=0.5, color='k', linestyle='--', linewidth=0.5, alpha = 0.8)
        legend = plt.legend(fancybox = True,framealpha=True, loc = 'upper right', shadow = False)
        fig5.savefig('%smrt%s.pdf' %(directory,mrt_id))
        f.close()
