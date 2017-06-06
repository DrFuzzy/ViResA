#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 23:52:18 2015

@author: Dr. Kyriakos M. Deliparaschos
"""

import numpy as np

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
        
        return mrt    
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
def real_mrt_plot(controller):
  import csv
  import matplotlib.pyplot as plt

  total = 0
  time = 0
  start = 0
  counter = 0
  mrt = 0
  limit = 0
  currenttime = 0
  resptime = 0 
  cntr = 0
  mrt_list = [0]*2000

  # read the last timestamp from file
  with open ('response.txt',"r") as f1:
    data1 = f1.readlines()
    end = data1[len(data1)-1]
    last = int(end.split('\t', 1)[0])

  with open ('response.txt',"r") as f:
    time = 0
    resp = 0

    # read the first timestamp from file to begin start and limit
    data = f.readline()
    start = int(data.split('\t', 1)[0])
    limit = start + 1000 
  
    # read every line and split them to currenttime and resptime
    for line in f:
        currenttime , resptime = map(int,(item.strip() for item in line.split('\t')))
    
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
          limit = currenttime + 1000
         
  f.close()

  mrts=[0]*(cntr)
  for i in range(cntr):
    if i > 1:
      mrts[i-1] = mrt_list[i-1]

  # Plots
  plt.figure(2)
  #set(gca,'FontSize',14);
  if controller == '1':
    plt.plot(mrts,'-b', label = '$\mathit{Kalman}$', linewidth=1.0)
  elif controller == '3':
    plt.plot(mrts,'-b', label = '$\mathcal{H}_{\infty}$', linewidth=1.0)
  elif controller == '5':
    plt.plot(mrts,'-b', label = '$\mathit{Fuzzy}$ $\mathit{(Kalman)}$', linewidth=1.0)
  elif controller == '6':
    plt.plot(mrts,'-b', label = '$\mathit{Fuzzy}$ $\mathit{(}$$\mathcal{H}_{\infty}$$\mathit{)}$', linewidth=1.0)
  elif controller == '9':
    plt.plot(mrts,'-b', label = '$\mathit{MCC-KF}$', linewidth=1.0)
  elif controller == '12':
    plt.plot(mrts,'-b', label = '$\mathit{Non}$ $\mathit{Controlled}$', linewidth=1.0)
  else:
    print "Error plotting mRT\n"

  plt.yticks([0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000])
  plt.xticks([0,10,20,30,40, 50, 60, 70, 80, 90, 100])
  plt.xlabel('$\mathit{time}$ $\mathit{interval}$ $\mathit{(s)}$')
  plt.ylabel('$\mathit{mRT}$ $\mathit{(ms)}$')
  plt.ylim((0,3000))
  plt.xlim((0,100))
  plt.axhline(y=1000, color='k', linestyle='--', linewidth=0.5)
  legend = plt.legend(fancybox = True,framealpha=True, loc = 'upper right', shadow = False)
  #plt.box(on=True)
  plt.show()
    
# Test
#x = mrt_cost( array([1,2,3,4]).T,array([5,6,7,8]).T,1,1 )
#mrt_model()
