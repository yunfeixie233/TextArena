import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

# -------------------------------
# Configuration block
CSV_PATH = "leaderboard_analysis_detailed_results.csv"        # path to your CSV
FIG_SIZE = (12, 8)                    # wider aspect ratio for better readability
TITLE_FONT_SIZE = 22
AXIS_FONT_SIZE = 16
CELL_FONT_SIZE = 14
BOLD_CELL_VALUES = False              # whether to make cell values bold
AXIS_LABEL_ROTATION = 45
COLOR_MAP = "Blues"                   # sequential colormap

# Paper-quality settings
DPI = 300                             # high resolution for publication
LINE_WIDTH = 1.0                      # thicker grid lines
CBAR_SHRINK = 0.8                     # shrink colorbar height
CBAR_ASPECT = 20                      # colorbar aspect ratio
SAVE_FORMAT = "pdf"                   # vector format for papers

# Colorbar label controls  
COLORBAR_LABEL = "Elo Rating"         # full label text
COLORBAR_FONT_SIZE = 16               # font size for colorbar label

# Data field to plot
VALUE_FIELD = "Elo"                   # use Elo values for cell colors

# Mapping from raw Run_Name to display label on x-axis
RUN_NAME_MAP = {
    "Poker-v0_5x_CHEAP_MODELS_basic": "Basic",
    "Poker-v0_5x_CHEAP_MODELS_chain_of_thought": "Chain of Thought",
    "Poker-v0_5x_CHEAP_MODELS_few_shot": "Few-Shot",
    "Poker-v0_5x_CHEAP_MODELS_generated_knowledge": "Generated Knowledge", 
    "Poker-v0_5x_CHEAP_MODELS_tree_of_thoughts": "Tree of Thoughts",
}

# Model name mapping for cleaner display
MODEL_NAME_MAP = {
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gpt-4o-mini": "GPT-4o Mini", 
    "grok-3-mini": "Grok 3 Mini",
    "kimi-k2": "Kimi K2",
    "llama-4-maverick": "Llama 4 Maverick",
    "qwen3-235b-a22b-2507": "Qwen3 235B"
}

# Desired column order on the x-axis (omit any you do not want)
RUN_ORDER = ["Basic", "Chain of Thought", "Few-Shot", "Generated Knowledge", "Tree of Thoughts"]   
# -------------------------------

# Read CSV
csv_path = Path(CSV_PATH)
df_raw = pd.read_csv(csv_path)

# Validate required columns
required_cols = {"Model", "Run_Name", VALUE_FIELD}
missing = required_cols - set(df_raw.columns)
if missing:
    raise ValueError(f"CSV missing columns: {sorted(missing)}")

# Map raw run names to short labels and clean model names
df_raw["Run_Short"] = df_raw["Run_Name"].map(RUN_NAME_MAP).fillna(df_raw["Run_Name"])
df_raw["Model_Clean"] = df_raw["Model"].map(MODEL_NAME_MAP).fillna(df_raw["Model"])

# Pivot so rows are models and columns are run names, values are Elo
heat_df = df_raw.pivot_table(
    index="Model_Clean",
    columns="Run_Short", 
    values=VALUE_FIELD,
    aggfunc="mean"    # in case the CSV has duplicates
)

# Reorder columns per RUN_ORDER when present
ordered_cols = [c for c in RUN_ORDER if c in heat_df.columns] + \
               [c for c in heat_df.columns if c not in RUN_ORDER]
heat_df = heat_df.reindex(columns=ordered_cols)

# Sort models alphabetically (change as you like)
heat_df = heat_df.sort_index()

# Plot heatmap with paper-quality settings
fig, ax = plt.subplots(figsize=FIG_SIZE)

# Configure cell annotation style
annot_kws = {"size": CELL_FONT_SIZE}
if BOLD_CELL_VALUES:
    annot_kws["weight"] = "bold"

# Create heatmap with enhanced visual settings
heatmap = sns.heatmap(
    heat_df,
    annot=True,
    cmap=COLOR_MAP,
    cbar_kws={
        "shrink": CBAR_SHRINK,
        "aspect": CBAR_ASPECT,
        "label": COLORBAR_LABEL
    },
    linewidths=LINE_WIDTH,
    linecolor="white",
    fmt=".0f",                        # integer format for cleaner look
    annot_kws=annot_kws,
    square=True,                      # square cells for better proportions
    ax=ax
)

# Set colorbar label font size
cbar = heatmap.collections[0].colorbar
cbar.set_label(COLORBAR_LABEL, size=COLORBAR_FONT_SIZE)

# Enhanced title and labels
plt.title("Model Performance Across Prompt Strategies", fontsize=TITLE_FONT_SIZE, pad=20, fontweight='bold')
plt.xlabel("Prompt Strategy", fontsize=AXIS_FONT_SIZE, fontweight='bold')
plt.ylabel("Model", fontsize=AXIS_FONT_SIZE, fontweight='bold')

# Rotate x-axis labels for better readability
plt.xticks(rotation=AXIS_LABEL_ROTATION, ha="right", fontsize=AXIS_FONT_SIZE)
plt.yticks(rotation=0, fontsize=AXIS_FONT_SIZE)

# Adjust layout and save
plt.tight_layout()
plt.savefig(f"heatmap.{SAVE_FORMAT}", dpi=DPI, bbox_inches='tight', facecolor='white')
plt.savefig("heatmap.png", dpi=DPI, bbox_inches='tight', facecolor='white')  # keep PNG for compatibility
plt.show()
