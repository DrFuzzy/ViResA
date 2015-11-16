#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 16:56:08 2015

@author: Dr. Kyriakos M. Deliparaschos
"""

#import os
import numpy as np
import matplotlib.pyplot as plt

import operation
import estimators
import metrics

"""
 This function studies the performance of various methods for state
 estimation of the usage and allocation in virtualised servers.
"""
#def server_consolidation

#os.system('clear')
# Global Parameters:
time = 100
s = 4
random_gen = 2
demand_scheme = 6
gamma = 10
phi = 0.8

# save generator's state in order to be able to use the same random numbers 
# in other algorithms and compare their performance.
state = np.random.RandomState(seed = s)

ans = True
while ans:
    menulist = '''\nChoose a controller from the menu ('q' to quit).

        1 - Kalman SISO
        2 - Kalman MIMO
        3 - Hinf SISO
        4 - Hinf MIMO
        5 - Fuzzy Kalman SISO
        6 - Fuzzy Hinf SISO
        7 - Fuzzy Kalman MIMO
        8 - Fuzzy Hinf MIMO
        q - Quit'''

    print menulist # no parentheses, menulist is not a function
    ans = raw_input('\033[93m' + '#? ' + '\033[0m')

    # initialize variables
    if ans == '1' or ans == '3' or ans == '5' or ans == '6':
        # variables for Kalman SISO and Hinf SISO
        P = 10
        R = 1
        Q = 4
        c = 0.95
        # set the initial required demand (D) and initialize CPU usage (u)
        D = 60
        u = D
        # set the initial allocation (a)
        a = 100
        # define archives
        archive_K = np.zeros((time, np.size(a)))
        archive_a = np.zeros((time, np.size(a)))
        archive_u = np.zeros((time, np.size(u)))
        archive_D = np.zeros((time, np.size(D)))

    elif ans == '2' or ans == '4' or ans == '7' or ans == '8':
        # not implemented yet!
        fake = True

    # choose which controller to use    
    if ans == '1':
        print('\nKalman SISO')
        a_in = np.zeros((time, np.size(a)))
        obs = np.zeros((time, np.size(a)))
        a_out = np.zeros((time, np.size(a)))
        
        for t in range(time):
            # innovation
            if random_gen == 1:
               y = u+np.sqrt(R)*np.random.RandomState.randn(state)
            elif random_gen == 2:
               y = u+np.sqrt(R)*(1-2*np.random.RandomState.rand(state))

            a_in[t] = a # save current allocation
            obs[t] = y # save current observed utilization

            # Kalman SISO
            (a,P,K) = estimators.kalman_siso(P, Q, R, c, y, a)
        
            a_out[t] = a # save predicted allocation

            # find the current CPU usage:
            (u,q) = operation.current_cpu_usage(ans, D, a, u)

            # archives
            archive_a[t] = a
            archive_u[t] = u
            archive_D[t] = D
            archive_K[t] = K

            # change demand
            D = operation.demand(ans, t, time, D, demand_scheme, q, random_gen, Q);
        
        # save training data objects
        path = './kalman.dat'
        data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
        np.savetxt(path, data)
        #np.savetxt(path, (a_in, obs, a_out))

    elif ans == '2':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')

    elif ans == '3':
        print('\nHinf SISO')
        a_in = np.zeros((time, np.size(a)))
        obs = np.zeros((time, np.size(a)))
        a_out = np.zeros((time, np.size(a)))
        
        for t in range(time):
            # innovation
            if random_gen == 1:
               y = u+np.sqrt(R)*np.random.RandomState.randn(state)
            elif random_gen == 2:
               y = u+np.sqrt(R)*(1-2*np.random.RandomState.rand(state))

            a_in[t] = a # save current allocation
            obs[t] = y # save current observed utilization

            # Hinf SISO            
            (a,P,K) = estimators.hinf_siso(P, Q, R, c, y, a)
        
            a_out[t] = a # save predicted allocation

            # find the current CPU usage:
            (u,q) = operation.current_cpu_usage(ans, D, a, u)

            # archives
            archive_a[t] = a
            archive_u[t] = u
            archive_D[t] = D
            archive_K[t] = K
            
            # change demand
            D = operation.demand(ans, t, time, D, demand_scheme, q, random_gen, Q);

        # save training data objects
        path = './hinf.dat'
        data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
        np.savetxt(path, data)
        
    elif ans == '4':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')
    
    elif ans == '5':
        print('\nFuzzy Kalman SISO')
        
        # check if a training data file exists
        path = './kalman.dat'
        try:
            # http://effbot.org/zone/python-with-statement.htm
            # with is more safe to open file
            with open(path) as fh: 
                # do something with fh
                obs = np.zeros((time, np.size(a)))
                a_out = np.zeros((time, np.size(a)))
       
                # estimate ANFIS parameters based on Kalman training data         
                anf = estimators.anfis_train(path)

                for t in range(time):
                    # innovation
                    if random_gen == 1:
                        y = u+np.sqrt(R)*np.random.RandomState.randn(state)
                    elif random_gen == 2:
                        y = u+np.sqrt(R)*(1-2*np.random.RandomState.rand(state))

                    # fuzzy Kalman SISO
                    a = estimators.anfis_siso(y, anf);

                    # allocation contraint        
                    if a < 1:
                        a = 1
                    elif a > 100:
                        a = 100

                    # find the current CPU usage:
                    (u,q) = operation.current_cpu_usage(ans, D, a, u)

                    # archives
                    archive_a[t] = a
                    archive_u[t] = u
                    archive_D[t] = D
                    #archive_K[t] = K
        
                    # change demand
                    D = operation.demand(ans, t, time, D, demand_scheme, q, random_gen, Q)
        except IOError as e:
            print("\n({})\n".format(e))
            ans = True            

    elif ans == '6':
        print('\nFuzzy Hinf SISO')
      
        # check if a training data file exists
        path = './hinf.dat'
        try:
            # http://effbot.org/zone/python-with-statement.htm
            # with is more safe to open file
            with open(path) as fh: 
                # do something with fh
                obs = np.zeros((time, np.size(a)))
                a_out = np.zeros((time, np.size(a)))
       
                # estimate ANFIS parameters based on Kalman training data         
                anf = estimators.anfis_train(path)

                for t in range(time):
                    # innovation
                    if random_gen == 1:
                        y = u+np.sqrt(R)*np.random.RandomState.randn(state)
                    elif random_gen == 2:
                        y = u+np.sqrt(R)*(1-2*np.random.RandomState.rand(state))

                    # fuzzy Hinf SISO
                    a = estimators.anfis_siso(y, anf);
                    
                    # find the current CPU usage:
                    (u,q) = operation.current_cpu_usage(ans, D, a, u)

                    # archives
                    archive_a[t] = a
                    archive_u[t] = u
                    archive_D[t] = D
                    #archive_K[t] = K
        
                    # change demand
                    D = operation.demand(ans, t, time, D, demand_scheme, q, random_gen, Q);
        except IOError as e:
            print("\n({})\n".format(e))
            ans = True            

    elif ans == '7':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')
    
    elif ans == '8':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')

    elif ans == 'q':
        print('\nGood bye!')
        ans = None

    else:
        print('\033[91m' + '\nInvalid option. Try another one!\n' + '\033[0m')
        ans = True


    # PLOTS and METRICS
    if ans == '1':
        plt.figure(1)
        #set(gca,'FontSize',14);
        plt.plot(archive_a, '-b', linewidth=1.5)
        plt.plot(archive_u,'k', linewidth=1.5)
        plt.xlabel('time interval')
        plt.ylabel('CPU (%)')
        #plt.box(on=True)

        plt.figure(2)
        #set(gca,'FontSize',14);
        cost_kalman = metrics.mrt_cost(archive_D, archive_a, phi, gamma)
        plt.plot(cost_kalman,'-b', linewidth=1.5)
        plt.xlabel('time interval')
        plt.ylabel('mRT (s)')
        #plt.box(on=True)

        plt.figure(3)
        plt.xlabel('time interval')
        plt.ylabel('gain')
        #set(gca,'FontSize',12);
        plt.plot(archive_K,'-b*')
        #plt.box(on=True)

        plt.show() # force plot now and then return to main code

        RMS_kalman = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('Kalman RMS estimation error ='), RMS_kalman
        print('Kalman mRT ='), np.mean(cost_kalman)

    elif ans == '2':
        # reserved        
        pass
    
    elif ans == '3':
        plt.figure(1)
        #set(gca,'FontSize',14);
        plt.plot(archive_a, '-b', linewidth=1.5)
        plt.plot(archive_u,'k', linewidth=1.5)
        plt.xlabel('time interval')
        plt.ylabel('CPU (%)')
        #plt.box(on=True)

        plt.figure(2)
        #set(gca,'FontSize',14);
        cost_hinf = metrics.mrt_cost(archive_D, archive_a, phi, gamma)
        plt.plot(cost_hinf,'-b', linewidth=1.5)
        plt.xlabel('time interval')
        plt.ylabel('mRT (s)')
        #plt.box(on=True)

        plt.figure(3)
        plt.xlabel('time interval')
        plt.ylabel('gain')
        #set(gca,'FontSize',12);
        plt.plot(archive_K,'-b*')
        #plt.box(on=True)

        plt.show() # force plot now and then return to main code

        RMS_hinf = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('Hinf RMS estimation error ='), RMS_hinf
        print('Hinf mRT ='), np.mean(cost_hinf)

    elif ans == '4':
        # reserved        
        pass

    elif ans == '5':
        plt.figure(1)
        #set(gca,'FontSize',14);
        plt.plot(archive_a, '-b', linewidth=1.5)
        plt.plot(archive_u,'k', linewidth=1.5)
        plt.xlabel('time interval')
        plt.ylabel('CPU (%)')
        #plt.box(on=True)

        plt.figure(2)
        #set(gca,'FontSize',14);
        cost_fuzzykalman = metrics.mrt_cost(archive_D, archive_a, phi, gamma)
        plt.plot(cost_fuzzykalman,'-b', linewidth=1.5)
        plt.xlabel('time interval')
        plt.ylabel('mRT (s)')
        #plt.box(on=True)
        
        plt.show() # force plot now and then return to main code

        RMS_fuzzykalman = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('Fuzzy Kalman RMS estimation error ='), RMS_fuzzykalman
        print('Fuzzy Kalman mRT ='), np.mean(cost_fuzzykalman)
    
    elif ans == '6':
        plt.figure(1)
        #set(gca,'FontSize',14);
        plt.plot(archive_a, '-b', linewidth=1.5)
        plt.plot(archive_u,'k', linewidth=1.5)
        plt.xlabel('time interval')
        plt.ylabel('CPU (%)')
        #plt.box(on=True)

        plt.figure(2)
        #set(gca,'FontSize',14);
        cost_fuzzyhinf = metrics.mrt_cost(archive_D, archive_a, phi, gamma)
        plt.plot(cost_fuzzyhinf,'-b', linewidth=1.5)
        plt.xlabel('time interval')
        plt.ylabel('mRT (s)')
        #plt.box(on=True)
        
        plt.show() # force plot now and then return to main code

        RMS_fuzzyhinf = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('Fuzzy Hinf RMS estimation error ='), RMS_fuzzyhinf
        print('Fuzzy Hinf mRT ='), np.mean(cost_fuzzyhinf)
    
    elif ans == '7':
        # reserved        
        pass

    elif ans == '8':
        # reserved        
        pass
    
    else:
        pass