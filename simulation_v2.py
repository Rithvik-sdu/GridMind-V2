#Import packages
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#Identify Variables
baseline_demand_w = 4680
battery_capacity_wh = 2048  # 5 × 409.6Wh LiFePO4 units
battery_soc = 100
solar_max_output_w = 10000
grid_price_per_kwh = 0.12
grid_max_output_w = 20000
forecast_demand_w = 0

#Algorithm parameters
MAX_BATTERY_DISCHARGE_W = 3200  # 5 × 640W continuous discharge

#Key Metrics
battery_soc_list = []
grid_contribution_list = []
solar_output_list = []
demand_list = []
mode_list = []
battery_setpoints = []

#Simulation parameters
TIME_STEP_SECONDS = 1
SIM_DURATION_SECONDS = 3600
