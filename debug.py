import pandas as pd
grid_pos = pd.read_csv('data/grid_positions.csv')
race_df = pd.read_csv('data/all_seasons.csv')

print("grid_pos race names sample:")
print(grid_pos['Race'].unique()[:5])

print("\nrace_df race names sample:")
print(race_df['Race'].unique()[:5])