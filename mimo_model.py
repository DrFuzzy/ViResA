#!/usr/bin/python
# -*- coding: utf-8 -*-

import estimators
import metrics
import statistics
import sys
import os
import math
import csv
import numpy as np
from time import sleep
from datetime import datetime
import subprocess

# Function definitions


def mimo(ans, total_exps, duration, delay, qos, control_interval):
    N = 10  # variance and covariance window
    t = 0
    timelist = np.zeros(duration)  # keep timing logs
    a_min = [20, 20]
    a_max = [100, 100]
    sampling_point = 0
    samples = float(duration)/control_interval
    # components addresses
    webserver = 'root@172.16.56.9'
    database = 'root@172.16.56.10'
    controller = 'root@172.16.56.8'
    vm_web_name = 'Tomcat'
    vm_db_name ='MySQL'
    # controller's variables
    P = np.array([[0, 0], [0, 0]])  # error matrix
    R = np.array([[1, 0], [0, 1]])  # measurement noise matrix
    Q = np.array([[4, 0], [0, 4]])  # process noise matrix
    K = np.array([[1, 1], [1, 1]])  # gain matrix
    C = np.array([[0.7, 0], [0, 0.7]])  # ECC'16: 0.95 , ETFA'17: 0.70
    # system model's variables
    a = [100, 100]
    cap = [100, 100]
    y = np.array([0.0, 0.0])
    y_mean = np.array([0.0, 0.0])
    y_hold_mean = np.array([0.0, 0.0])
    # archives
    archive_K = np.zeros((samples, 2))
    archive_a = np.zeros((duration, 2))
    archive_u = np.zeros((duration, 2))
    archive_alloc = np.zeros((samples, 2))
    archive_usage = np.zeros((samples, 2))
    archive_cap = np.zeros((duration, 2))
    archive_var = np.zeros((duration, 2))
    archive_cov = np.zeros(duration)
    archive_var_mean = np.zeros((samples, 2))
    archive_cov_mean = np.zeros(samples)
    archive_y_hold_mean = np.zeros((duration, 2))
    # statistics
    sl_window1 = []
    sl_window2 = []
    qerr = np.zeros((duration, 2))
    var = np.zeros((duration, 2))
    cov = 0
    cov_matrix = []
    # average cpu usage
    sum_cpu = np.array([0.0, 0.0])
    avg_cpu = np.array([0.0, 0.0])

    # os.makedirs('./experiments/experiment-%s'%date)
    for exp in range(total_exps):
        print "\nStarting experiment no: %s" % exp
        try:
          # initialize the allocation at 100% for domains 5 and 10
          os.system("ssh %s xl sched-credit -d %s -c %s" % (webserver, vm_web_name, a[0]))
          os.system("ssh %s xl sched-credit -d %s -c %s" % (database, vm_db_name, a[1]))
          # client connection and exit (install screen on remote machine)
          os.system("ssh %s screen -d -m /root/clear_response_logs.sh " % controller)
          print "\nConnecting to Client..."
          sleep(10)
          print "\nConnection established!"

          # capture cpu usage every 1 sec for t secs for Tomcat and MySQL domains
          print "\nCPU usage%:"
          vm1_cmd_record = "ssh " + webserver + " xentop -b -d 1 -i 300 | awk '/" + vm_web_name + "/ {print $4 fflush(stdout) }' &"
          vm1_record = subprocess.Popen(vm1_cmd_record, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          stdout = []

          vm2_cmd_record = "ssh " + database + " xentop -b -d 1 -i 300 | awk '/" + vm_db_name + "/ {print $4 fflush(stdout) }' &"
          vm2_record = subprocess.Popen(vm2_cmd_record, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          stdout = []

          date = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
          # convert string cpu usage into float and start estimator for (duration) seconds
          for t in range(duration):
            vm1_line = vm1_record.stdout.readline()
            stdout.append(vm1_line)
            y[0] = float(vm1_line)
            if vm1_line == '' and vm1_record.poll() is not None:
              break

            vm2_line = vm2_record.stdout.readline()
            stdout.append(vm2_line)
            y[1] = float(vm2_line)
            if vm2_line == '' and vm2_record.poll() is not None:
              break

            if t % control_interval != 0:
              y_mean = np.add(y_mean, y)

            # adapt the predicted allocation
            if t >= delay:
              # calculate variance
              Q, sl_window1, sl_window2 = statistics.covariance(N, t , y , sl_window1, sl_window2)
              if t == delay:
                qerr[t] = 0
              else:
                qerr[t] = math.sqrt(Q[0,0]), math.sqrt(Q[1,1])

              if t % control_interval == 0:
                sampling_point += 1
                print "Sample: %s" %(sampling_point)
                y_mean = np.true_divide(np.add(y_mean, y), control_interval)
                print "Current cpu recourse usage: %s" %y_mean
                 
                # allocation prediction using the filters
                if ans == '1':
                  (a, P, K) = estimators.kalman_mimo(P, Q, R, C, y_mean, a)  # Kalman MIMO
                elif ans == '2':
                  (a, P, K) = estimators.hinf_mimo(P, Q, R, C, y_mean, a)  # Hinf MIMO
                elif ans == '3':
                  (a, P, K) = estimators.mcc_kf_mimo(P, Q, R, C, y_mean, a)  # MCC-KF MIMO
                print "Predicted cpu resources: %s" %a

                # bounded allocations
                cap = a
                cap = capAllocation(cap, y, a_min, a_max)
                print "Allocated cpu resources: %s" %cap

                sum_cpu = (sum_cpu[0] + y[0]), (sum_cpu[1] + y[1])

                os.system("ssh %s xl sched-credit -d %s -c %s" % (webserver, vm_web_name, cap[0]))  # set the predicted allocation (cpu cap)
                os.system("ssh %s xl sched-credit -d %s -c %s" % (database, vm_db_name, cap[1]))  # set the predicted allocation (cpu cap)

                archive_alloc[sampling_point] = cap
                archive_usage[sampling_point] = y_mean
                archive_K[sampling_point] = K[0,0], K[1,1]
                archive_var_mean[sampling_point] = Q[0,0], Q[1,1]
                archive_cov_mean[sampling_point] = Q[0,1]

                with open("./experiments/log_sp_%s.txt" %date, "a") as stlog:
                  stlog.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), 
                                                            archive_usage[sampling_point, 0],
                                                            archive_usage[sampling_point, 1],
                                                            archive_alloc[sampling_point, 0],
                                                            archive_alloc[sampling_point, 0],
                                                            archive_K[sampling_point, 0],
                                                            archive_K[sampling_point, 1],
                                                            archive_var_mean[sampling_point, 0],
                                                            archive_var_mean[sampling_point, 1],
                                                            archive_cov_mean[sampling_point]))

                y_hold_mean = y_mean
                y_mean = 0

                # add workload/clients
                if t == 50 or t == 150:
                  os.system("ssh %s screen -d -m /root/add_workload.sh " %controller)

              # archives
              archive_a[t] = a
              archive_cap[t] = cap
              archive_u[t] = y
              archive_var[t] = Q[0,0], Q[1,1]
              archive_cov[t] = Q[0,1]
              archive_y_hold_mean[t] = y_hold_mean
              timelist[t] = t
              with open("./experiments/log_%s.txt" %date, "a") as stlog:
                stlog.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), 
                                                    archive_u[t, 0],
                                                    archive_u[t, 1],
                                                    archive_a[t, 0],
                                                    archive_a[t, 1],
                                                    archive_var[t, 0],
                                                    archive_var[t, 1],
                                                    archive_cov[t],
                                                    archive_y_hold_mean[t, 0],
                                                    archive_y_hold_mean[t, 1]))
          sleep(1)

          # compute average cpu usage
          avg_cpu = (sum_cpu[0] / sampling_point), (sum_cpu[1] / sampling_point)
          # compute overall variances and covariance
          cov_matrix = np.cov(archive_u[0], archive_u[1], ddof = 0, bias=1)
          var = cov_matrix[0,0], cov_matrix[1,1]
          cov = cov_matrix[0,1]
          sampling_point = 0
          # compute mrt
          os.system("scp %s:/root/RUBiS/response.txt /root/viresa/response.txt" %controller)
          mrt = metrics.real_mrt_plot(ans,duration,date,avg_cpu,var,cov,qos,control_interval)
          with open("./experiments/mrt_%s.txt" %date, mode="w") as mrtlog:
            for s in mrt:
              mrtlog.write("%s\n" % s)


        except IOError as e:
          print("\n({})\n".format(e))
          ans = True

def capAllocation(cap, y, a_min, a_max):
    if cap[0] > a_max[0]:
      cap[0] = a_max[0]
    if cap[1] > a_max[1]:
      cap[1] = a_max[1]
    if cap[0] < y[0]:
      cap[0] = y[0]
    if cap[1] < y[1]:
      cap[1] = y[1]
    if cap[0] < a_min[0]:
      cap[0] = a_min[0]
    if cap[1] < a_min[1]:
      cap[1] = a_min[1]
  
    return cap