import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import argparse
import os

# ====================
# CONFIGURABLE SETTINGS
# ====================
FONT_SIZE = 11
BAR_WIDTH = 0.6
BAR_SPACING = 1.0
BAR_BORDER_WIDTH = 2  # Border width for bars
ICON_SIZE = 0.25  # Size of icons as fraction of figure width
ICON_HEIGHT_ABOVE_BARS = 0.20   # Distance above bars where icons are placed (as fraction of y-range)
ICON_PIXEL_SIZE = (128, 128)  # Pixel size to resize all icons to (width, height)
FIGURE_SIZE = (12, 8)
Y_LIMIT = (0, 1.0)  # Win rate from 0 to 1
GRID_ALPHA = 0.3
ERROR_BAR_CAPSIZE = 5
ERROR_BAR_WIDTH = 2
JITTER_AMOUNT = 0.15  # Amount of horizontal jitter for dots
DOT_SIZE = 60  # Size of scatter dots
DOT_BORDER_WIDTH = 2  # Border width for scatter points

# Colors from the provided figure (hex codes)
COLORS = {
    'gemini-2.5-flash': '#92A5D1',  # Blue
    'kimi-k2': '#C5DFF4',            # Light blue
    'grok-3-mini': '#7C9895',        # Teal
    'llama-4-maverick': '#C9DCC4',   # Light green
    'qwen3-235b-a22b-2507': '#DAA87C',  # Orange/tan
    'gpt-4o-mini': '#F4EEAC',         # Light yellow
    'chatgpt-4o-latest': '#89CFF0',  # Light blue
    'deepseek-r1': '#FFB6C1',        # Light pink
    'o3-mini': '#FFD700'             # Gold
}

# Model definitions with abbreviations and icon paths
MODEL_INFO = {
    'gemini-2.5-flash': {
        'abbrev': 'Gemini-2.5-flash',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/gemini.jpeg'
    },
    'kimi-k2': {
        'abbrev': 'Kimi-K2',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/deepseek.png'
    },
    'grok-4': {
        'abbrev': 'Grok-4',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/grok.png'
    },
    'llama-4-maverick': {
        'abbrev': 'Llama-4',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/llama4.jpeg'
    },
    'qwen3-235b-a22b-2507': {
        'abbrev': 'Qwen3-235B',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/qwen.png'
    },
    'gpt-4o-mini': {
        'abbrev': 'GPT-4o-mini',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/gpt-4o.png'
    },
    'chatgpt-4o-latest': {
        'abbrev': 'GPT-4o',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/gpt-4o.png'
    },
    'deepseek-r1': {
        'abbrev': 'DeepSeek-R1',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/deepseek.png'
    },
    'o3-mini': {
        'abbrev': 'O3-mini',
        'icon_path': '/teamspace/studios/this_studio/TextArena/utils/icon/gpt-4o.png'
    }
}

# ====================
# DATA LOADING
# ====================
# Parse command line arguments
parser = argparse.ArgumentParser(description='Draw jitter plot from detailed results CSV')
parser.add_argument('csv_file', type=str, help='Path to detailed results CSV file')
parser.add_argument('--output', type=str, default='jitter_plot.png', help='Output file name')
args = parser.parse_args()

csv_file = args.csv_file

# Read CSV data
df_detailed = pd.read_csv(csv_file)
# Clean column names (remove any extra spaces)
df_detailed.columns = df_detailed.columns.str.strip()
# Clean model names
df_detailed['Model'] = df_detailed['Model'].str.strip()

# Calculate statistics for each model
df_stats = df_detailed.groupby('Model').agg({
    'Win_Rate': ['mean', 'std', 'count']
}).reset_index()

# Flatten column names
df_stats.columns = ['Model', 'Mean_Win_Rate', 'Std_Win_Rate', 'Count']

# Handle NaN std deviation (for models with only one data point)
df_stats['Std_Win_Rate'] = df_stats['Std_Win_Rate'].fillna(0)

# Sort by mean win rate (descending)
df_stats = df_stats.sort_values('Mean_Win_Rate', ascending=False)

# Get individual data points for visualization
df_individual = df_detailed[['Model', 'Win_Rate']].copy()

# ====================
# PLOTTING
# ====================
fig, ax = plt.subplots(figsize=FIGURE_SIZE)

# Create x positions for bars
models = df_stats['Model'].tolist()
x_positions = np.arange(len(models)) * BAR_SPACING

# Create model names with fallback for unknown models
model_names = []
for model in models:
    if model in MODEL_INFO:
        model_names.append(MODEL_INFO[model]['abbrev'])
    else:
        # Use shortened version of model name as fallback
        model_names.append(model.split('/')[-1][:10])

# Create bars with fill color and optional border
bars = []
np.random.seed(42)  # For consistent jitter
for i, (idx, row) in enumerate(df_stats.iterrows()):
    model = row['Model']
    mean = row['Mean_Win_Rate']
    std = row['Std_Win_Rate']
    
    # Get color with fallback to gray
    color = COLORS.get(model, '#808080')
    
    # Create bar with fill color and optional border
    bar = ax.bar(x_positions[i], mean, BAR_WIDTH,
                  facecolor=color,  # Fill color
                  edgecolor='black',  # Black border
                  linewidth=BAR_BORDER_WIDTH,  # Border width
                  yerr=std,
                  capsize=ERROR_BAR_CAPSIZE,
                  error_kw={'linewidth': ERROR_BAR_WIDTH, 'color': 'black'})
    bars.append(bar)
    
    # Add individual data points with jitter (filled circles with black border)
    model_points = df_individual[df_individual['Model'] == model]['Win_Rate']
    x_jittered = np.random.uniform(x_positions[i] - JITTER_AMOUNT * BAR_WIDTH, 
                                   x_positions[i] + JITTER_AMOUNT * BAR_WIDTH, 
                                   size=len(model_points))
    ax.scatter(x_jittered, model_points, 
               color=color,  # Fill color
               edgecolor='black',  # Black border
               linewidth=DOT_BORDER_WIDTH,  # Border width
               s=DOT_SIZE, 
               alpha=0.7, 
               zorder=5)

# ====================
# ICON PLACEMENT
# ====================
def add_icon(ax, icon_path, x, y, size):
    try:
        # Load and resize image using PIL to ensure consistent size
        with Image.open(icon_path) as pil_img:
            # Convert to RGBA if not already
            if pil_img.mode != 'RGBA':
                pil_img = pil_img.convert('RGBA')
            # Resize to specified pixel dimensions
            pil_img = pil_img.resize(ICON_PIXEL_SIZE, Image.Resampling.LANCZOS)
            # Convert PIL image to numpy array
            img_array = np.array(pil_img)
        
        # Create OffsetImage with the resized image
        imagebox = OffsetImage(img_array, zoom=size)
        # Create annotation box
        ab = AnnotationBbox(imagebox, (x, y), 
                           frameon=False,
                           box_alignment=(0.5, 0))
        ax.add_artist(ab)
    except Exception as e:
        # If icon file not found or error occurs, add text placeholder
        print(f"Warning: Could not load icon {icon_path}: {e}")
        ax.text(x, y, '●', fontsize=20, ha='center', va='bottom', 
                color='gray')


# Add icons above bars
y_range = Y_LIMIT[1] - Y_LIMIT[0]
for i, model in enumerate(models):
    bar_height = bars[i][0].get_height()
    icon_y = bar_height + ICON_HEIGHT_ABOVE_BARS * y_range
    
    # Get icon path with fallback
    if model in MODEL_INFO:
        icon_path = MODEL_INFO[model]['icon_path']
    else:
        icon_path = None  # Will show placeholder
    
    if icon_path:
        add_icon(ax, icon_path, x_positions[i], icon_y, ICON_SIZE)
    else:
        # Add text placeholder for unknown models
        ax.text(x_positions[i], icon_y, '?', fontsize=20, ha='center', va='bottom', 
                color='gray', weight='bold')

# ====================
# FORMATTING
# ====================
# Set labels and title
ax.set_ylabel('Win Rate', fontsize=FONT_SIZE + 2, fontweight='bold')
ax.set_ylim(Y_LIMIT)

# Set x-axis
ax.set_xticks(x_positions)
ax.set_xticklabels(model_names, rotation=45, ha='right', fontsize=FONT_SIZE)

# Format y-axis as percentages
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{int(y*100)}%'))

# Add grid
ax.grid(True, axis='y', alpha=GRID_ALPHA, linestyle='--', linewidth=0.5)
ax.set_axisbelow(True)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Make remaining spines thicker
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)

# Add subtle background
ax.set_facecolor('#FAFAFA')

# Add a horizontal line at 50% win rate
ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1.5)

# Print statistics to console
print("\nModel Performance Statistics:")
print("-" * 60)
print(f"{'Model':<20} {'Mean Win Rate':>15} {'Std Dev':>12} {'N':>5}")
print("-" * 60)
for _, row in df_stats.iterrows():
    model_short = MODEL_INFO.get(row['Model'], {'abbrev': row['Model'].split('/')[-1][:10]})['abbrev']
    print(f"{model_short:<20} {row['Mean_Win_Rate']:>15.3f} {row['Std_Win_Rate']:>12.3f} {row['Count']:>5}")
print("-" * 60)

# Tight layout and save
plt.tight_layout()
plt.savefig(args.output)
print(f"\nPlot saved to: {args.output}")