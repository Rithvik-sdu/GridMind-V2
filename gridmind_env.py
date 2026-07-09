#Import modules
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math as mt

#Ensure period accuracy with a seed
np.random.seed(42)

#Identify Demand Variables
baseline_demand_w = 23400
spike_demand_w = 42150
idle_demand_w = 9300

#Identify Battery Variables
battery_capacity_wh = 10240
max_battery_discharge_w = 16000
max_battery_charge_w = 10240
battery_tank_wh = 10240

#Identify Grid Variables
grid_cap_w = 53000
last_grid_output = 0
max_jump = 53000

#Identify Solar Variables
solar_fraction = 0.10

#Identify Time Variables
dt = 0.1
sim_duration = 864000

#generate demand traces
def demand_trace(d_log):
    rand_hertz = np.random.uniform(0.2, 3.0)
    period = int(1/(rand_hertz * dt))
    quarter = max(2, period//4)
    d_log.append(np.random.normal(idle_demand_w, 186))

    idle_baseline = np.linspace(idle_demand_w, baseline_demand_w, 10)
    idle_baseline = idle_baseline + np.random.normal(0, 468, 10)
    d_log.extend(idle_baseline)

    while len(d_log) < 864000:

        ramp_up = np.linspace(baseline_demand_w, spike_demand_w, quarter)
        ramp_up = ramp_up + np.random.normal(0, 843, quarter)
        d_log.extend(ramp_up)

        d_log.extend(np.random.normal(spike_demand_w, 843, quarter))

        ramp_down = np.linspace(spike_demand_w,baseline_demand_w, quarter)
        ramp_down = ramp_down + np.random.normal(0, 843, quarter)
        d_log.extend(ramp_down)

        d_log.extend(np.random.normal(baseline_demand_w, 468, quarter))

    baseline_idle = np.linspace(baseline_demand_w, idle_demand_w, 10)
    baseline_idle = baseline_idle + np.random.normal(0, 468, 10)
    d_log.extend(baseline_idle)

def extract_solar(file_path, target_length, column_name):
    df = pd.read_csv(file_path)
    solar = pd.to_numeric(df[column_name], errors='coerce')

    solar = solar.fillna(0)
    solar = solar.clip(lower=0)      

    peak = solar.max()
    scale = ((solar_fraction * spike_demand_w)/peak)
    solar *= scale

    repeat_factor = mt.ceil(target_length / len(solar))
    solar = np.repeat(solar, repeat_factor)
    solar = solar[:target_length]

    return solar.tolist()


csv_file_one = "/Users/uthangavelu/Downloads/system_10__date_2015_06_17.csv" #Golden, Colorado
ac_power_name_one = 'ac_power__423'

csv_file_two = "/Users/uthangavelu/Downloads/system_1423__date_2023_02_28.csv" #Clark County, Nevada
ac_power_name_two = 'inv1_ac_power__4854'

csv_file_three = "/Users/uthangavelu/Downloads/system_1403__date_2020_06_02.csv" #Cocoa Beach, Florida
ac_power_name_three = 'ac_power__5034'

csv_file_four = "/Users/uthangavelu/Downloads/system_1422__date_2017_05_17.csv"
ac_power_name_four = 'inv1_ac_power__4830' #Burlington, Vermont

csv_file_five = "/Users/uthangavelu/Downloads/system_1429__date_2017_07_16.csv" #Alberquerque, New Mexico
ac_power_name_five = 'inv1_ac_power__4917'
