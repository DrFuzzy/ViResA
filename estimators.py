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