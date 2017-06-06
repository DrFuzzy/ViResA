#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 16:56:08 2015

@author: Dr. Kyriakos M. Deliparaschos
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import sys
import subprocess
from time import sleep
from datetime import datetime
from cStringIO import StringIO

import operation
import estimators
import metrics

# additional features in archive folder
# from xen_control_functions import *
# from cpu_usages import *


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

        1  - Kalman SISO
        2  - Kalman MIMO
        3  - Hinf SISO
        4  - Hinf MIMO
        5  - Fuzzy Kalman SISO
        6  - Fuzzy Hinf SISO
        7  - Fuzzy Kalman MIMO
        8  - Fuzzy Hinf MIMO
        9  - MCC-KF SISO
	10 - MCC-KF MIMO
	11 - Comparison
	12 - Manual Control
        q  - Quit'''

    print menulist # no parentheses, menulist is not a function
    ans = raw_input('\033[93m' + '#? ' + '\033[0m')

    # initialize variables
    if ans == '1' or ans == '3' or ans == '5' or ans == '6' or ans== '9' or '11':
        real_data = 0
        # variables for Kalman SISO, Hinf SISO, MCC-KF SISO
        F = 1
        P = 10
        R = 1
        Q = 4
        c = 0.70 # ECC'16: 0.95 , ETFA'17: 0.70
        # set the initial required demand (D) and initialize CPU usage (u)
        D = 60
        u = D
        # set the initial allocation (a)
        a = 100

        # for comparison
        a1 = 100
        a2 = 100
        a3 = 100
        a4 = 100

        # for average cpu usage
        cntr = 0
        sum_cpu = 0
        avg_cpu = 0
        # delay of controller adaptation
        delay = 1
        # initialize the allocation at 100% on domain (eg. -d 1 for domain 1)
        os.system("xl sched-credit -d 5 -c %s" %a )
        # define archives
        archive_K = np.zeros((time, np.size(a)))
        archive_a = np.zeros((time, np.size(a)))
        archive_u = np.zeros((time, np.size(u)))
        archive_D = np.zeros((time, np.size(D)))

        # for comparison
        archive_a1 = np.zeros((time, np.size(a)))
        archive_a2 = np.zeros((time, np.size(a)))
        archive_a3 = np.zeros((time, np.size(a)))
        archive_a4 = np.zeros((time, np.size(a)))

    elif ans == '2' or ans == '4' or ans == '7' or ans == '8':
        # not implemented yet!
        fake = True


#####################################################################################################################################################
##
##	1 - Kalman SISO
##
#####################################################################################################################################################

    # choose which controller to use    
    if ans == '1':
        print('\nKalman SISO')
        a_in = np.zeros((time, np.size(a)))
        obs = np.zeros((time, np.size(a)))
        a_out = np.zeros((time, np.size(a)))
        
        data_type = True
        while data_type:
           datalist = '''\nData acquisition type ('q' to quit).     
             1 - Synthetic Data
             2 - Real Data
             q - Quit'''
           print datalist # no parentheses, datalist is not a function
           data_type = raw_input('\033[93m' + '#? ' + '\033[0m')
        
           ###################################### Kalman SISO (Synthetic Data) ##########################################
           if data_type == '1':
             real_data = 0
             print "\nSynthetic Data"
             
             # innovation
             for t in range(time): 
               if random_gen == 1:
                 y = u+np.sqrt(R)*np.random.RandomState.randn(state)
               elif random_gen == 2:
                 y = u+np.sqrt(R)*(1-2*np.random.RandomState.rand(state))
                 
               a_in[t] = a # save current allocation
               obs[t] = y # save current observed utilization
  
               # Kalman SISO
               (a,P,K) = estimators.kalman_siso(P, Q, R, c, y, a) # predict the new allocation      
               a_out[t] = a # save predicted allocation

               # find the current CPU usage:
               (u,q) = operation.current_cpu_usage(ans, D, a, u)
             
               # archives for Demand and K
               archive_D[t] = D
               archive_K[t] = K

               # change demand
               D = operation.demand(ans, t, time, D, demand_scheme, q, random_gen, Q);

               # archives
               archive_a[t] = a
               archive_u[t] = y

             # save training data objects with timestamp
             path = './training_data/kalman-synthetic-%s.dat'%datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
             data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
             np.savetxt(path, data)
             # save training data objects
             path = './training_data/kalman-synthetic.dat'
             data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
             np.savetxt(path, data)
             #np.savetxt(path, (a_in, obs, a_out))
             data_type = False

           ###################################### Kalman SISO (Real Data) ######################################
           elif data_type == '2':
             print "\nReal Data"
             real_data = 1
             try:
               # connection to Client Server & begin Client Emulator (workload generation) 
               print "\nConnecting to Client..."
               #os.system("ssh root@10.190.12.56 screen -d -m /root/run_client_emulator.sh ") # client connection and exit (install screen on remote machine)
               os.system("ssh root@10.190.12.56 screen -d -m /root/initialize.sh ")
               os.system("rm response.txt")
          
               # capture cpu usage every 1 sec for 300 secs for Tomcat Domain name
               print "\nCPU usage%:"
               cmd1 = ("xentop -b -d 1 -i 300 | awk '/Tomcat/ {print $4 fflush(stdout) }' &")        
               p1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
               stdout = []

               # capture current cpu allocation
               cmd2 = ("xl sched-credit | awk '/Tomcat/ {print $4} '")
               p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
               a_string = p2.stdout.readline()
               a = int(a_string)

               # convert string cpu usage into float and start estimator for (time) seconds
               for t in range(time):
                 line = p1.stdout.readline()
                 stdout.append(line)
                 y = float(line)
                 print "Current CPU usage: %d" %y
                 if line == '' and p.poll() != None:
                   break
                 
                 # save current observed utilization & current allocation      
                 obs[t] = y
                 a_in[t] = a
               
                 # Kalman SISO
                 (a,P,K) = estimators.kalman_siso(P, Q, R, c, y, a) # predict the new allocation          
                 print "Predicted Allocation: %d \n" %a
            
                 # adapt the predicted allocation
                 if t > delay:    
                   cntr += 1
                   sum_cpu = sum_cpu + y
                   a_out[t] = a # save predicted allocation
                   os.system("xl sched-credit -d 5 -c %s" %a ) # set the predicted allocation (cpu cap)
               
                 # archives
                 archive_a[t] = a
                 archive_u[t] = y
                 archive_D[t] = y
	         archive_K[t] = K          
                
               # compute average cpu usage after delay 
               avg_cpu = sum_cpu / cntr  
               print "Average CPU usage: %d" %avg_cpu 
               # save training data objects with timestamp
               path = './training_data/kalman-%s.dat'%datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
               data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
               np.savetxt(path, data)
               # save training data objects
               path = './training_data/kalman.dat'
               data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
               np.savetxt(path, data)
               #np.savetxt(path, (a_in, obs, a_out))
               data_type = False

             except IOError as e:
               print("\n({})\n".format(e))
               ans = True 
           
           elif data_type == 'q':
             print('\nGood bye!')
             data_type = None
             ans = None

           else:
             print('\033[91m' + '\nInvalid option. Try another one!\n' + '\033[0m')
             data_type = True


#####################################################################################################################################################
##
##	2 - Kalman MIMO
##
#####################################################################################################################################################

    elif ans == '2':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')


#####################################################################################################################################################
##
##	3 - Hinf SISO
##
#####################################################################################################################################################

    elif ans == '3':
      print('\nHinf SISO')
      a_in = np.zeros((time, np.size(a)))
      obs = np.zeros((time, np.size(a)))
      a_out = np.zeros((time, np.size(a)))
      
      data_type = True
      while data_type:
        datalist = '''\nData acquisition type ('q' to quit).     
             1 - Synthetic Data
             2 - Real Data
             q - Quit'''
        
        print datalist # no parentheses, menulist is not a function
        data_type = raw_input('\033[93m' + '#? ' + '\033[0m')
        
        ###################################### Hinf SISO (Synthetic Data) ##########################################
        if data_type == '1':
          real_data = 0
          print "\nSynthetic Data"
     
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

          # save training data objects with timestamp
          path = './training_data/hinf-synthetic-%s.dat'%datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
          data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
          np.savetxt(path, data)
          # save training data objects
          path = './training_data/hinf-synthetic.dat'
          data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
          np.savetxt(path, data)
          data_type = False


        ###################################### Hinf SISO (Real Data) ##########################################
        elif data_type == '2':
          real_data = 1
          print "\nReal Data"
          
          # connection to Client Server & begin Client Emulator (workload generation) 
          print "Connecting to Client..."   
          #os.system("ssh root@10.190.12.56 screen -d -m /root/run_client_emulator.sh ") # client connection and exit (install screen on remote machine)
          os.system("ssh root@10.190.12.56 screen -d -m /root/initialize.sh ")
          os.system("rm response.txt") 

          # capture cpu usage every 1 sec for 300 secs for Tomcat Domain name
          print "\nCPU usage%:"
          cmd1 = ("xentop -b -d 1 -i 300 | awk '/Tomcat/ {print $4 fflush(stdout) }' &")        
          p1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          stdout = []

          # capture current cpu allocation
          cmd2 = ("xl sched-credit | awk '/Tomcat/ {print $4} '")
          p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
          a_string = p2.stdout.readline()
          a = int(a_string)

          # convert string cpu usage into float and start estimator for (time) seconds
          for t in range(time):    
            line = p1.stdout.readline()
            stdout.append(line)
            y = float(line)
            print "Current CPU usage: %d" %y
            if line == '' and p.poll() != None:
              break
            
            # save current observed utilization & current allocation      
            a_in[t] = a
            obs[t] = y           
  
            # Hinf SISO
            (a,P,K) = estimators.hinf_siso(P, Q, R, c, y, a) # predict the new allocation          
            print "Predicted Allocation: %d \n" %a
               
            # adapt the predicted allocation
	    if t > delay:    
              cntr += 1
              sum_cpu = sum_cpu + y
              a_out[t] = a # save predicted allocation
              os.system("xl sched-credit -d 5 -c %s" %a ) # set the new allocation (cpu cap)

            # archives
            archive_a[t] = a
            archive_u[t] = y
            archive_D[t] = D
            archive_K[t] = K
   
          # compute average cpu usage after delay 
          avg_cpu = sum_cpu / cntr  
          print "Average CPU usage: %d" %avg_cpu 
          # save training data objects with timestamp
          path = './training_data/hinf-%s.dat'%datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
          data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
          np.savetxt(path, data)
          # save training data objects
          path = './training_data/hinf.dat'
          data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
          np.savetxt(path, data)
          #np.savetxt(path, (a_in, obs, a_out))
          data_type = False
           
        elif data_type == 'q':
          print('\nGood bye!')
          data_type = None
          ans = None

        else:
          print('\033[91m' + '\nInvalid option. Try another one!\n' + '\033[0m')
          data_type = True


#####################################################################################################################################################
##
##	4 - Hinf MIMO
##
#####################################################################################################################################################
        
    elif ans == '4':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')


#####################################################################################################################################################
##
##	5 - Fuzzy Kalman SISO
##
#####################################################################################################################################################
    
    elif ans == '5':
        print('\nFuzzy Kalman SISO')
        a_in = np.zeros((time, np.size(a)))
        obs = np.zeros((time, np.size(a)))
        a_out = np.zeros((time, np.size(a)))
      
        data_type = True
        while data_type:
          datalist = '''\nData acquisition type ('q' to quit).     
               1 - Synthetic Data
               2 - Real Data
               q - Quit'''
        
          print datalist # no parentheses, menulist is not a function
          data_type = raw_input('\033[93m' + '#? ' + '\033[0m')
        
          ###################################### Fuzzy Kalman SISO (Synthetic Data) ##########################################
          if data_type == '1':
            real_data = 0
            print "\nSynthetic Data"
      
            # check if a training data file exists
            path = './training_data/kalman-synthetic.dat'
            if os.path.exists(path) == False:
              print "No trained data found !"
            else:
              print "Trained data found !"

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
        
          ###################################### Fuzzy Kalman SISO (Real Data) ##########################################
          elif data_type == '2':
            real_data = 1
            print "\nReal Data"

            # check if a training data file exists
            path = './training_data/kalman.dat'
            if os.path.exists(path) == False:
              print "No trained data found !"
            else:
              print "Trained data found !"

              try:
                # http://effbot.org/zone/python-with-statement.htm
                # with is more safe to open file
                with open(path) as fh: 
                    # do something with fh
                    obs = np.zeros((time, np.size(a)))
                    a_out = np.zeros((time, np.size(a)))
       
                    # estimate ANFIS parameters based on Kalman training data         
                    anf = estimators.anfis_train(path)
                    
                    # connection to Client Server & begin Client Emulator (workload generation) 
                    print "Connecting to Client..."
                    #os.system("ssh root@10.190.12.56 screen -d -m /root/run_client_emulator.sh ") # client connection and exit (install screen on remote machine)
                    os.system("ssh root@10.190.12.56 screen -d -m /root/initialize.sh ")
                    os.system("rm response.txt")     

                    # capture cpu usage every 1 sec for 300 secs for Tomcat Domain name
                    print "\nCPU usage%:"
                    cmd1 = ("xentop -b -d 1 -i 300 | awk '/Tomcat/ {print $4 fflush(stdout) }' &") # monitoring web server cpu usages for 180 secs
                    p1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    stdout = []

                    # capture current cpu allocation
                    cmd2 = ("xl sched-credit | awk '/Tomcat/ {print $4} '")
                    p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
                    a_string = p2.stdout.readline()
                    a = int(a_string)
      
                    # convert string cpu usage into float and start estimator for (time) seconds
                    for t in range(time):    
                      line = p1.stdout.readline()
                      stdout.append(line)
                      y = float(line)
                      print "Current CPU usage: %d" %y
                      if line == '' and p.poll() != None:
                        break

                      # save current observed utilization & current allocation      
                      obs[t] = y
                      a_in[t] = a

                      # Fuzzy Kalman SISO
                      a = estimators.anfis_siso(y, anf);

                      # allocation contraint        
                      if a < 1:
                          a = 1
                      elif a > 100:
                          a = 100

                      print "Predicted Allocation: %d \n" %a

                      # adapt the predicted allocation
	    	      if t > delay:    
                        cntr += 1
                        sum_cpu = sum_cpu + y
                        a_out[t] = a # save predicted allocation
                        os.system("xl sched-credit -d 5 -c %s" %a ) # set the new allocation (cpu cap)
                      
                      # archives
                      archive_a[t] = a
                      archive_u[t] = y
                      archive_D[t] = y
                      #archive_K[t] = K
        
                    # compute average cpu usage after delay 
                    avg_cpu = sum_cpu / cntr  
                    print "Average CPU usage: %d" %avg_cpu 
                    path = './training_data/fuzzy_kalman-%s.dat'%datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
                    data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
                    np.savetxt(path, data)
                    data_type = False

              except IOError as e:
                print("\n({})\n".format(e))
                ans = True           

          elif data_type == 'q':
             print('\nGood bye!')
             data_type = None
             ans = None


#####################################################################################################################################################
##
##	6 - Fuzzy Hinf SISO
##
#####################################################################################################################################################

    elif ans == '6':
        print('\nFuzzy Hinf SISO')
        a_in = np.zeros((time, np.size(a)))
        obs = np.zeros((time, np.size(a)))
        a_out = np.zeros((time, np.size(a)))
      
        data_type = True
        while data_type:
          datalist = '''\nData acquisition type ('q' to quit).     
               1 - Synthetic Data
               2 - Real Data
               q - Quit'''
        
          print datalist # no parentheses, menulist is not a function
          data_type = raw_input('\033[93m' + '#? ' + '\033[0m')

          ###################################### Fuzzy Hinf SISO (Synthetic Data) ##########################################
          if data_type == '1':
            real_data = 0
            print "\nSynthetic Data"

            # check if a training data file exists
            path = './training_data/hinf-synthetic.dat'
            if os.path.exists(path) == False:
              print "No trained data found !"
            else:
              print "Trained data found !"

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

          ###################################### Fuzzy Hinf SISO (Real Data) ##########################################
          elif data_type == '2':
            real_data = 1
            print "\nReal Data"

            # check if a training data file exists
            path = './training_data/hinf.dat'
            if os.path.exists(path) == False:
              print "No trained data found !"
            else:
              print "Trained data found !"
              
              try:
                # http://effbot.org/zone/python-with-statement.htm
                # with is more safe to open file
                with open(path) as fh: 
                    # do something with fh
                    obs = np.zeros((time, np.size(a)))
                    a_out = np.zeros((time, np.size(a)))
       
                    # estimate ANFIS parameters based on Kalman training data         
                    anf = estimators.anfis_train(path)
  
                    # connection to Client Server & begin Client Emulator (workload generation) 
                    print "Connecting to Client..." 
                    #os.system("ssh root@10.190.12.56 screen -d -m /root/run_client_emulator.sh ") # client connection and exit (install screen on remote machine)
                    os.system("ssh root@10.190.12.56 screen -d -m /root/initialize.sh ")
                    os.system("rm response.txt")  

                    # capture cpu usage every 1 sec for 300 secs for Tomcat Domain name
                    print "\nCPU usage%:"
                    cmd1 = ("xentop -b -d 1 -i 300 | awk '/Tomcat/ {print $4 fflush(stdout) }' &") # monitoring web server cpu usages for 180 secs
                    p1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    stdout = []

                    # capture current cpu allocation
                    cmd2 = ("xl sched-credit | awk '/Tomcat/ {print $4} '")
                    p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
                    a_string = p2.stdout.readline()
                    a = int(a_string)
      
                    # convert string cpu usage into float and start estimator for (time) seconds
                    for t in range(time):    
                      line = p1.stdout.readline()
                      stdout.append(line)
                      y = float(line)
                      print "Current CPU usage: %d" %y
                      if line == '' and p.poll() != None:
                        break

                      # fuzzy Hinf SISO
                      a = estimators.anfis_siso(y, anf);

                      # allocation contraint        
                      if a < 1:
                          a = 1
                      elif a > 100:
                          a = 100

                      print "Predicted Allocation: %d \n" %a

                      # adapt the predicted allocation
	    	      if t > delay:    
                        cntr += 1
                        sum_cpu = sum_cpu + y
                        a_out[t] = a # save predicted allocation
                        os.system("xl sched-credit -d 5 -c %s" %a ) # set the new allocation (cpu cap)
                      
                      # archives
                      archive_a[t] = a
                      archive_u[t] = y
                      archive_D[t] = y
                      #archive_K[t] = K
        
                    # compute average cpu usage after delay 
                    avg_cpu = sum_cpu / cntr  
                    print "Average CPU usage: %d" %avg_cpu
                    path = './training_data/fuzzy_hinf-%s.dat'%datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
                    data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
                    np.savetxt(path, data)
                    data_type = False

              except IOError as e:
                print("\n({})\n".format(e))
                ans = True           

          elif data_type == 'q':
             print('\nGood bye!')
             data_type = None
             ans = None
         

#####################################################################################################################################################
##
##	7 - Fuzzy Kalman MIMO
##
#####################################################################################################################################################

    elif ans == '7':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')
    

#####################################################################################################################################################
##
##	8 - Fuzzy Hinf MIMO
##
#####################################################################################################################################################

    elif ans == '8':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')


#####################################################################################################################################################
##
##	9 - MCC-KF SISO
##
#####################################################################################################################################################

    elif ans == '9':
        print('\nMCC Kalman SISO')
        a_in = np.zeros((time, np.size(a)))
        obs = np.zeros((time, np.size(a)))
        a_out = np.zeros((time, np.size(a)))
        
        data_type = True
        while data_type:
           datalist = '''\nData acquisition type ('q' to quit).     
             1 - Synthetic Data
             2 - Real Data
             q - Quit'''
           print datalist # no parentheses, menulist is not a function
           data_type = raw_input('\033[93m' + '#? ' + '\033[0m')
        
           ###################################### MCC - Kalman SISO (Synthetic Data) ##########################################
           if data_type == '1':
             real_data = 0
             print "\nSynthetic Data"
             
             # innovation
             for t in range(time): 
               if random_gen == 1:
                 y = u+np.sqrt(R)*np.random.RandomState.randn(state)
               elif random_gen == 2:
                 y = u+np.sqrt(R)*(1-2*np.random.RandomState.rand(state))
                 
               a_in[t] = a # save current allocation
               obs[t] = y # save current observed utilization
  
               # MCC-KF SISO
               (a,P,K) = estimators.mcc_kf_siso(P, Q, R, c, y, a) # predict the new allocation      
               a_out[t] = a # save predicted allocation

               # find the current CPU usage:
               (u,q) = operation.current_cpu_usage(ans, D, a, u)
             
               # archives for Demand and K
               archive_D[t] = D
               archive_K[t] = K

               # change demand
               D = operation.demand(ans, t, time, D, demand_scheme, q, random_gen, Q);

               # archives
               archive_a[t] = a
               archive_u[t] = y


             # save training data objects
             path = './training_data/mcckf-synthetic.dat'
             data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
             np.savetxt(path, data)
             #np.savetxt(path, (a_in, obs, a_out))
             data_type = False

           ###################################### MCC - Kalman SISO (Real Data) ######################################
           elif data_type == '2':
             real_data = 1
             print "\nReal Data"
             
             # connection to Client Server & begin Client Emulator (workload generation) 
             print "\nConnecting to Client..."
             #os.system("ssh root@10.190.12.56 screen -d -m /root/run_client_emulator.sh ") # client connection and exit (install screen on remote machine)
             os.system("ssh root@10.190.12.56 screen -d -m /root/initialize.sh ")
             os.system("rm response.txt")

             # capture cpu usage every 1 sec for 300 secs for Tomcat Domain name
             print "\nCPU usage%:"
             cmd1 = ("xentop -b -d 1 -i 300 | awk '/Tomcat/ {print $4 fflush(stdout) }' &")        
             p1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
             stdout = []

             # capture current cpu allocation
             cmd2 = ("xl sched-credit | awk '/Tomcat/ {print $4} '")
             p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
             a_string = p2.stdout.readline()
             a = int(a_string)

             # convert string cpu usage into float and start estimator for (time) seconds
             for t in range(time):
               line = p1.stdout.readline()
               stdout.append(line)
               y = float(line)
               print "Current CPU usage: %d" %y
               if line == '' and p.poll() != None:
                 break
                 
               # save current observed utilization & current allocation      
               obs[t] = y
               a_in[t] = a
               
               # MCC-KF SISO
               (a,P,K) = estimators.mcc_kf_siso(P, Q, R, c, y, a) # predict the new allocation   
               print "Predicted Allocation: %f \n" %a
            
               # adapt the predicted allocation
               if t > delay:    
                 cntr += 1
                 sum_cpu = sum_cpu + y
                 a_out[t] = a # save predicted allocation
                 os.system("xl sched-credit -d 5 -c %s" %a ) # set the predicted allocation (cpu cap)

               # archives
               archive_a[t] = a
               archive_u[t] = y
               archive_D[t] = y
	       archive_K[t] = K          
                
             # compute average cpu usage after delay 
             avg_cpu = sum_cpu / cntr  
             print "Average CPU usage: %d" %avg_cpu 
             # save training data objects with timestamp
             path = './training_data/mcckf-%s.dat'%datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
             data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
             np.savetxt(path, data)
             # save training data objects
             path = './training_data/mcckf.dat'
             data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
             np.savetxt(path, data)
             #np.savetxt(path, (a_in, obs, a_out))
             data_type = False
           
           elif data_type == 'q':
             print('\nGood bye!')
             data_type = None
             ans = None

           else:
             print('\033[91m' + '\nInvalid option. Try another one!\n' + '\033[0m')
             data_type = True  


#####################################################################################################################################################
##
##	10 - MCC-KF MIMO
##
#####################################################################################################################################################

    elif ans == '10':
        print('\033[93m' + '\nNot implemented yet!\n' + '\033[0m')   


#####################################################################################################################################################
##
##	11 - Comparison
##
#####################################################################################################################################################

    elif ans == '11':
             print('\nComparison')
             a_in1 = np.zeros((time, np.size(a)))
             a_in2 = np.zeros((time, np.size(a)))
             a_in3 = np.zeros((time, np.size(a)))
             obs = np.zeros((time, np.size(a)))
             a_out1 = np.zeros((time, np.size(a)))
             a_out2 = np.zeros((time, np.size(a)))
             a_out3 = np.zeros((time, np.size(a)))
             #a_out4 = np.zeros((time, np.size(a)))
        
             ###################################### Comparison (Real Data) ######################################
             data_type = '2'
             print "\nReal Data"
             real_data = 1
             time = 50
             try:
               # connection to Client Server & begin Client Emulator (workload generation) 
               print "\nConnecting to Client..."
               #os.system("ssh root@10.190.12.56 screen -d -m /root/run_client_emulator.sh ") # client connection and exit (install screen on remote machine)
               os.system("ssh root@10.190.12.56 screen -d -m /root/initialize.sh ")
               os.system("rm response.txt")
          
               # capture cpu usage every 1 sec for 300 secs for Tomcat Domain name
               print "\nCPU usage%:"
               cmd1 = ("xentop -b -d 1 -i 300 | awk '/Tomcat/ {print $4 fflush(stdout) }' &")        
               p1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
               stdout = []

               # capture current cpu allocation
               #cmd2 = ("xl sched-credit | awk '/Tomcat/ {print $4} '")
               #p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
               #a_string = p2.stdout.readline()
               #a = int(a_string)
               a1=100
               a2=100
               a3=100
              
               # convert string cpu usage into float and start estimator for (time) seconds
               for t in range(time):
                 line = p1.stdout.readline()
                 stdout.append(line)
                 y = float(line)
                 print "Current CPU usage: %d" %y
                 if line == '' and p.poll() != None:
                   break
                 
                 # save current observed utilization & current allocation      
                 obs[t] = y
                 a_in1[t] = a1
                 a_in2[t] = a2
                 a_in3[t] = a3

                 # Kalman SISO
                 (a1,P,K) = estimators.kalman_siso(P, Q, R, c, y, a1) # predict the new allocation
                 (a2,P,K) = estimators.hinf_siso(P, Q, R, c, y, a2) # predict the new allocation          
                 (a3,P,K) = estimators.mcc_kf_siso(P, Q, R, c, y, a3) # predict the new allocation
                 #a4 = estimators.anfis_siso(y, anf);        
                 #print "Predicted Allocation: %d \n" %a
            
                 # adapt the predicted allocation
                 if t > delay:    
                   cntr += 1
                   sum_cpu = sum_cpu + y
                   a_out1[t] = a1 # save predicted allocation
                   a_out2[t] = a2 # save predicted allocation
                   a_out3[t] = a3 # save predicted allocation
                   #a_out4[t] = a4 # save predicted allocation
                   #os.system("xl sched-credit -d 5 -c %s" %a ) # set the predicted allocation (cpu cap)
               
                 # archives
                 archive_a1[t] = a1
                 archive_a2[t] = a2
                 archive_a3[t] = a3
                 #archive_a4[t] = a4
                 archive_u[t] = y
                 archive_D[t] = y
	         archive_K[t] = K          
                
               # compute average cpu usage after delay 
               avg_cpu = sum_cpu / cntr  
               print "Average CPU usage: %d" %avg_cpu 
               data_type = False

             except IOError as e:
               print("\n({})\n".format(e))
               ans = True 
           

#####################################################################################################################################################
##
##	12 - Manual Control
##
#####################################################################################################################################################

    elif ans == '12':
             print('\nManual Control')
             a_in = np.zeros((time, np.size(a)))
             obs = np.zeros((time, np.size(a)))
             a_out = np.zeros((time, np.size(a)))
            
             ###################################### Manual Control (Real Data) ######################################
             data_type = '2'
             print "\nReal Data"
             real_data = 1
             try:
               # connection to Client Server & begin Client Emulator (workload generation) 
               print "\nConnecting to Client..."
               #os.system("ssh root@10.190.12.56 screen -d -m /root/run_client_emulator.sh ") # client connection and exit (install screen on remote machine)
               os.system("ssh root@10.190.12.56 screen -d -m /root/initialize.sh ")
               os.system("rm response.txt")
          
               # capture cpu usage every 1 sec for 300 secs for Tomcat Domain name
               print "\nCPU usage%:"
               cmd1 = ("xentop -b -d 1 -i 300 | awk '/Tomcat/ {print $4 fflush(stdout) }' &")        
               p1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
               stdout = []

               # capture current cpu allocation
               cmd2 = ("xl sched-credit | awk '/Tomcat/ {print $4} '")
               p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
               a_string = p2.stdout.readline()
               a = int(a_string)

               # convert string cpu usage into float and start estimator for (time) seconds
               for t in range(time):
                 line = p1.stdout.readline()
                 stdout.append(line)
                 y = float(line)
                 print "Current CPU usage: %d" %y
                 if line == '' and p.poll() != None:
                   break
                 
                 # save current observed utilization & current allocation      
                 obs[t] = y
                 a_in[t] = a

                 if t <= 20 and t > 0:
		    a = 100
		 elif t <= 40 and t > 20:
		    a = 80
		 elif t <= 60 and t > 40:
		    a = 60
		 elif t <= 80 and t > 60:
		    a = 40
		 elif t <= 100 and t > 80:
		    a = 20
		 else:
		    a = 100
           
                 print "Predicted Allocation: %f \n" %a

                 # adapt the predicted allocation
                 if t > delay:    
                   cntr += 1
                   sum_cpu = sum_cpu + y
                   a_out[t] = a # save predicted allocation
                   os.system("xl sched-credit -d 5 -c %s" %a ) # set the predicted allocation (cpu cap)
               
                 # archives
                 archive_a[t] = a
                 archive_u[t] = y   
                 archive_D[t] = y             
                
               # compute average cpu usage after delay 
               avg_cpu = sum_cpu / cntr  
               print "Average CPU usage: %d" %avg_cpu 
               # save training data objects with timestamp
               path = './training_data/non_controlled-%s.dat'%datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
               data = np.vstack((a_in[:,0],obs[:,0],a_out[:,0])).T
               np.savetxt(path, data)
               data_type = False

             except IOError as e:
               print("\n({})\n".format(e))
               ans = True 
           


    elif ans == 'q':
        print('\nGood bye!')
        ans = None


    else:
        print('\033[91m' + '\nInvalid option. Try another one!\n' + '\033[0m')
        ans = True


#####################################################################################################################################################
##
##	PLOTS and METRICS
##
#####################################################################################################################################################
    
    if ans == '1' or ans=='3' or ans=='5' or ans=='6' or ans == '9' or ans == '12':
        plt.figure(1)
	plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        plt.xticks([0,10,20,30,40, 50, 60, 70, 80, 90, 100])
        plt.ylim((0,100))
        plt.xlim((0,time))
        plt.plot(archive_a,'r',linestyle='-',marker='+', label='$\mathit{allocation}$' , linewidth=1.0)
        plt.plot(archive_u,'k',linestyle='-', label='$\mathit{usage}$' , linewidth=1.0)
        plt.xlabel('$\mathit{time}$ $\mathit{interval}$ $\mathit{(s)}$')
        plt.ylabel('$\mathit{CPU}$ $\mathit{(\%)}$')
        legend = plt.legend(fancybox = True,framealpha=True, loc = 'lower right', shadow = False)

        if real_data == 0:
          plt.figure(2)
          cost = metrics.mrt_cost(archive_D, archive_a, phi, gamma)
	  plt.yticks([0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000])
          plt.xticks([0,10,20,30,40, 50, 60, 70, 80, 90, 100])
          plt.plot(cost,'-b', linewidth=1.0)
          plt.xlabel('$\mathit{time}$ $\mathit{interval}$ $\mathit{(s)}$')
          plt.ylabel('$\mathit{mRT}$ $\mathit{(ms)}$')
    
        elif real_data == 1:
          os.system("scp root@ent01cl001:/root/RUBiS/response.txt /root/ViReSa_real_data/response.txt")
          metrics.real_mrt_plot(ans)

        else:
          print "Error" 

        plt.figure(3)
        plt.xlabel('$\mathit{time}$ $\mathit{interval}$ $\mathit{(s)}$')
        plt.ylabel('$\mathit{gain}$')
        plt.plot(archive_K,'-b*')
        plt.show()
 

    elif ans == '2':
        # reserved        
        pass

    elif ans == '4':
        # reserved        
        pass
    
    elif ans == '7':
        # reserved        
        pass

    elif ans == '8':
        # reserved        
        pass

    elif ans == '10':
        # reserved        
        pass

    elif ans == '11':
        plt.figure(1)
        #set(gca,'FontSize',14);
	plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        plt.xticks([0,10,20,30,40, 50, 60, 70, 80, 90, 100])#, 150, 200])
        plt.ylim((0,100))
        plt.xlim((0,time))
        plt.plot(archive_a1,'b', label='$\mathit{Kalman}$' , linewidth=1.0)
        plt.plot(archive_a2,'g', label='$\mathcal{H}_{\infty}$' , linewidth=1.0)
        plt.plot(archive_a3,'r', label='$\mathit{MCC-KF}$' , linewidth=1.0)
        #plt.plot(archive_a4,'c', label='Fuzzy' , linewidth=1.0)
        plt.plot(archive_u,'k', label='$\mathit{usage}$' , linewidth=1.0)
        plt.xlabel('$\mathit{time}$ $\mathit{interval}$ $\mathit{(s)}$')
        plt.ylabel('$\mathit{CPU}$ $\mathit{(\%)}$')
        legend = plt.legend(fancybox = True,framealpha=True, loc = 'lower right', shadow = False)
        plt.show()
        #plt.box(on=True)
   
    else:
        pass
 
'''        
        else:
          print "Error"  

    if ans == '1':
        plt.show() # force plot now and then return to main code
        RMS_kalman = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('Kalman RMS estimation error ='), RMS_kalman
        print('Kalman mRT ='), np.mean(cost)

    if ans == '3':
        plt.show() # force plot now and then return to main code
        RMS_hinf = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('Hinf RMS estimation error ='), RMS_hinf
        print('Hinf mRT ='), np.mean(cost)

    if ans == '5':    
        plt.show() # force plot now and then return to main code
        RMS_fuzzykalman = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('Fuzzy Kalman RMS estimation error ='), RMS_fuzzykalman
        print('Fuzzy Kalman mRT ='), np.mean(cost)
    
    if ans == '6':
        plt.show() # force plot now and then return to main code
        RMS_fuzzyhinf = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('Fuzzy Hinf RMS estimation error ='), RMS_fuzzyhinf
        print('Fuzzy Hinf mRT ='), np.mean(cost)

    if ans == '9':
        plt.show() # force plot now and then return to main code
        RMS_mcckf = np.sqrt(np.linalg.norm(archive_u-c*archive_a)**2/time)
        print('MCC-KF RMS estimation error ='), RMS_mcckf
        print('MCC-KF mRT ='), np.mean(cost)

    
    elif ans == '2':
        # reserved        
        pass

    elif ans == '4':
        # reserved        
        pass
    
    elif ans == '7':
        # reserved        
        pass

    elif ans == '8':
        # reserved        
        pass

    elif ans == '10':
        # reserved        
        pass
    
    else:
        pass
'''
