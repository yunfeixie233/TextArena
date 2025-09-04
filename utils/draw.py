import matplotlib.pyplot as plt
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Data for the bars
categories = ['Rank-3', 'Rank-2', 'Rank-1']  # Reversed order for bottom-to-top display
values = [3.5, 5.5, 7.0]  # Approximate values based on visual proportions

# Colors for the bars
colors = ['#FF8C69', '#FF8C69', '#87CEEB']  # Orange/salmon for Rank-2&3, light blue for Rank-1

# Create horizontal bars
bars = ax.barh(categories, values, color=colors, height=0.6)

# Add diagonal hatching to the Rank-1 bar (last bar, index 2)
bars[2].set_hatch('///')

# Customize the plot
ax.set_title('Performance\nImprovement', fontsize=16, fontweight='bold', pad=20)

# Remove spines and ticks
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Remove x-axis ticks and labels
ax.set_xticks([])
ax.set_xlabel('')

# Style y-axis
ax.tick_params(axis='y', which='both', left=False, right=False, labelsize=12)
ax.set_ylabel('')

# Adjust layout
plt.tight_layout()

# Show the plot
plt.savefig('performance_improvement.png')