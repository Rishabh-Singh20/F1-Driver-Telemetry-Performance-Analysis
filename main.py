import fastf1 as ff1
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import pandas as pd

# Enable caching
ff1.Cache.enable_cache('D:/Python/cache')

# Set up matplotlib for FastF1 plotting
plotting.setup_mpl(color_scheme='fastf1', misc_mpl_mods=False)

# Load the qualifying session data for Monza 2024
year = int(input("Enter the year: "))
track = input("Enter the track name: ")
session = input("Enter the session type(FP1/FP2/FP3/Q/R): ")
print("Please enter the driver's abbreviation (e.g., 'LEC' for Charles Leclerc, 'VER' for Max Verstappen)")
driver1 = input("Enter first driver's number or name: ").upper()
driver2 = input("Enter second driver's number or name: ").upper()
quali = ff1.get_session(year, track, session)
quali.load()  # Ensure session data is loaded

# Load laps data with telemetry
laps = quali.laps



try:
    driver1_number = quali.get_driver(driver1).number
    driver2_number = quali.get_driver(driver2).number
except AttributeError:
    driver1_number = driver1
    driver2_number = driver2
# Pick driver laps
laps_driver1 = laps.pick_drivers(driver1)
laps_driver2 = laps.pick_drivers(driver2)

# Get the fastest lap telemetry data
fastest_driver1 = laps_driver1.pick_fastest()
fastest_driver2 = laps_driver2.pick_fastest()

# Check if fastest laps are available
if fastest_driver1 is not None:
    telemetry_driver1 = fastest_driver1.get_telemetry().add_distance()
else:
    print("No fastest lap data for driver1.")
    telemetry_driver1 = pd.DataFrame()

if fastest_driver2 is not None:
    telemetry_driver2 = fastest_driver2.get_telemetry().add_distance()
else:
    print("No fastest lap data for driver2.")
    telemetry_driver2 = pd.DataFrame()

# Add driver name to telemetry data
if not telemetry_driver1.empty:
    telemetry_driver1['Driver'] = "driver1"

if not telemetry_driver2.empty:
    telemetry_driver2['Driver'] = "driver2"

# Combine the telemetry data
telemetry = pd.concat([telemetry_driver1, telemetry_driver2])

# Define the number of minisectors
num_minisectors = 25

# Calculate total distance and minisector length
total_distance = max(telemetry['Distance'])
minisector_length = total_distance / num_minisectors

# Assign minisector numbers
telemetry['Minisector'] = telemetry['Distance'].apply(lambda dist: int(dist // minisector_length) + 1)

# Calculate average speed per minisector per driver
average_speed = telemetry.groupby(['Minisector', 'Driver'])['Speed'].mean().reset_index()

# Determine the fastest driver per minisector
fastest_driver = average_speed.loc[average_speed.groupby('Minisector')['Speed'].idxmax()]
fastest_driver = fastest_driver[['Minisector', 'Driver']].rename(columns={'Driver': 'Fastest_driver'})

# Merge with telemetry data
telemetry = telemetry.merge(fastest_driver, on='Minisector').sort_values(by='Distance')

# Map drivers to integers for coloring
telemetry['Fastest_driver_int'] = telemetry['Fastest_driver'].map({'driver1': 1, 'driver2': 2})

# Create points and segments for plotting
x = np.array(telemetry['X'].values)
y = np.array(telemetry['Y'].values)
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# Create the line collection object
cmap = plt.get_cmap('rainbow_r', 2)
lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
lc_comp.set_array(telemetry['Fastest_driver_int'].to_numpy().astype(float))
lc_comp.set_linewidth(5)

# Plot the data
plt.rcParams['figure.figsize'] = [18, 10]
plt.gca().add_collection(lc_comp)
plt.axis('equal')
plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

# Add a color bar
cbar = plt.colorbar(mappable=lc_comp, boundaries=np.arange(1, 4))
cbar.set_ticks([1.5, 2.5])
cbar.set_ticklabels([driver1, driver2])

# Save and show the plot
plt.savefig(f"{year}_{driver1}_{driver2}.png", dpi=500)
plt.show()
