#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  10 10:36:14 2017

@author: Evagoras Makridis
"""

import numpy as np
import math

def variance(N,data,y,obs):
  QN = 0.0
  if data > N:
    obs = obs[1:] + [y]
    QN = np.var(obs)
  else:
    obs.append(y)
    QN = np.var(obs)
  return QN,obs

def covariance(N,data,y,sw1,sw2): # sw: sliding window
  QN = 0.0
  if data > N:
    sw1 = sw1[1:] + [y[0]]
    sw2 = sw2[1:] + [y[1]]
    QN = np.cov(sw1,sw2, ddof=1)
  else:
    sw1.append(y[0])
    sw2.append(y[1])
    QN = np.cov(sw1,sw2, bias=1)
  return QN,sw1,sw2




