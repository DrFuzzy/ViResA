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

def covariance(N,data,y,obs1,obs2):
  QN = 0.0
  y1 = y[0]
  y2 = y[1]
  if data > N:
    obs1 = obs1[1:] + [y1]
    obs2 = obs2[1:] + [y2]
    QN = np.cov(obs1,obs2, ddof=1)
  else:
    obs1.append(y1)
    obs2.append(y2)
    QN = np.cov(obs1,obs2, bias=1)
  return QN,obs1,obs2




