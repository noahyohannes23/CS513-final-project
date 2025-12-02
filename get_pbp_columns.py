import nflreadpy as nfl
from helpers import explore_columns

# Load a small sample of pbp data (just 2023 season)
print("Loading pbp data for 2023...")
pbp = nfl.load_pbp(2023)

print(f"Loaded {pbp.height} rows with {len(pbp.columns)} columns\n")

# Get list of all columns
print("All columns in pbp:")
for i, col in enumerate(pbp.columns, 1):
    print(f"{i}. {col}")

# Generate HTML exploration
print("\nGenerating HTML column explorer...")
explore_columns(pbp, output='html', save_path='pbp_columns.html')

# Also create a simple column list file for reference
with open('pbp_column_list.txt', 'w') as f:
    f.write(f"Play-by-Play DataFrame Columns ({len(pbp.columns)} total)\n")
    f.write("=" * 60 + "\n\n")
    for col in pbp.columns:
        f.write(f"{col}\n")

print("[OK] Created pbp_columns.html")
print("[OK] Created pbp_column_list.txt")
