#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 17:07:45 2015

@author: Dr. Kyriakos M. Deliparaschos
"""

import numpy as np
#import matplotlib.pyplot as plt

# Function definitions

# This function changes the demand throughout the operation of the system
def demand(control, t, time, D, demand_scheme, q, random_gen, Q):
    if demand_scheme == 1:
        if control == '1' or control == '3' or control == '5' or control == '6':
            # change the workload at specific time instants
            if t == 30:
                D = 100
            elif t == 50:
                D = 30   

            if random_gen == 1:
                D = D+(np.sqrt(Q)*np.random.standard_normal(1)+q)
            elif random_gen == 2:
                D = D+(np.sqrt(Q)*(1-2*np.random.uniform(0,1))+q)
            else:
                print("Choose a valid noise distribution (1,2)!")
                return 
                
        elif control == '2' or control == '4':
            print("Not implemented yet!")
            return    
        
        else:
            print("Choose a valid control option (1-8)!")
            return

    elif demand_scheme == 2:
        if control == '1' or control == '3' or control == '5' or control == '6':
            # change the workload at specific time instants
            if t >= 20 and t < 50:
                D = 0.6-0.01*(t-20)
            elif t >= 50 or t < 80:
                D = 0.3+0.01*(t-50)
            elif t >= 80 and t <= time:
                D = 0.6

            if random_gen == 1:
                D = D+(np.sqrt(Q)*np.random.standard_normal(1)+q)
            elif random_gen == 2:
                D = D+(np.sqrt(Q)*(1-2*np.random.uniform(0,1))+q)
            else:
                print("Choose a valid noise distribution (1,2)!")
                return 
                
        elif control == '2' or control == '4':
            print("Not implemented yet!")
            return    

        else:
            print("Choose a valid control option (1-8)!")
            return  
            
    elif demand_scheme == 3:
        if control == '1' or control == '3' or control == '5' or control == '6':            
            if random_gen == 1:
                D = D+(np.sqrt(Q)*np.random.standard_normal(1)+q)
            elif random_gen == 2:
                D = D+(np.sqrt(Q)*(1-2*np.random.uniform(0,1))+q)
            else:
                print("Choose a valid noise distribution (1,2)!")
                return 
                
        elif control == '2' or control == '4':
            print("Not implemented yet!")
            return

        else:
            print("Choose a valid control option (1-8)!")
            return  
            
    elif demand_scheme == 4:
        if control == '1' or control == '3' or control == '5' or control == '6':
            # change the workload at specific time instants
            if t >= 1 and t < 15:
                D = 0.6-0.02*(t-1)
            elif t >= 15 or t < 25:
                D = 0.3
            elif t >= 25 and t <= 40:
                D = 0.6-0.02*(t-25)
            elif t >= 25 and t <= 40:
                D = 0.3
            elif t >= 50 and t <= 65:
                D = 0.6-0.02*(t-50)                
            elif t >= 65 and t <= 75:
                D = 0.3
            elif t >= 75 and t <= 90:
                D = 0.6-0.02*(t-75)
            elif t >= 90 and t <= time:
                D = 0.3
                
            if random_gen == 1:
                D = D+(np.sqrt(Q)*np.random.standard_normal(1)+q)
            elif random_gen == 2:
                D = D+(np.sqrt(Q)*(1-2*np.random.uniform(0,1))+q)
            else:
                print("Choose a valid noise distribution (1,2)!")
                return 
                
        elif control == '2' or control == '4':
            print("Not implemented yet!")
            return

        else:
            print("Choose a valid control option (1-8)!")
            return   
            
    elif demand_scheme == 5:
        if control == '1' or control == '3' or control == '5' or control == '6':
            # change the workload at specific time instants
            if t >= 10 and t < 30:
                D = 0.6+0.02*(t-10)
            elif t >= 30 or t < 50:
                D = 1.05
            elif t >= 50 and t <= 60:
                D = 0.6
            elif t >= 60 and t <= 80:
                D = 0.6+0.02*(t-60)
            elif t >= 80 and t <= 100:
                D = 1.05               
            elif t >= 100 and t <= time:
                D = 0.6
                
            if random_gen == 1:
                D = D+(np.sqrt(Q)*np.random.standard_normal(1)+q)
            elif random_gen == 2:
                D = D+(np.sqrt(Q)*(1-2*np.random.uniform(0,1))+q)
            else:
                print("Choose a valid noise distribution (1-2)!")
                return  
            
        elif control == '2' or control == '4':
            print("Not implemented yet!")
            return              

        else:
            print("Choose a valid control option (1-8)!")
            return    

    elif demand_scheme == 6:
        if control == '1' or control == '3' or control == '5' or control == '6':
            # change the workload at specific time instants
            if t >= 10 and t < 30: 
                D = 60+2*(t-10)
            elif t >= 30 and t < 40: 
                D = 105
            elif t >= 40 and t < 50:
                D = 60
            elif t >= 50 and t < 80: 
                D = 60-2*(t-60)
            elif t >= 80 and t <= 90:
                D = 60
            elif t >= 90 and t <= time:
                D = 30
                
            if random_gen == 1:
                D = D+(np.sqrt(Q)*np.random.standard_normal(1)+q)
            elif random_gen == 2:
                D = D+(np.sqrt(Q)*(1-2*np.random.uniform(0,1))+q)
            else:
                print("Choose a valid noise distribution (1-2)!")
                return

        elif control == '2' or control == '4':
            print("Not implemented yet!")
            return
            
        else:
            print("Choose a valid control option (1-8)!")
            return    

    else:
        print("Choose a valid demand scheme (1-6)!")
        return    
        
    return D

# This function computes the current CPU usage    
def current_cpu_usage(control, D, a, u):
    if control == '1' or control == '3' or control == '5' or control == '6':
        value = a - D

        # if demand is more than the allocation:
        if value < 0:
            # we can't have a usage larger than the allocation.
            u = a
        
            # just to make sure u is within the limits: 0 \leq u\leq a
            if u > a:
                u = a
            elif u < 0:
                u = 0

        # if the demand is less than the allocation
        else:
            u = D
            if u > a:
                u = a
            elif u < 0:
                u = 0

    elif control == '2':
        print("Not implemented yet!")
        return
    else:
        print("Choose a valid control option (1, 2, 3, 5, 6)!")
        return

    q = D - u
    return (u, q)
    
# Test
#u = current_cpu_usage(1, 2, 3, 1)
#D = demand(1, 20, 100, 60, 5, 0, 1, 4)
