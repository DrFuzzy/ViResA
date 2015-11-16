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
    plt.plot(u, mrt, linewidth=1.2)
    plt.xlabel('CPU Demand/CPU allocation', fontsize=12)
    plt.ylabel('mRT (s)', fontsize=12)
    # dotted region    
    plt.plot(u[0:800], np.ones(800), 'k--')
    plt.plot(0.8*np.ones(101), x, 'k--')

    return
    
# Test
#x = mrt_cost( array([1,2,3,4]).T,array([5,6,7,8]).T,1,1 )
#mrt_model()