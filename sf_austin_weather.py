import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
from datetime import datetime

# Data from San Francisco and Austin
filename = '/Users/charliemaxwell/Documents/Python/Python Crash Course/projectA\
/data/3152763.csv'

# Opening the file and appending its contents into a dictionary
with open(filename) as f:
    reader = csv.reader(f)
    header_row = next(reader)

    # Creating a dictionary for each station and some relevant details
    # like its location, date range, data types available, data coverage
    stations = {}

    # iterating through each row (date and measurement per station) in the CSV 
    for row in reader:
        
        # pull the date for the reading
        current_date = datetime.strptime(row[5], '%Y-%m-%d')

        # initialize the attributes that are fixed for each station
        if row[0] not in stations.keys():
           
            # set location
            if 'CA US' in row[1]:
                location = 'CA'
            elif 'TX US' in row[1]:
                location = 'TX'

            # create an empty dictionary for each station in the file
            # date range is the longest stretch of dates for that location
            stations[row[0]] = {
                'location': location,
                'min_date': current_date,
                'max_date': current_date,
                'date_count': 0,
                'data_types': {
                    'AWND': 0,
                    'EVAP': 0,
                    'PRCP': 0,
                    'TAVG': 0,
                    'TMAX': 0,
                    'TMIN': 0,
                    }, 
                'coverage': {
                    'AWND': 0.0,
                    'EVAP': 0.0,
                    'PRCP': 0.0,
                    'TAVG': 0.0,
                    'TMAX': 0.0,
                    'TMIN': 0.0,
                    }
                }
        # update the data that's not fixed
        elif row[0] in stations.keys():

            # update max date and date count
            if current_date > stations[row[0]]['max_date']:
                stations[row[0]]['max_date'] = current_date 
                stations[row[0]]['date_count'] += 1

                # if there's data in the columns for any data measurements, 
                # note that for later comparison (AWND through TMIN)
                for i in range(6, 12):
                    dtype = header_row[i]

                    # if not blank, increment count for that data type
                    if len(row[i]) != 0:
                        stations[row[0]]['data_types'][dtype] += 1

    # now we'll close out of the CSV and run some analytics on the stations 
    # dictionary in order to decide what date ranges and stations give 
    # the best data

# creating a second dictionary for each state
CA_stations = {}
TX_stations = {}

# creating emnpty lists (of lists) for plotting data available at each station
CA_data_visual = []
TX_data_visual = []
CA_data_by_type = {}
TX_data_by_type = {}

# Going through each station in the dictionary to update calculated parameters 
# and append to the new dictionaries
for station in stations:

    # calculate the date range
    datediff = stations[station]['max_date'] - stations[station]['min_date']
    stations[station]['date_count'] = datediff

    # calculate the coverage for each data type by station
    # which I'm defining as the proportion of days with data throughout the
    # station's entire date range
    for datatype in stations[station]['coverage']:
        try:
            stations[station]['coverage'][datatype] = round(stations[station]\
            ['data_types'][datatype] / (stations[station]['date_count'].days),2)
            CA_data_by_type[datatype] = []        
            TX_data_by_type[datatype] = []
        except ZeroDivisionError:
            pass # for stations with only one day of data

    # Approximating the best stations with the total coverage across ALL data 
    # types at each location
    total_coverage = 0
    for item in stations[station]['data_types']:
        total_coverage += stations[station]['data_types'][item]
    
    stations[station]['daysofdata'] = total_coverage

    # Adding to the new dictionaries and lists based on data coverage and 
    # location. Only those with 100% coverage of any of the data types 
    # are good enough to work with, since we have so many.
    for item in stations[station]['coverage']:
        if stations[station]['coverage'][item] == 1:
            if stations[station]['location'] == 'TX':
                TX_stations[station] = stations[station]
                TX_data_visual.append(list(stations[station]['coverage'].\
                    values()))
            elif stations[station]['location'] == 'CA':
                CA_stations[station] = stations[station]
                CA_data_visual.append(list(stations[station]['coverage'].\
                    values()))
            # exit this loop once we hit 100% coverage for a given data type
            break


### VISUALIZATIONS ###

# Formatting and setting up subplots
# ax1 and ax2 are for the stations' data availability, while ax3 will show the 
# weather data over time at the top 2 stations
plt.style.use('dark_background')
bar_colors = ['navy','orange','forestgreen','purple','crimson','cornflowerblue']

fig = plt.figure(figsize=(13,7.8))
ax1 = plt.subplot2grid(shape=(2,2), loc=(0,0))
ax2 = plt.subplot2grid(shape=(2,2), loc=(0,1))
ax3 = plt.subplot2grid(shape=(2,2), loc=(1,0), colspan=2)

fig.suptitle("Data Availability for Weather Stations in CA and TX", fontsize=13)
width = 0.15


### VISUALIZATION 1
# Showing measurements available by station to give an idea of the data we have

# Creating x-axis ticks with weather station names
TX_x_labels = list(TX_stations.keys()) 
CA_x_labels = list(CA_stations.keys())

## California Subplot    
# populate dicts with data type as keys and observation data as a list
for i in range(len(CA_data_visual)):
    for j in range(len(CA_data_visual[0])):
        CA_data_by_type[list(CA_data_by_type)[j]].append(CA_data_visual[i][j])

# create nparray to store the locations of each bar, then generate plots
# the bars are each offset by the width we set
xval = np.arange(len(CA_data_by_type['AWND']))
for i, measure in enumerate(CA_data_by_type):
    ax1.bar(x=xval+(width*i), height=CA_data_by_type[measure], label=measure, \
        width=width, color=bar_colors[i])

# format subplot
ax1.set_title("California Weather Stations", fontsize=12)
ax1.set_xticks(ticks=xval-width/2, labels=CA_x_labels, fontsize=2, \
    rotation='vertical')


## Texas Subplot    
# populate dicts with data type as keys 
for i in range(len(TX_data_visual)):
    for j in range(len(TX_data_visual[0])):
        TX_data_by_type[list(TX_data_by_type)[j]].append(TX_data_visual[i][j])

# create nparray to store the locations of each bar, then generate plots
xval = np.arange(len(TX_data_by_type['AWND']))
for i, measure in enumerate(TX_data_by_type):
    ax2.bar(x=xval+(width*i), height=TX_data_by_type[measure], label=measure, \
        width=width, color=bar_colors[i])

ax2.set_title("Texas Weather Stations", fontsize=12)
ax2.set_xticks(ticks=xval-width/2, labels=TX_x_labels, fontsize=2, \
    rotation='vertical')


# -- VISUALIZATION 2 -- 
# plotting the weather data for the top station from each locale

# First pick the station from each list with the best coverage
top_CA_station = ''
max_coverage = 0
for station in CA_stations:
    if CA_stations[station]['daysofdata'] >= max_coverage:
        top_CA_station = station
        max_coverage = CA_stations[station]['daysofdata']

top_TX_station = ''
max_coverage = 0
for station in TX_stations:
    if TX_stations[station]['daysofdata'] >= max_coverage:
        top_TX_station = station
        max_coverage = TX_stations[station]['daysofdata']

# get data for the top 2 stations
with open(filename) as f:
    reader = csv.reader(f)

    dates = []
    CAwind, CArain, CAavgtemp, CAhighs, CAlows = [], [], [], [], []
    TXwind, TXrain, TXavgtemp, TXhighs, TXlows = [], [], [], [], []
 
    for row in reader:
        # pulling in data for top CA station
        if row[0] == top_CA_station:
            current_date = datetime.strptime(row[5], '%Y-%m-%d')
            dates.append(current_date)
            try:
                wind = float(row[6])
                rainfall = float(row[8])
                avgtemp = float(row[9])
                high = float(row[10])
                low = float(row[11])                
            # For days where there is no data, use the previous day's value
            except ValueError:
                CAwind.append(CAwind[-1])
                CArain.append(CArain[-1])
                CAavgtemp.append(CAavgtemp[-1])
                CAhighs.append(CAhighs[-1])
                CAlows.append(CAlows[-1])
            else:
                CAwind.append(wind)
                CArain.append(rainfall)
                CAavgtemp.append(avgtemp)
                CAhighs.append(high)
                CAlows.append(low)
            
        
        # and repeating for top TX station's data
        elif row[0] == top_TX_station:
            current_date = datetime.strptime(row[5], '%Y-%m-%d')
            try:
                wind = float(row[6])
                rainfall = float(row[8])
                avgtemp = float(row[9])
                high = float(row[10])
                low = float(row[11])
            # For days where there is no data, use the previous day's value
            except ValueError:
                TXwind.append(TXwind[-1])
                TXrain.append(TXrain[-1])
                TXavgtemp.append(TXavgtemp[-1])
                TXhighs.append(TXhighs[-1])
                TXlows.append(TXlows[-1])
            else:
                TXwind.append(wind)
                TXrain.append(rainfall)
                TXavgtemp.append(avgtemp)
                TXhighs.append(high)
                TXlows.append(low)

# plot CA data
ax3.plot(dates, CAhighs, c='salmon', alpha=0.1)
ax3.plot(dates, CAlows, c='lightsteelblue', alpha=0.1)
ax3.plot(dates, CAavgtemp, c='royalblue', alpha=0.8)
plt.fill_between(dates, CAhighs, CAlows, facecolor='cornflowerblue', alpha=0.4)

# plot TX data
ax3.plot(dates, TXhighs, c='orangered', alpha=0.1)
ax3.plot(dates, TXlows, c='royalblue', alpha=0.1)
ax3.plot(dates, TXavgtemp, c='orange', alpha=0.8)
plt.fill_between(dates, TXhighs, TXlows, facecolor='orange', alpha=0.4)

# Format plot
ax3.set_title("Daily Temperature Range in SF and Austin", fontsize=12)
ax3.set_xlabel('', fontsize=14)
fig.autofmt_xdate()
ax3.set_ylabel("Temperature (°F)", fontsize=10)
ax3.tick_params(axis='both', which='major', labelsize=10)

# Back to the full figure...
# Make custom shapes (using patch from matplotlib.patches) for the legends
city_labels = [Patch(facecolor='cornflowerblue', edgecolor='royalblue',\
                    label='San Francisco'), 
                Patch(facecolor='orange', edgecolor='orange',\
                    label='Austin')]
weather_labels = []
for color, datatype in zip(bar_colors, list(TX_data_by_type.keys())):
    weather_labels.append(Patch(facecolor=color, label=datatype))

# Create legends and format chart
plt.figlegend(fontsize=8, handles=city_labels, bbox_to_anchor=(1.0, 0.525),\
    title='City', facecolor='black', edgecolor='gray')
plt.figlegend(fontsize=8, handles=weather_labels, bbox_to_anchor=(1.0, 0.88), \
    title='Data Type', facecolor='black', edgecolor='gray')
ax1.set_ylabel("Measurement availability by data type", fontsize=10)
ax2.label_outer()

# And the big reveal
plt.show()


