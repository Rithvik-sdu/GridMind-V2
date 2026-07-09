#Import modules
from grid_mind_env import *
import matplotlib.pyplot as plt

#Identify Controller Varaibles
static_dispatch_w = 8000

#Initialize Logging Lists
demand_log = []
solar_log = []
battery_output_log = []
grid_output_log = []
tank_log = []
unmet_demand_log = []
curtailment_log = []
solar_used_log = []
timestamp_log = []
grid_ramp_log = []

#Create Demand Trace
demand_trace(demand_log)
# plt.plot(demand_log[:300])
# plt.xlabel("Time (s)")
# plt.ylabel("Power (W)") 
# plt.show()

#Create Solar Trace
solar_log = extract_solar(csv_file_one, len(demand_log), ac_power_name_one)
# plt.plot(solar_log)
# plt.xlabel("Time (hours)")
# plt.ylabel("Solar Power (W)")  
# plt.show()

for subsec in range(len(demand_log)):
    leftover = demand_log[subsec] - solar_log[subsec]
    battery_output_w = static_dispatch_w 
    headroom = grid_cap_w - leftover
    #Branch 1: Solar is less than the demand
    if leftover > 0 and demand_log[subsec] > baseline_demand_w:
        #Cap battery output to tank and rate restrictions
        if battery_output_w > max_battery_discharge_w:
            battery_output_w = max_battery_discharge_w
        elif battery_output_w < 0:
            battery_output_w = 0
        else:
            battery_output_w = battery_output_w

        #Cap battery output to tank capacity
        if battery_output_w *(dt/3600) > battery_tank_wh:
            battery_output_w = battery_tank_wh * (3600/dt)
        else:
            battery_output_w = battery_output_w

        #Discharge battery to meet demand and calculate grid_output
        grid_output = leftover - battery_output_w
        battery_tank_wh -= battery_output_w * (dt/3600)

        #Cap grid output to max capacity
        if grid_output > grid_cap_w:
            grid_output = grid_cap_w
        elif grid_output < 0:
            grid_output = 0
        else:
            grid_output = grid_output

        #Update remaining logs
        battery_output_log.append(battery_output_w)
        grid_output_log.append(grid_output)
        tank_log.append(battery_tank_wh)

        unmet_demand = demand_log[subsec] - solar_log[subsec] - battery_output_w - grid_output
        if unmet_demand < 0:
            unmet_demand = 0
        else:
            unmet_demand = unmet_demand
        unmet_demand_log.append(unmet_demand)

        curtailment_log.append(0)
        solar_used_log.append(solar_log[subsec])
        timestamp_log.append(subsec)

        grid_ramp = (abs((grid_output_log[subsec] - last_grid_output)))
        grid_ramp_log.append(grid_ramp)

        last_grid_output = grid_output_log[subsec]
    #Branch 2: Demand is low 
    elif leftover > 0 and demand_log[subsec] <= baseline_demand_w:
         #Update Battery Tank
        charge_power = min(((battery_capacity_wh - battery_tank_wh) * (3600/dt)), max_battery_charge_w, headroom)

        battery_output_capacity = charge_power * (dt/3600)
        battery_tank_wh += battery_output_capacity

        #Calculate grid output
        grid_output = charge_power + leftover

        #Cap battery tank to max capacity
        if battery_tank_wh > battery_capacity_wh:
            battery_tank_wh = battery_capacity_wh
        else:
            battery_tank_wh = battery_tank_wh

        #Cap grid output to max capacity
        if grid_output > grid_cap_w:
            grid_output = grid_cap_w
        elif grid_output < 0:
            grid_output = 0
        else:
            grid_output = grid_output

        #Update remaining logs
        battery_output_log.append(0)
        grid_output_log.append(grid_output)
        tank_log.append(battery_tank_wh)

        unmet_demand_log.append(0)

        curtailment_log.append(0)
        solar_used_log.append(solar_log[subsec])
        timestamp_log.append(subsec)

        grid_ramp = (abs((grid_output_log[subsec] - last_grid_output)))
        grid_ramp_log.append(grid_ramp)

        last_grid_output = grid_output_log[subsec]
    #Branch 3: Solar is greater than the demand
    elif leftover <= 0:
        #Intialize battery and grid output
        battery_output_w = 0
        grid_output = 0

        if abs(leftover) > (max_battery_charge_w):
            new_leftover = max_battery_charge_w
        else:
            new_leftover = abs(leftover)
        #Charge battery
        battery_tank_wh += new_leftover * (dt/3600)

        #Cap battery tank to max capacity
        if battery_tank_wh > battery_capacity_wh:
            battery_tank_wh = battery_capacity_wh
        else:
            battery_tank_wh = battery_tank_wh

        #Update remaining logs
        battery_output_log.append(0)
        grid_output_log.append(grid_output)
        tank_log.append(battery_tank_wh)

        unmet_demand_log.append(0)

        curtailment_log.append(abs(leftover) - new_leftover)
        solar_used_log.append(solar_log[subsec])
        timestamp_log.append(subsec)

        grid_ramp = (abs((grid_output_log[subsec] - last_grid_output)))
        grid_ramp_log.append(grid_ramp)

        last_grid_output = grid_output_log[subsec]

assert len(demand_log) == len(tank_log) == len(grid_output_log) == len(battery_output_log) == len(unmet_demand_log)

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
plt.plot(grid_output_log[:10000], label="Grid output")
plt.plot(battery_output_log[:10000], label="Battery output")
plt.xlabel("Step"); plt.ylabel("Power (W)"); plt.legend(); plt.show()
