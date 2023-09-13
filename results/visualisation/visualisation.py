import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import math


block_num = 10
shapes_num = 1000




sizes = [10, 25, 50, 100, 200, 500]
solve_types = ['parallel', 'sequential']

parallel_avgs = []
sequential_avgs = []

error_percentages = []


fill_avgs = []
lshaped_avgs = []
empty_avgs = []

for size in sizes:
    if size == 200:
        shapes_num = 100
    elif size == 500:
        shapes_num = 10
    path = f"/home/matt/Repos/parallel-squares/results/json_results/results_size_{size}_shapes_{shapes_num}.json"
    with open(path) as data:
        obj = json.load(data)
        if obj['_version'] > 1:
            raise Exception('Save file with incorrect version')
        parallel_avgs.append(obj['avg_moves_monotone'])
        sequential_avgs.append(obj['avg_moves_seq']) 
        
        error_percentage = (len(obj['errors_monotone'])/shapes_num)
        error_percentages.append(error_percentage) 

        fill_nums = [fill for fill, _, _ in obj['all_move_nums']]
        lshaped_nums = [lshaped for _, lshaped, _ in obj['all_move_nums']]
        empty_nums = [empty for _, _, empty in obj['all_move_nums']]

        fill_avg = sum(fill_nums)/len(fill_nums)
        lshaped_avg = sum(lshaped_nums)/len(lshaped_nums)
        empty_avg = sum(empty_nums)/len(empty_nums)

        fill_avgs.append(fill_avg)
        lshaped_avgs.append(lshaped_avg)
        empty_avgs.append(empty_avg)

    
# Set the width of the bars
bar_width = 0.35

# Create an array for the x-axis positions
x = np.arange(len(sizes))

# # Create the double bar chart
fig, ax = plt.subplots()
parallel_bars = ax.bar(x - bar_width/2, parallel_avgs, bar_width, label='Parallel')
sequential_bars = ax.bar(x + bar_width/2, sequential_avgs, bar_width, label='Sequential')



# Set the x-axis labels
ax.set_xticks(x)
ax.set_xticklabels(sizes)
ax.set_xlabel('Number of blocks in the configuration')

# Set the y-axis label
ax.set_ylabel('Average number of moves')

# Set the chart title
ax.set_title('Average number of moves for both algorithms')

# Add a legend
ax.legend()

# Show the plot
plt.show()

move_types = ["Fill", "L-shaped", "Emptying"]



         


bar_width = 0.25

# Create the double bar chart
fig, ax = plt.subplots()
fill_bars = ax.bar(x - bar_width, fill_avgs, bar_width, label='Fill Boundary')
lshaped_bars = ax.bar(x, lshaped_avgs, bar_width, label='L-shaped moves')
empty_bars = ax.bar(x + bar_width, empty_avgs, bar_width, label='Empty Boundary')

# Set the x-axis labels
ax.set_xticks(x)
ax.set_xticklabels(sizes)
ax.set_xlabel('Number of blocks in the configuration')

# Set the y-axis label
ax.set_ylabel('Average number of moves')

# Set the chart title
ax.set_title('Average number of moves for the different stages per number of blocks')

# Add a legend
ax.legend()

# Show the plot
plt.show()


# Set the width of the bars
bar_width = 0.35

# Create an array for the x-axis positions
x = np.arange(len(sizes))

# # Create the double bar chart
fig, ax = plt.subplots()
parallel_bars = ax.bar(x, error_percentages, bar_width,)




# Set the x-axis labels
ax.set_xticks(x)
ax.set_xticklabels(sizes)
ax.set_xlabel('Number of blocks in the configuration')

# Set the y-axis label
ax.set_ylabel('Error percentage')

# Set the chart title
ax.set_title('Percentage of configurations')

# Add a legend
ax.legend()

# Show the plot
plt.show()