import pandas as pd

# Load all the CSVs
races = pd.read_csv('data/races.csv')
results = pd.read_csv('data/results.csv')
drivers = pd.read_csv('data/drivers.csv')
constructors = pd.read_csv('data/constructors.csv')
qualifying = pd.read_csv('data/qualifying.csv')
driver_standings = pd.read_csv('data/driver_standings.csv')
constructor_standings = pd.read_csv('data/constructor_standings.csv')
status = pd.read_csv('data/status.csv')

# Only use modern F1 (2010 onwards - more relevant for predictions)
races = races[races['year'] >= 2010]

# Merge results with race info
df = results.merge(races[['raceId', 'year', 'round', 'circuitId', 'name']], on='raceId')

# Merge driver info
df = df.merge(drivers[['driverId', 'driverRef', 'nationality']], on='driverId')

# Merge constructor info
df = df.merge(constructors[['constructorId', 'constructorRef', 'nationality']], 
              on='constructorId', suffixes=('_driver', '_constructor'))

# Merge qualifying position
qual = qualifying[['raceId', 'driverId', 'position']].rename(columns={'position': 'quali_position'})
df = df.merge(qual, on=['raceId', 'driverId'], how='left')

# Merge status (to know if DNF)
df = df.merge(status[['statusId', 'status']], on='statusId')

# Clean up finish position (some are \N for DNFs)
df['positionOrder'] = pd.to_numeric(df['positionOrder'], errors='coerce')
df['grid'] = pd.to_numeric(df['grid'], errors='coerce')
df['points'] = pd.to_numeric(df['points'], errors='coerce')
df['quali_position'] = pd.to_numeric(df['quali_position'], errors='coerce')

# Create target columns
df['won_race'] = (df['positionOrder'] == 1).astype(int)
df['podium'] = (df['positionOrder'] <= 3).astype(int)
df['dnf'] = (~df['status'].str.contains('Finished|Lap', na=False)).astype(int)

# Add driver standings before each race (championship position)
driver_standings['points'] = pd.to_numeric(driver_standings['points'], errors='coerce')
driver_standings['position'] = pd.to_numeric(driver_standings['position'], errors='coerce')

ds = driver_standings[['raceId', 'driverId', 'points', 'position']].rename(
    columns={'points': 'driver_champ_points', 'position': 'driver_champ_pos'})
df = df.merge(ds, on=['raceId', 'driverId'], how='left')

# Add constructor standings
cs = constructor_standings[['raceId', 'constructorId', 'points', 'position']].rename(
    columns={'points': 'constructor_champ_points', 'position': 'constructor_champ_pos'})
df = df.merge(cs, on=['raceId', 'constructorId'], how='left')

# Select final features
final_df = df[[
    'raceId', 'year', 'round', 'circuitId', 'name',
    'driverRef', 'constructorRef',
    'grid', 'quali_position',
    'driver_champ_points', 'driver_champ_pos',
    'constructor_champ_points', 'constructor_champ_pos',
    'positionOrder', 'points', 'status',
    'won_race', 'podium', 'dnf'
]].copy()

final_df = final_df.dropna(subset=['grid', 'positionOrder'])

final_df.to_csv('data/processed_data.csv', index=False)
print(f"✅ Processed data saved! Shape: {final_df.shape}")
print(f"\nSample:")
print(final_df.head())
print(f"\nWin rate check: {final_df['won_race'].sum()} winners from {final_df['raceId'].nunique()} races")