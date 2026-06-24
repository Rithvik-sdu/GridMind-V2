#Import packages
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math as mt

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

#Identify Controller Variables
decay = 0.51
alpha = 7.5
beta_battery = 95
beta_grid = 5
w1 = 1
w2 = 1
x1 = 0
x2 = 0

#Identify Time Variables
dt = 0.1
sim_duration = 864000

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
grid_ramp_log = []

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

demand_trace(demand_log)
# plt.plot(demand_log[:300])
# plt.xlabel("Time (s)")
# plt.ylabel("Power (W)") 
# plt.show()

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

solar_log = extract_solar(csv_file_one, len(demand_log), ac_power_name_one)

# plt.plot(solar_log)
# plt.xlabel("Time (hours)")
# plt.ylabel("Solar Power (W)")  
# plt.show()

for subsec in range(0, len(demand_log)):
    #Calculate key variables
    leftover = demand_log[subsec] - solar_log[subsec]
    headroom = grid_cap_w - leftover

    if leftover > 0 and demand_log[subsec] > baseline_demand_w:

        #Split Leftover into battery
        battery_output = leftover * (beta_battery / 100)

        #Cap Battery
        if battery_output > max_battery_discharge_w:
            battery_output = max_battery_discharge_w
        elif battery_output < 0:
            battery_output = 0
        else:
            battery_output = battery_output

        if battery_output * (dt/3600) > battery_tank_wh:
            battery_output = battery_tank_wh * (3600/dt)
        else:
            pass


        #Split Leftover into grid
        grid_output = leftover - battery_output

        #Add Battery Output to Lists
        battery_output_log.append(battery_output)

        #Cap Grid
        if grid_output > grid_cap_w:
            grid_output = grid_cap_w
        elif grid_output < 0:
            grid_output = 0
        else:
            grid_output = grid_output
        
        #Update Grid Output Log
        grid_output_log.append(grid_output)
    

        #Measure Cost Terms 
        x1 = (abs((grid_output_log[subsec] - last_grid_output)))/max_jump
        grid_ramp = x1 * max_jump
        grid_ramp_log.append(grid_ramp)
        x2 = grid_output/grid_cap_w
        cost = (w1 * x1) + (w2 * x2)

        #Adjust Beta Slices
        beta_battery = beta_battery + (alpha * cost) - (beta_battery * decay)

        if beta_battery < 0:
            beta_battery = 0
        elif beta_battery > 100:
            beta_battery = 100
        else:
            beta_battery = beta_battery

        beta_grid = 100 - beta_battery

        #Add betas and costs to list
        beta_log.append((beta_battery, beta_grid))
        C_log.append(cost)

        #Update Battery Tank
        battery_output_capacity = battery_output * (dt/3600)
        battery_tank_wh -= battery_output_capacity

        #Update tank log
        tank_log.append(battery_tank_wh)

        #Check for unmet demand and update log
        if leftover > (battery_output + grid_output):
            unmet_demand = leftover - (battery_output + grid_output)
            unmet_demand_log.append(unmet_demand)
        else:
            unmet_demand = 0
            unmet_demand_log.append(unmet_demand)

        #Update for remaining logs
        curtailment_log.append(0)
        solar_used_log.append(solar_log[subsec])
        timestamp_log.append(subsec)

    elif leftover > 0 and demand_log[subsec] <= baseline_demand_w:
        #No leftover, no battery
        battery_output = 0

        #Update battery logs
        battery_output_log.append(battery_output)

        #No Cost Terms
        x1 = 0
        grid_ramp_log.append(x1)
        x2 = 0
        cost = 0

        #Update beta and cost lists
        beta_log.append((beta_battery, beta_grid))
        C_log.append(cost)

        #Update Battery Tank
        charge_power = min(((battery_capacity_wh - battery_tank_wh) * (3600/dt)), max_battery_charge_w, headroom)

        battery_output_capacity = charge_power * (dt/3600)
        battery_tank_wh += battery_output_capacity

        grid_output = charge_power + leftover
        if battery_tank_wh > battery_capacity_wh:
            battery_tank_wh = battery_capacity_wh
        else:
            grid_output = grid_output
            battery_tank_wh = battery_tank_wh
        
        #Update Grid Output
        grid_output = charge_power + leftover
        grid_output_log.append(grid_output)

        #Update tank log
        tank_log.append(battery_tank_wh)

        #Update curtailment and used solar logs
        curtailment_log.append(0)
        solar_used_log.append(solar_log[subsec])

        #Update remaining logs
        unmet_demand_log.append(0)
        timestamp_log.append(subsec)
    elif leftover <= 0:
        #No leftover, no battery or grid output
        battery_output = 0
        grid_output = 0

        #Update battery and grid output logs
        battery_output_log.append(battery_output)
        grid_output_log.append(grid_output)

        #No Cost Terms
        x1 = 0
        grid_ramp_log.append(x1)
        x2 = 0
        cost = 0

        #Update beta and cost lists
        beta_log.append((beta_battery, beta_grid))
        C_log.append(cost)

        #Update Battery Tank

        if abs(leftover) > max_battery_charge_w:
            leftover = max_battery_charge_w

        battery_output_capacity = abs(leftover) * (dt/3600)
        battery_tank_wh += battery_output_capacity

        if battery_tank_wh > battery_capacity_wh:
            battery_tank_wh = battery_capacity_wh
        else:
            grid_output = grid_output
            battery_tank_wh = battery_tank_wh

        #Update tank log
        tank_log.append(battery_tank_wh)

        #Update curtailment and used solar logs
        curtailment_log.append(abs(leftover) - solar_log[subsec])
        solar_used_log.append((solar_log[subsec] - abs(leftover)))

        #Update remaining logs
        unmet_demand_log.append(0)
        timestamp_log.append(subsec)
    
    last_grid_output = grid_output

assert len(demand_log) == len(tank_log) == len(grid_output_log) == len(battery_output_log) == len(beta_log) == len(unmet_demand_log)

print("Steps:", len(tank_log))
print("Tank — start:", round(tank_log[0],1), "min:", round(min(tank_log),1), "max:", round(max(tank_log),1), "end:", round(tank_log[-1],1))
print("Battery out — min:", round(min(battery_output_log),1), "max:", round(max(battery_output_log),1))
print("Grid out — min:", round(min(grid_output_log),1), "max:", round(max(grid_output_log),1))
print("Unmet — total:", round(sum(unmet_demand_log),1), "max:", round(max(unmet_demand_log),1))
print("Curtailment total:", round(sum(curtailment_log),1))
print("Charge steps (headroom branch entered):", sum(1 for b in battery_output_log if b == 0))

grid_ramp_mean = sum(grid_ramp_log[1:]) / len(grid_ramp_log[1:])
print("Mean grid ramp:", round(grid_ramp_mean, 2))
no_batt_grid = [max(0, demand_log[i] - solar_log[i]) for i in range(len(demand_log))]
no_batt_ramp = sum(abs(no_batt_grid[i] - no_batt_grid[i-1]) for i in range(1, len(no_batt_grid))) / (len(no_batt_grid) - 1)
print("No-battery grid ramp:", round(no_batt_ramp, 2))
print("With-battery grid ramp:", round(grid_ramp_mean, 2))
print("Reduction:", round(100*(1 - grid_ramp_mean/no_batt_ramp), 1), "%")


plt.plot(demand_log[:10000], label="Demand")
plt.plot(grid_output_log[:1000], label="Grid output")
plt.plot(battery_output_log[:1000], label="Battery output")
plt.xlabel("Step"); plt.ylabel("Power (W)"); plt.legend(); plt.show()