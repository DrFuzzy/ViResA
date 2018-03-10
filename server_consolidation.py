#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 16:56:08 2015

@author: Dr. Kyriakos M. Deliparaschos
"""
import math
import os
import csv
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
import statistics
from datetime import datetime
from multiprocessing import Process

# additional features in archive folder
# from xen_control_functions import *
# from cpu_usages import *

"""
 This function studies the performance of various methods for state
 estimation of the usage and allocation in virtualized servers.
"""
# def server_consolidation

# os.system('clear')
# Global Parameters: 
time = 251 # 250 seconds
delay = 1  # the first measurement of cpu usage is always 0 because of Xen
date = ''
qos = 0.5  # Quality of Service in seconds (0.5 = 500ms)
s = 4
random_gen = 2
demand_scheme = 7
gamma = 10
phi = 0.8
N = 10  # variance and covariance window
timelist = np.zeros(time)  # keep timing logs
w = 0
a_min = 20
a_max = 100
# system variables
vm_name1 = 'Tomcat'
vm_name2 = 'MySQL'
a_initial = '100'

# save generator's state in order to be able to use the same random numbers
# in other algorithms and compare their performance.
state = np.random.RandomState(seed=s)

ans = True
while ans:
    w += 1
    menulist = '''\nChoose a controller from the menu ('q' to quit).
      1  - Kalman SISO
      2  - Kalman MIMO
      3  - Hinf SISO
      4  - Hinf MIMO
      5  - MCC-KF SISO
      6  - MCC-KF MIMO
      q  - Quit'''
    print menulist
    ans = raw_input('\033[93m' + '#? ' + '\033[0m')
    
    # initialize variables
    if ans == '1' or ans == '3' or ans == '5':
      real_data = 0
      # siso usage-based controller inputs
      # p = 1.25 # the lowest proportion of the utilisation that the allocation is assigned to and its values are > 1
      # l = 0.3 # proportion of the control error that is considered towards the final allocation
      # r = 50 # the extra allocation required
      # variables for Kalman SISO, Hinf SISO, MCC-KF SISO
      # component name (VM name)
      vm_name1 = 'Tomcat'
      vm_name2 = 'MySQL'
      F = 1
      P = 10
      R = 1
      Q = 4
      K = 1
      c = 0.7  # ECC'16: 0.95 , ETFA'17: 0.70
      # set the initial required demand (D) and initialize CPU usage (u)
      D = 50
      u = D
      # set the initial allocation (a)
      a = 100
      # allocation and usage logs
      a_in = np.zeros((time, np.size(a)))
      obs = np.zeros((time, np.size(a)))
      a_out = np.zeros((time, np.size(a)))
      obs_win = []
      # for average cpu usage
      cntr = sum_cpu = avg_cpu = 0
      # define archives
      archive_var = np.zeros((time, np.size(a)))
      archive_a = np.zeros((time, np.size(a)))
      archive_K = np.zeros((time, np.size(a)))
      archive_u = np.zeros((time, np.size(u)))
      archive_D = np.zeros((time, np.size(D)))
      # variance error
      qerr = np.zeros(time)
      var1 = 0
      var2 = 0
      cov = 0
      # usage
      usages = np.zeros(time)

    elif ans == '2' or ans == '4' or ans == '6':
      real_data = 0
      ca = 5 # control action interval
      sp = 0 # sampling point
      # variables for Kalman MIMO, Hinf MIMO, MCC-KF MIMO
      P = np.array([[0, 0], [0, 0]])
      R = np.array([[1, 0], [0, 1]])
      Q = np.array([[4, 0], [0, 4]])
      C = np.array([[0.7, 0], [0, 0.7]])  # ECC'16: 0.95 , ETFA'17: 0.70
      # set the initial required demand (D) and initialize CPU usage (u)
      D = np.array([50, 30])
      u = D
      y_1 = 0
      y_2 = 0
      a_1 = 100
      a_2 = 100
      cap1 = 100
      cap2 = 100
      # set the initial allocation for VMs
      a = np.array([100, 100])
      y = np.array([0, 0])
      y_mean = np.array([0, 0])
      y_hold = np.array([0, 0])
      K = np.array([[1, 1],[1, 1]])
      # allocation and usage logs
      a_in1 = np.zeros(time)
      a_in2 = np.zeros(time)
      a_in = np.zeros((time, np.size(a)))
      obs = np.zeros((time, np.size(a)))
      a_out = np.zeros((time, np.size(a)))
      obs1 = []
      obs2 = []
      # archives
      test = 0
      archive_D1 = np.zeros((time, np.size(D)))
      archive_D2 = np.zeros((time, np.size(D)))
      archive_K1 = np.zeros(time, dtype=object)
      archive_K2 = np.zeros(time, dtype=object)
      archive_a1 = np.zeros((time, np.size(test)))
      archive_a2 = np.zeros((time, np.size(test)))
      archive_alloc1 = np.zeros((time, np.size(test)))
      archive_alloc2 = np.zeros((time, np.size(test)))
      archive_u1 = np.zeros((time, np.size(test)))
      archive_u2 = np.zeros((time, np.size(test)))
      archive_usag1 = np.zeros((time, np.size(test)))
      archive_usag2 = np.zeros((time, np.size(test)))
      archive_var1 = np.zeros((time, np.size(test)))
      archive_var2 = np.zeros((time, np.size(test)))
      archive_cov = np.zeros((time, np.size(test)))
      archive_vr1 = np.zeros((time, np.size(test)))
      archive_vr2 = np.zeros((time, np.size(test)))
      archive_cv = np.zeros((time, np.size(test)))
      archive_y1hold = np.zeros((time, np.size(test)))
      archive_y2hold = np.zeros((time, np.size(test)))
      # variance errors
      qerr1 = np.zeros(time)
      qerr2 = np.zeros(time)
      # usage for both machines
      usage1 = np.zeros(time)
      usage2 = np.zeros(time)
      # for average variance
      cov_matrix = []
      var1 = 0
      var2 = 0
      cov = 0
      # for average cpu usage
      cntr = 0
      sum_cpu1 = 0
      sum_cpu2 = 0
      avg_cpu1 = 0
      avg_cpu2 = 0
      avg_cpu = np.array([0, 0])

  ####################################################################################################################
  #
  #  SISO Controllers
  #
  ####################################################################################################################

    if ans == '1' or ans == '3' or ans == '5':
      date = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
      #os.makedirs('./experiments/experiment-%s'%date)
      data_type = True
      while data_type:
        datalist = '''\nData acquisition type ('q' to quit).
        1 - Synthetic Data
        2 - Real Data
        q - Quit'''
        print datalist  # no parentheses, datalist is not a function
        #data_type = raw_input('\033[93m' + '#? ' + '\033[0m')
        data_type = '2'         
        # ##################################### (Synthetic Data) #######################################
        if data_type == '1':
          print "\nSynthetic Data"
          real_data = 0
          # innovation
          for t in range(time):
            if random_gen == 1:
              y = u + np.random.RandomState.randn(state)
            elif random_gen == 2:
              y = u + (1 - 2 * np.random.RandomState.rand(state))

            a_in[t] = a  # save current allocation
            obs[t] = y  # save current observed utilization
            usages[t] = y
            # calculate variance
            Q, obs_win = statistics.variance(N, t, y, obs_win)
            qerr[t] = math.sqrt(Q)

            # allocation prediction using the filters
            if ans == '1':
              (a, P, K) = estimators.kalman_siso(P, Q, R, c, y, a)  # Kalman SISO
            elif ans == '3':
              (a, P, K) = estimators.hinf_siso(P, Q, R, c, y, a)  # Hinf SISO
            elif ans == '5':
              (a, P, K) = estimators.mcc_kf_siso(P, Q, R, c, y, a)  # MCC-KF SISO

            cap = a/c
            if cap > 100:	# a_max = 100
              cap = 100
            if cap < y:
              cap = y
            if cap < a_min:
              cap = a_min

            a_out[t] = a  # save predicted allocation

            # find the current CPU usage:
            (u, q) = operation.current_cpu_usage(ans, D, a, u)
 
            # archives for Demand and K
            archive_D[t] = D
            archive_K[t] = K
            timelist[t] = t

            # change demand
            D = operation.demand(ans, t, time, D, demand_scheme, q, random_gen, Q)

            # archives
            archive_var[t] = Q
            archive_a[t] = a
            archive_u[t] = y

          # save training data objects with timestamp
          path = './training_data/kalman-synthetic-%s.dat' % datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
          data = np.vstack((a_in[:, 0], obs[:, 0], a_out[:, 0])).T
          np.savetxt(path, data)
          # save training data objects
          path = './training_data/kalman-synthetic.dat'
          data = np.vstack((a_in[:, 0], obs[:, 0], a_out[:, 0])).T
          np.savetxt(path, data)
          # np.savetxt(path, (a_in, obs, a_out))
          data_type = False


        # ##################################### (Real Data) #######################################
        elif data_type == '2':
          print "\nReal Data"
          real_data = 1
          try:

            def remote_code1():
              os.system("ssh root@10.190.12.57 python ~/viresa/manager.py %s %s %s %s" %(vm_name1, a_initial, str(ans), str(date)))

            def remote_code2():
              os.system("ssh root@10.190.12.58 python ~/viresa/manager.py %s %s %s %s" %(vm_name2, a_initial, str(ans), str(date)))

            if __name__ == '__main__':
              p1 = Process(target=remote_code1)
              p1.start()
              p2 = Process(target=remote_code2)
              p2.start()
              p1.join()
              p2.join()
              data_type = False

            print_figures = True
            while print_figures:
              printfigures = '''\nExport figures from logs?
              y - Yes
              n - No'''
              print printfigures  # no parentheses, datalist is not a function
              print_figures = raw_input('\033[93m' + '#? ' + '\033[0m')

              if print_figures == 'y':
                os.system("scp -r root@ent01cl002:viresa/experiments/*.txt /root/viresa/experiments/web/")
                os.system("scp -r root@ent01cl003:viresa/experiments/*.txt /root/viresa/experiments/db/")
                print "\nPrinting figures..."               
                metrics.export_figs_siso(ans, vm_name1)
                metrics.export_figs_siso(ans, vm_name2)
                print_figures = False

              elif print_figures == 'n':
                print_figures = False
                break

              else:
                print('\033[91m' + '\nInvalid option. Try another one!\n' + '\033[0m')
                print_figures = True

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

  ####################################################################################################################
  #
  #  MIMO Controllers
  #
  ####################################################################################################################

    elif ans == '2' or ans == '4' or ans == '6':
      date = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
      #os.makedirs('./experiments/experiment-%s'%date)
      data_type = True
      while data_type:
        datalist = '''\nData acquisition type ('q' to quit).
        1 - Synthetic Data
        2 - Real Data
        q - Quit'''
        print datalist  # no parentheses, datalist is not a function
        #data_type = raw_input('\033[93m' + '#? ' + '\033[0m')
        data_type = '2'         
 
        # ##################################### (Synthetic Data) #######################################
        if data_type == '1':
          print "\nSynthetic Data"
          real_data = 0
          # innovation
          for t in range(time):
            test += 1
            if random_gen == 1:
              y = u + np.sqrt(R[0,0]) * np.random.RandomState.randn(state)
            elif random_gen == 2:
              y = u + np.sqrt(R[0,0]) * (1 - 2 * np.random.RandomState.rand(state))

            print "Current cpu usage: "
            print y

            a_in[t] = a  # save current allocation
            obs[t] = y  # save current observed utilization PM1
            usage1[t] = y[0]
            usage2[t] = y[1]

            # calculate variance
            Q,obs1,obs2 = statistics.covariance(N,t,y,obs1,obs2)
            if t == delay:
              qerr1[t] = 0
              qerr2[t] = 0
            else:
              qerr1[t] = math.sqrt(Q[0,0])
              qerr2[t] = math.sqrt(Q[1,1])

            # allocation prediction using the filters
            if ans == '2':
              (a, P, K) = estimators.kalman_mimo(P, Q, R, C, y, a)  # Kalman MIMO
            elif ans == '4':
              (a, P, K) = estimators.hinf_mimo(P, Q, R, C, y, a)  # Hinf MIMO
            elif ans == '6':
              (a, P, K) = estimators.mcc_kf_mimo(P, Q, R, C, y, a)  # MCC-KF MIMO

            a_out[t] = a  # save predicted allocations

            print "Predicted cpu allocation: "
            print a

            # find the current CPU usage:
            (u, q) = operation.current_cpu_usage(ans, D, a, u)
            # change demand
            D = operation.demand(ans, t, time, D, demand_scheme, q, random_gen, Q)
		    
            # archives
            archive_D1[t] = D[0]
            archive_D2[t] = D[1]
            archive_a1[t] = a[0]
            archive_a2[t] = a[1]
            archive_u1[t] = y[0]
            archive_u2[t] = y[1]
            archive_var1[t] = Q[0,0]
            archive_var2[t] = Q[1,1]
            archive_cov[t] = Q[0,1]
            archive_K1[t] = K[0,0]
            archive_K2[t] = K[1,1]
            timelist[t] = t

          sleep(3)
          data_type = False

        # ######################################## (Real Data) #########################################
        elif data_type == '2':
          print "\nReal Data"
          real_data = 1
          try:
          # initialize the allocation at 100% for domains 5 and 10
            os.system("ssh root@10.190.12.57 xl sched-credit -d Tomcat -c %s" % a[0])
            os.system("ssh root@10.190.12.58 xl sched-credit -d MySQL -c %s" % a[1])
            # connection to Client Server & begin Client Emulator (workload generation)
            print "\nConnecting to Client..."
            sleep(30)
            # client connection and exit (install screen on remote machine)
            os.system("ssh root@10.190.12.56 screen -d -m /root/initialize.sh ")
		    
            # capture cpu usage every 1 sec for 150 secs for Tomcat and MySQL domains
            print "\nCPU usage%:"
            us1 = "ssh root@10.190.12.57 xentop -b -d 1 -i 300 | awk '/Tomcat/ {print $4 fflush(stdout) }' &"
            p1 = subprocess.Popen(us1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout = []

            us2 = "ssh root@10.190.12.58 xentop -b -d 1 -i 300 | awk '/MySQL/ {print $4 fflush(stdout) }' &"
            p2 = subprocess.Popen(us2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout = []

            # convert string cpu usage into float and start estimator for (time) seconds
            for t in range(time):
              line = p1.stdout.readline()
              stdout.append(line)
              y_1 = float(line)
              #print "Current web server usage: %.2f" % y_1
              if line == '' and p.poll() is not None:
                break

              line = p2.stdout.readline()
              stdout.append(line)
              y_2 = float(line)
              #print "Current database cpu usage: %.2f" % y_2
              if line == '' and p.poll() is not None:
                break

              # save current observed utilization & current allocation
              y[0] = y_1
              y[1] = y_2

              if t % ca != 0:
                y_mean[0] = y_mean[0] + y_1
                y_mean[1] = y_mean[1] + y_2

              # adapt the predicted allocation
              if t >= delay:
                # calculate variance
                Q,obs1,obs2 = statistics.covariance(N,t,y,obs1,obs2)
                if t == delay:
                  qerr1[t] = 0
                  qerr2[t] = 0
                else:
                  qerr1[t] = math.sqrt(Q[0,0])
                  qerr2[t] = math.sqrt(Q[1,1])

                if t % ca == 0:
                  sp = sp + 1
                  y_mean[0] = (y_mean[0] + y_1) / ca
                  y_mean[1] = (y_mean[1] + y_2) / ca
                 
                  # allocation prediction using the filters
                  if ans == '2':
                    (a, P, K) = estimators.kalman_mimo(P, Q, R, C, y_mean, a)  # Kalman MIMO
                  elif ans == '4':
                    (a, P, K) = estimators.hinf_mimo(P, Q, R, C, y_mean, a)  # Hinf MIMO
                  elif ans == '6':
                    (a, P, K) = estimators.mcc_kf_mimo(P, Q, R, C, y_mean, a)  # MCC-KF MIMO
                
                  a_out[t] = a  # save predicted allocations
                  print "Predicted cpu allocations: "
                  print a

                  cap1 = a[0]
                  cap2 = a[1] 

                  if cap1 > a_max:
                    cap1 = a_max
                  if cap2 > a_max:
                    cap2 = a_max
                  if cap1 < y[0]:
                    cap1 = y[0]
                  if cap2 < y[1]:
                    cap2 = y[1]
                  if cap1 < a_min:
                    cap1 = a_min
                  if cap2 < a_min:
                    cap2 = a_min

                  cntr += 1
                  sum_cpu1 = sum_cpu1 + y[0]
                  sum_cpu2 = sum_cpu2 + y[1]
                  os.system("ssh root@10.190.12.57 xl sched-credit -d Tomcat -c %s" % cap1)  # set the predicted allocation (cpu cap)
                  os.system("ssh root@10.190.12.58 xl sched-credit -d MySQL -c %s" % cap2)  # set the predicted allocation (cpu cap)

                  archive_alloc1[sp] = cap1
                  archive_alloc2[sp] = cap2
                  archive_usag1[sp] = y_mean[0]
                  archive_usag2[sp] = y_mean[1]
                  archive_K1[sp] = K[0,0]
                  archive_K2[sp] = K[1,1]
                  archive_vr1[sp] = Q[0,0]
                  archive_vr2[sp] = Q[1,1]
                  archive_cv[sp] = Q[0,1]
                  with open("./experiments/log_sp_%s.txt" %date, "a") as stlog:
                    stlog.write("%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n" %(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'),archive_usag1[sp],archive_usag2[sp],archive_alloc1[sp],archive_alloc2[sp],archive_K1[sp],archive_K2[sp],archive_vr1[sp],archive_vr2[sp],archive_cv[sp]))

                  y_hold[0] = y_mean[0]
                  y_hold[1] = y_mean[1]

                  y_mean[0] = 0
                  y_mean[1] = 0

                # add workload/clients
	        if t == 50 or t == 150:
                  os.system("ssh root@10.190.12.56 screen -d -m /root/add_clients.sh ")

                # archives
                archive_a1[t] = cap1
                archive_a2[t] = cap2
                archive_u1[t] = y_1
                archive_u2[t] = y_2
                archive_var1[t] = Q[0,0]
                archive_var2[t] = Q[1,1]
                archive_cov[t] = Q[0,1]
                archive_y1hold[t] = y_hold[0]
                archive_y2hold[t] = y_hold[1]
                timelist[t] = t
                with open("./experiments/log_%s.txt" %date, "a") as stlog:
                  stlog.write("%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n" %(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'),archive_u1[t],archive_u2[t],archive_a1[t],archive_a2[t], archive_var1[t], archive_var2[t], archive_cov[t], archive_y1hold[t], archive_y2hold[t]))
            
            # compute average cpu usage
            avg_cpu1 = sum_cpu1 / cntr
            avg_cpu2 = sum_cpu2 / cntr
            avg_cpu[0] = avg_cpu1
            avg_cpu[1] = avg_cpu2
            # compute overall variances and covariance
            cov_matrix = np.cov(archive_u1, archive_u2, ddof = 0, bias=1)
            var1 = cov_matrix[0,0]
            var2 = cov_matrix[1,1]
            cov = cov_matrix[0,1]
            # compute mrt
            os.system("scp root@10.190.12.56:/root/RUBiS/response.txt /root/viresa/response.txt")
            mrt = metrics.real_mrt_plot(ans,time,date,avg_cpu,var1,var2,cov,qos,ca)
            with open("./experiments/mrt_%s.txt" %date, mode="w") as mrtlog:
              for s in mrt:
                mrtlog.write("%s\n" % s)
            data_type = False

            print_figures = True
            while print_figures:
              printfigures = '''\nExport figures from logs?
              y - Yes
              n - No'''
              print printfigures  # no parentheses, datalist is not a function
              print_figures = raw_input('\033[93m' + '#? ' + '\033[0m')

              if print_figures == 'y':
                print "\nPrinting figures..."               
                metrics.export_figs_mimo(ans)
                print_figures = False

              elif print_figures == 'n':
                print_figures = False
                break

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


    elif ans == 'q':
      print('\nGood bye!')
      ans = None

    else:
      print('\033[91m' + '\nInvalid option. Try another one!\n' + '\033[0m')
      ans = True
