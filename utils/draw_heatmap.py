import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

# -------------------------------
# Configuration block
CSV_PATH = "game_logs/multi_template_run_20250904_180218_Poker-v0_5games_CHEAP_MODELS/analysis/cross_template_Poker-v0_5games_CHEAP_MODELS_detailed_results.csv"        # path to your CSV
# CSV_PATH = "leaderboard_analysis_detailed_results.csv"
# CSV_PATH = "game_logs/multi_template_run_20250901_021830_Poker-v0_5games_CHEAP_MODELS/analysis/cross_template_Poker-v0_5games_CHEAP_MODELS_detailed_results.csv"
FIG_SIZE = (12, 8)                    # wider aspect ratio for better readability
SHOW_TITLE = False                     # whether to display the chart title
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

# Mode detection and configuration
COT_MODE_KEYWORD = "chain_of_thought" # keyword to detect CoT mode
VARIANT_MODE_KEYWORD = "variant"      # keyword to detect variant mode

# Data field to plot
VALUE_FIELD = "Elo"                   # use Elo values for cell colors

# CoT mode mapping from raw Run_Name to display label on x-axis
COT_RUN_NAME_MAP = {
    "Poker-v0_5x_CHEAP_MODELS_basic": "Basic",
    "Poker-v0_5x_CHEAP_MODELS_chain_of_thought": "Chain of Thought",
    "Poker-v0_5x_CHEAP_MODELS_few_shot": "Few-Shot",
    "Poker-v0_5x_CHEAP_MODELS_generated_knowledge": "Generated Knowledge", 
    "Poker-v0_5x_CHEAP_MODELS_tree_of_thoughts": "Tree of Thoughts",
}

# Variant mode mapping from raw Run_Name to display label on x-axis
VARIANT_RUN_NAME_MAP = {
    "Poker-v0_5x_CHEAP_MODELS_basic": "Basic",
    "Poker-v0_5x_CHEAP_MODELS_basic_variant_1": "Variant 1",
    "Poker-v0_5x_CHEAP_MODELS_basic_variant_2": "Variant 2",
    "Poker-v0_5x_CHEAP_MODELS_basic_variant_3": "Variant 3",
    "Poker-v0_5x_CHEAP_MODELS_basic_variant_4": "Variant 4",
    "Poker-v0_5x_CHEAP_MODELS_basic_variant_5": "Variant 5",

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

# Desired column order on the x-axis for each mode
COT_RUN_ORDER = ["Basic", "Chain of Thought", "Few-Shot", "Generated Knowledge", "Tree of Thoughts"]
VARIANT_RUN_ORDER = ["Basic", "Variant 1", "Variant 2", "Variant 3", "Variant 4", "Variant 5"]   
# -------------------------------

# Read CSV
csv_path = Path(CSV_PATH)
df_raw = pd.read_csv(csv_path)

# Validate required columns
required_cols = {"Model", "Run_Name", VALUE_FIELD}
missing = required_cols - set(df_raw.columns)
if missing:
    raise ValueError(f"CSV missing columns: {sorted(missing)}")

# Detect mode based on run names
cot_mode = any(COT_MODE_KEYWORD in run_name for run_name in df_raw["Run_Name"])
variant_mode = any(VARIANT_MODE_KEYWORD in run_name for run_name in df_raw["Run_Name"])

print(f"CoT mode detected: {cot_mode}")
print(f"Variant mode detected: {variant_mode}")

# Create appropriate mapping based on mode
if variant_mode:
    # Mode 2: Variant mode - use predefined variant mapping
    # Validate all run names are in the mapping
    unmapped_runs = set(df_raw["Run_Name"]) - set(VARIANT_RUN_NAME_MAP.keys())
    if unmapped_runs:
        raise ValueError(f"Variant mode: Run names not in VARIANT_RUN_NAME_MAP: {sorted(unmapped_runs)}")
    
    df_raw["Run_Short"] = df_raw["Run_Name"].map(VARIANT_RUN_NAME_MAP)
    run_order = VARIANT_RUN_ORDER
    mode_suffix = "variant"
    chart_title = "Model Performance Across Prompt Variants"
    x_label = "Prompt Variant"
    print(f"Using Variant mode")
    print(f"Variant mapping: {VARIANT_RUN_NAME_MAP}")
elif cot_mode:
    # Mode 1: CoT mode - use predefined CoT mapping
    # Validate all run names are in the mapping
    unmapped_runs = set(df_raw["Run_Name"]) - set(COT_RUN_NAME_MAP.keys())
    if unmapped_runs:
        raise ValueError(f"CoT mode: Run names not in COT_RUN_NAME_MAP: {sorted(unmapped_runs)}")
    
    df_raw["Run_Short"] = df_raw["Run_Name"].map(COT_RUN_NAME_MAP)
    run_order = COT_RUN_ORDER
    mode_suffix = "cot"
    chart_title = "Model Performance Across Prompt Strategies"
    x_label = "Prompt Strategy"
    print(f"Using CoT mode")
    print(f"CoT mapping: {COT_RUN_NAME_MAP}")
else:
    # Default mode - use CoT mapping as fallback
    # Validate all run names are in the mapping
    unmapped_runs = set(df_raw["Run_Name"]) - set(COT_RUN_NAME_MAP.keys())
    if unmapped_runs:
        raise ValueError(f"Strategy mode: Run names not in COT_RUN_NAME_MAP: {sorted(unmapped_runs)}")
    
    df_raw["Run_Short"] = df_raw["Run_Name"].map(COT_RUN_NAME_MAP)
    run_order = COT_RUN_ORDER
    mode_suffix = "strategy"
    chart_title = "Model Performance Across Prompt Strategies"
    x_label = "Prompt Strategy"
    print(f"Using regular strategy mode")

# Clean model names
df_raw["Model_Clean"] = df_raw["Model"].map(MODEL_NAME_MAP).fillna(df_raw["Model"])

# Pivot so rows are models and columns are run names, values are Elo
heat_df = df_raw.pivot_table(
    index="Model_Clean",
    columns="Run_Short", 
    values=VALUE_FIELD,
    aggfunc="mean"    # in case the CSV has duplicates
)

# Reorder columns per run_order when present
ordered_cols = [c for c in run_order if c in heat_df.columns] + \
               [c for c in heat_df.columns if c not in run_order]
heat_df = heat_df.reindex(columns=ordered_cols)

# Sort models alphabetically (change as you like)
heat_df = heat_df.sort_index()

# Create ranking dataframe for cell annotations
# For each column (run), rank models from best (1st) to worst
ranking_df = heat_df.rank(method="dense", ascending=False).astype(int)

# Create annotation labels with ordinal suffixes
def get_ordinal_suffix(n):
    if 10 <= n % 100 <= 20:  # special case for 11th, 12th, 13th
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")

# Convert rankings to ordinal strings (1st, 2nd, 3rd, etc.)
annotation_df = ranking_df.copy()
for col in annotation_df.columns:
    for idx in annotation_df.index:
        rank = ranking_df.loc[idx, col]
        if pd.notna(rank):
            annotation_df.loc[idx, col] = f"{rank}{get_ordinal_suffix(rank)}"
        else:
            annotation_df.loc[idx, col] = "N/A"

# Plot heatmap with paper-quality settings
fig, ax = plt.subplots(figsize=FIG_SIZE)

# Configure cell annotation style
annot_kws = {"size": CELL_FONT_SIZE}
if BOLD_CELL_VALUES:
    annot_kws["weight"] = "bold"

# Create heatmap with enhanced visual settings
heatmap = sns.heatmap(
    heat_df,                          # Elo values for colors
    annot=annotation_df,              # Custom ranking annotations
    cmap=COLOR_MAP,
    cbar_kws={
        "shrink": CBAR_SHRINK,
        "aspect": CBAR_ASPECT,
        "label": COLORBAR_LABEL
    },
    linewidths=LINE_WIDTH,
    linecolor="white",
    fmt="",                           # no formatting since we're using custom annotations
    annot_kws=annot_kws,
    square=True,                      # square cells for better proportions
    ax=ax
)

# Set colorbar label font size
cbar = heatmap.collections[0].colorbar
cbar.set_label(COLORBAR_LABEL, size=COLORBAR_FONT_SIZE)

# Enhanced title and labels
if SHOW_TITLE:
    plt.title(chart_title, fontsize=TITLE_FONT_SIZE, pad=20, fontweight='bold')
plt.xlabel(x_label, fontsize=AXIS_FONT_SIZE, fontweight='bold')
plt.ylabel("Model", fontsize=AXIS_FONT_SIZE, fontweight='bold')

# Rotate x-axis labels for better readability
plt.xticks(rotation=AXIS_LABEL_ROTATION, ha="right", fontsize=AXIS_FONT_SIZE)
plt.yticks(rotation=0, fontsize=AXIS_FONT_SIZE)

# Adjust layout and save with mode-specific filename
plt.tight_layout()
plt.savefig(f"heatmap_{mode_suffix}.{SAVE_FORMAT}", dpi=DPI, bbox_inches='tight', facecolor='white')
plt.savefig(f"heatmap_{mode_suffix}.png", dpi=DPI, bbox_inches='tight', facecolor='white')
plt.show()
