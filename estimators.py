#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 17:31:55 2015

@author: Dr. Kyriakos M. Deliparaschos
"""

# import matplotlib.pyplot as plt
# import skfuzzy.membership as membership
# from skfuzzy import gaussmf, gbellmf, sigmf
import anfis
import numpy as np


# Attributes
# ----------
# x: State estimate vector
# y: Measurement (or observation)
# P: Covariance matrix
# W: Measurement noise matrix
# V: Process noise matrix
# A: State Transition matrix
# C: Measurement function
# r: Residual of the update step.
# K: Kalman gain of the update step
# S: Systen uncertaintly projected to measurement space

# Function definitions

# This function evaluates the SISO usage-based controller 
def usage_based_siso(p, l, r, u, ap):
    a = (p * u) + l * (r - ap + u)

    return a

# This function evaluates the SISO Kalman filter 
def kalman_siso(P, W, V, c, u, ap):
    P_new = P + W
    K = c * P_new / ((c ** 2) * P_new + V)
    a = ap + K * (u - c * ap)
    P = (1 - c * K) * P_new

    return a, P, K


# This function evaluates the MIMO Kalman filter
def kalman_mimo(P, W, V, C, y, x):
    A = np.array([[1, 0],[0, 1]])  # process equation
    # Time Update (Prediction)
    # ========================
    # Project the state ahead
    x = A.dot(x)
    # Project the error covariance ahead
    P = A.dot(P) + W

    # Measurement Update (Correction)
    # ===============================
    # Compute the Kalman Gain
    S = C.dot(P).dot(C) + V
    K = C.dot(P).dot(np.linalg.pinv(S))

    # Update the state estimate
    r = y - C.dot(x)  # innovation term (measurement residual)
    x = x + K.dot(r)

    # Update the error covariance
    P = np.eye(len(x)) - C.dot(K).dot(P)
    
    return x, P, K


# This function evaluates the SISO Hinf filter
def hinf_siso(P, Q, R, c, u, ap):
    theta = 0.7

    P_new = P + Q
    K = c * P_new / (1 + (c ** 2) * P_new * (R ** (-1)) - theta) * R
    a = ap + K * (u - c * ap)
    P = P_new / (1 + (c ** 2) * P_new * (R ** (-1)) - theta)

    # check validity of the condition:
    if (P ** (-1)) - theta + (c ** 2) / R <= 0:
        theta = R / ((c ** 2) * P) - 0.1

    return a, P, K


# This function evaluates the MIMO Hinf filter
def hinf_mimo(P, W, V, C, y, x):
    A = np.array([[1, 0],[0, 1]])  # process equation
    V_inv = np.linalg.pinv(V)
    C_tr = np.transpose(C)
    A_tr = np.transpose(A)
    theta = 0.1
    I = np.eye(len(x))

    # Predict
    x_new = A.dot(x)
    P_new = A.dot(P).dot(A_tr) + W

    # Update
    L = np.linalg.pinv(I - theta*P_new + C_tr.dot(V_inv).dot(C).dot(P_new))
    K = P_new.dot(L).dot(C_tr).dot(V_inv)
    r = y - C.dot(x_new)  # innovation term (measurement residual)
    x = x_new + K.dot(r)
    P = P_new.dot(L)

    return x, P, K

# This function evaluates the SISO MCC Kalman filter
def mcc_kf_siso(P, W, V, c, y, x):
    V_inv = V
    # Prior estimation
    x_n = x
    P_n = P + W

    # Posterior estimation
    P_p = P_n
    r = y - c * x  # innovation term (measurement residual)
    r_norm = np.sqrt(r * V_inv * r)
    sigma = 50
    L = np.exp(-(r_norm ** 2) / (2 * sigma ** 2))
    K = 1 / ((1 / P_p) + L * c * V_inv * c) * (L * c * V_inv)
    x_n = x_n + K * r
    P_n = (1 - K * c) * P_p * (1 - K * c) + K * V * K

    return x_n, P_n, K


# This function evaluates the MIMO MCC Kalman filter
def mcc_kf_mimo(P, W, V, C, y, x):
    A = np.array([[1, 0],[0, 1]])  # process equation
    A_tr = np.transpose(A)
    C_tr = np.transpose(C)
    V_inv = np.linalg.pinv(V)
    I = np.eye(len(x))
    sigma = 100

    # Prior estimation (Prediction)
    x_new = A.dot(x)
    P_new = A.dot(P).dot(A_tr) + W

    # Posterior estimation (Update)
    P_inv = np.linalg.pinv(P_new)
    r = y - C.dot(x_new) # innovation term (measurement residual)
    r_norm = np.sqrt(r.dot(V_inv).dot(r))
    dom = x_new - A.dot(x_new)
    dom_norm = np.sqrt(dom.dot(P_inv).dot(dom))

    L = (np.exp(-(r_norm ** 2) / (2 * sigma ** 2)))
    K = np.linalg.pinv(P_inv + (L*C_tr).dot(V_inv).dot(C)).dot(L*C_tr).dot(V_inv)
    x_n = x_new + K.dot(r)
    P_n = (I - K.dot(C)).dot(P_new).dot(np.transpose(I - K.dot(C))) + K.dot(V).dot(np.transpose(K))

    return x_n, P_n, K


# This function trains the ANFIS structure (estimates the MF's parameters)
def anfis_train(path):
    ts = np.loadtxt(path, usecols=[1, 2])  # ts, training set
    X = ts[:, 0:1]
    Y = ts[:, 1]

    # mf = [[['gaussmf',{'mean':25.,'sigma':10.}],['gaussmf',{'mean':40.,'sigma':10.}],
    #        ['gaussmf',{'mean':55.,'sigma':10.}], ['gaussmf',{'mean':70.,'sigma':10.}],
    #        ['gaussmf',{'mean':90.,'sigma':10.}]]]
    mf = [[['gbellmf', {'a': 9.7417, 'b': 2., 'c': 22.9247}], ['gbellmf', {'a': 9.7417, 'b': 2., 'c': 42.4081}],
           ['gbellmf', {'a': 9.7417, 'b': 2., 'c': 61.8915}], ['gbellmf', {'a': 9.7417, 'b': 2., 'c': 81.3749}],
           ['gbellmf', {'a': 9.7417, 'b': 2., 'c': 100.8583}]]]

    mfc = anfis.membershipfunction.MemFuncs(mf)
    # global anf
    anf = anfis.anfis.ANFIS(X, Y, mfc)
    anf.trainHybridJangOffLine(epochs=20)
    #    print round(anf.consequents[-1][0],6)
    #    print round(anf.consequents[-2][0],6)
    #    print round(anf.fittedValues[9][0],6)

    # if round(anf.consequents[-1][0],6) == -5.275538 and round(anf.consequents[-2][0],6) == -1.990703:
    #     if round(anf.fittedValues[9][0], 6) == 0.002249:
    #         print 'test is good'

    anf.plotErrors()
    anf.plotResults()

    return anf


# This function evaluates the ANFIS
def anfis_siso(u, ANFIS_obj):
    """
    Layer 1: Fuzzify Input / Output     
    """
    # Input Membership Functions
    mu = np.empty(len(ANFIS_obj.memFuncs[0]))

    for mf in range(len(ANFIS_obj.memFuncs[0])):
        mu[mf] = anfis.membershipfunction.gbellmf(u, **ANFIS_obj.memClass.MFList[0][mf][1])

    #    # Plot input Fuzzy Sets across the Universe of Discourse
    #    U = np.arange(min(X),max(X),1)
    #    FS = np.empty([len(U),len(anf.memFuncs[0])])
    #    for mf in range(len(anf.memFuncs[0])):
    #        FS[:,mf] = anfis.membershipfunction.gbellmf(U,**anf.memClass.MFList[0][mf][1])
    #    plt.plot(U,FS)
    """
    Layer 2:
    """
    w = mu  # SISO, hence reduces to w = mu (only here for consistency with paper)

    """
    Layer 3:
    """
    w_bar = np.empty(len(ANFIS_obj.memFuncs[0]))
    f = np.empty(len(ANFIS_obj.memFuncs[0]))
    y = np.empty(len(ANFIS_obj.memFuncs[0]))
    j = 0

    for mf in range(len(ANFIS_obj.memFuncs[0])):
        #        sum_mu = 0
        #        for i in range(len(anf.memFuncs[0])):
        #            sum_mu = sum_mu+mu[i]
        w_sum = sum(w)

        """
        Layer 4:
        """
        # Determine the weight for each rule from fuzzy antecedents
        # (first half of “Apply Implication Method” in Matlab tutorial)
        w_bar[mf] = w[mf] / w_sum
        # Output MFs (1order polynomial)
        f[mf] = u * ANFIS_obj.consequents[j] + ANFIS_obj.consequents[j + 1]
        # Apply implication operator (min or product)
        y[mf] = w_bar[mf] * f[mf]
        j = j + 2

    """
    Layer 5:
    """
    # Aggregate all outputs
    y = np.sum(y)

    # Alternative implementation from anfis module (comment all code above!)   
    # y = anfis.predict(ANFIS_obj,u)

    return y


# Test
"""
anf = anfis_train()

ts = np.loadtxt("kalman_training_set.txt", usecols=[1,2])
X = ts[:,0:1]
Y = ts[:,1]
Y_train = np.empty(len(X))

for x in range(len(X)):
   Y_train[x] = anfis_siso(X[x], anf)
#    Y_train[x] = anfis_siso(np.array([X[x]]), anf) # for use with anfis.predict()

#Y_train = anfis_siso(X, anf) # for use with anfis.predict() 
#y = anfis_siso(np.array([[40]]), anf) # for use with anfis.predict()
#y = anfis_siso(40, anf)

plt.figure(1)
plt.plot(Y, 'b', label='Kalman')
plt.plot(Y_train, 'r', label='ANFIS')
plt.legend(loc='upper right')

plt.figure(2)
plt.plot(X, 'b', label='input')
plt.plot(Y_train, 'r', label='output')
plt.legend(loc='upper right')
"""
