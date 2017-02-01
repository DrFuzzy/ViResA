#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 17:31:55 2015

@author: Dr. Kyriakos M. Deliparaschos
"""

import numpy as np
#import matplotlib.pyplot as plt
#import skfuzzy.membership as membership
#from skfuzzy import gaussmf, gbellmf, sigmf
import anfis

# import skfuzzy.membership as mf
class Estimators(object):
    """ Class that contains all estimators """

    def __init__(self, Q, R, c):
        self.Q = Q
        self.R = R
        self.c = c
    
    def kalman_siso(self, ap, P, u):
        """ Evaluate the SISO Kalman filter """
    
        P_new = P + self.Q
        K = self.c * P_new / ((self.c ** 2) * P_new + self.R)
        a = ap + K * (u - self.c * ap)
        P = (1 - self.c * K) * P_new

        if a > 100:
            a = 100
        elif a < 0:
            a = 0
        elif a < u:
            a = u

        return (a, P, K)

    def hinf_siso(self, ap, P, u):
        """ Evaluate the Hinf filter """

        theta = 0.7
        P_new = P + self.Q
        K = self.c * P_new / (1 + (self.c ** 2) * P_new * (self.R ** (-1)) - theta) * self.R
        a = ap + K * (u - self.c * ap)
        P = P_new / (1 + (self.c ** 2) * P_new * (self.R ** (-1)) - theta)

        # check validity of the condition:
        if (P ** (-1)) - theta + (self.c ** 2) / self.R <= 0:
            theta = self.R / ((self.c ** 2) * P) - 0.1

        if a > 100:
            a = 100
        elif a < 0:
            a = 0
        elif a < u:
            a = u

        return (a, P, K)

    def anfis_train(self, path):
        """ Create and then train the ANFIS structure (estimates the MF's parameters) """

        ts = np.loadtxt(path, usecols=[1, 2])  # ts, training set
        X = ts[:, 0:1]
        Y = ts[:, 1]

        # mf =
        # [[['gaussmf',{'mean':25.,'sigma':10.}],['gaussmf',{'mean':40.,'sigma':10.}],['gaussmf',{'mean':55.,'sigma':10.}],
        # ['gaussmf',{'mean':70.,'sigma':10.}],
        # ['gaussmf',{'mean':90.,'sigma':10.}]]]
        mf = [[['gbellmf', {'a': 9.7417, 'b': 2., 'c': 22.9247}], ['gbellmf', {'a': 9.7417, 'b': 2., 'c': 42.4081}], ['gbellmf', {
            'a': 9.7417, 'b': 2., 'c': 61.8915}], ['gbellmf', {'a': 9.7417, 'b': 2., 'c': 81.3749}], ['gbellmf', {'a': 9.7417, 'b': 2., 'c': 100.8583}]]]

        mfc = anfis.membershipfunction.MemFuncs(mf)
        # global anf
        anf = anfis.anfis.ANFIS(X, Y, mfc)
        anf.trainHybridJangOffLine(epochs=20)
        #print round(anf.consequents[-1][0],6)
        #print round(anf.consequents[-2][0],6)
        #print round(anf.fittedValues[9][0],6)

        #if round(anf.consequents[-1][0],6) == -5.275538 and round(anf.consequents[-2][0],6) == -1.990703 and round(anf.fittedValues[9][0],6) == 0.002249:
        #   print 'test is good'

        anf.plotErrors()
        anf.plotResults()

        return anf

    def anfis_siso(self, u, ANFIS_obj):
        """ Evaluate the ANFIS """

        # Layer 1: Fuzzify Input / Output
        mu = np.empty(len(ANFIS_obj.memFuncs[0])) # Input Membership Functions

        for mf in range(len(ANFIS_obj.memFuncs[0])):
            mu[mf] = anfis.membershipfunction.gbellmf(u, **ANFIS_obj.memClass.MFList[0][mf][1])
            #    # Plot input Fuzzy Sets across the Universe of Discourse
            #    U = np.arange(min(X),max(X),1)
            #    FS = np.empty([len(U),len(anf.memFuncs[0])])    
            #    for mf in range(len(anf.memFuncs[0])):
            #        FS[:,mf] = gbellmf(U,**anf.memClass.MFList[0][mf][1])        
            #    plt.plot(U,FS)    
        
        # Layer 2:    
        w = mu  # SISO, hence reduces to w = mu (here only for consistency with the paper)

        # Layer 3:
        w_bar = np.empty(len(ANFIS_obj.memFuncs[0]))
        f = np.empty(len(ANFIS_obj.memFuncs[0]))
        y = np.empty(len(ANFIS_obj.memFuncs[0]))
        j = 0       

        for mf in range(len(ANFIS_obj.memFuncs[0])):
        #        sum_mu = 0  
        #        for i in range(len(anf.memFuncs[0])):
        #            sum_mu = sum_mu+mu[i]
            w_sum = sum(w)
        
            # Layer 4:
            w_bar[mf] = w[mf] / w_sum # Determine the weight for each rule from fuzzy antecedents (first half of “Apply Implication Method” in Matlab tutorial)
            f[mf] = u * ANFIS_obj.consequents[j] + ANFIS_obj.consequents[j + 1] # Output MFs (1order polynomial)
            y[mf] = w_bar[mf] * f[mf] # Apply implication operator (min or product)
            j = j + 2

        # Layer 5:
        y = np.sum(y) # Aggregate all outputs

        # y = anfis.predict(ANFIS_obj,u) # Alternative implementation from anfis module (to use comment all code above!)   
        return y
    
# Test
#anf = anfis_train()
#ts = np.loadtxt("kalman_training_set.txt", usecols=[1,2])
#X = ts[:,0:1]
#Y = ts[:,1]
#Y_train = np.empty(len(X))
#
#for x in range(len(X)):
#   Y_train[x] = anfis_siso(X[x], anf)
##    Y_train[x] = anfis_siso(np.array([X[x]]), anf) # for use with anfis.predict()
## Y_train = anfis_siso(X, anf) # for use with anfis.predict() 
## y = anfis_siso(np.array([[40]]), anf) # for use with anfis.predict()
## y = anfis_siso(40, anf)
#
#plt.figure(1)
#plt.plot(Y, 'b', label='Kalman')
#plt.plot(Y_train, 'r', label='ANFIS')
#plt.legend(loc='upper right')
#plt.figure(2)
#plt.plot(X, 'b', label='input')
#plt.plot(Y_train, 'r', label='output')
#plt.legend(loc='upper right')
