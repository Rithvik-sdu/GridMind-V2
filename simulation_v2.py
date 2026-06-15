#Import packages
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#Identify Demand Variables
baseline_demand_w = 23400
spike_demand_w = 42150
idle_demand_w = 9300

#Identify Battery Variables
battery_capacity_wh = 10240
max_battery_discharge_w = 16000
battery_tank_wh = 10240

#Identify Grid Variables
grid_cap_w = 33500

#Identify Solar Variables
solar_fraction = 0.10

#Identify Controller Variables
alpha = 7.5
beta_battery = 95
w1 = 1
w3 = 1

#Identify Time Variables
dt = 1
sim_duration = 3600

#Identify Logging Lists
demand_log = []
solar_log = []
battery_output_log = []
grid_output_log = []
beta_log = []
tank_log = []
unmet_demand_log = []
curtailment_log = []
solar_used_log = []
timestamp_log = []
C_log = []

#generate demand traces
def demand_trace(scenario, d_log):
    if scenario == '1':
        for sec in range(0, 200):
            d_log.append(np.random.normal(idle_demand_w, 186))
        for sec in range(200, 1200):
            d_log.append(np.random.normal(baseline_demand_w, 468))
        for sec in range(1200, 1600):
            d_log.append(np.random.normal(spike_demand_w, 843))
        for sec in range(1600, 3000):
            d_log.append(np.random.normal(baseline_demand_w, 468))
        for sec in range(3000, 3600):
            d_log.append(np.random.normal(idle_demand_w, 186))

