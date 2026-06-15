import fastf1
import pandas as pd
import time

fastf1.Cache.enable_cache('data')

calendar = pd.read_csv('data/race_calendar.csv')

CAR_DNF_STATUSES = [
    'Engine', 'Gearbox', 'Hydraulics', 'Electrical', 'Power Unit',
    'Turbo', 'Brakes', 'Suspension', 'Oil leak', 'Oil pressure',
    'Water leak', 'Water pressure', 'Fuel system', 'Fuel pressure',
    'Exhaust', 'Clutch', 'Driveshaft', 'Wheel', 'Tyre', 'Fire',
    'Mechanical', 'Technical', 'Vibrations', 'ERS', 'MGU-H', 'MGU-K'
]

DRIVER_DNF_STATUSES = [
    'Accident', 'Collision', 'Collision damage', 'Spun off',
    'Fatal accident', 'Injury', 'Withdrew', 'Disqualified'
]

def categorise_status(status):
    if status in ['Finished'] or '+' in str(status) or 'Lap' in str(status):
        return 'Finished'
    for s in CAR_DNF_STATUSES:
        if s.lower() in str(status).lower():
            return 'CarDNF'
    for s in DRIVER_DNF_STATUSES:
        if s.lower() in str(status).lower():
            return 'DriverDNF'
    return 'CarDNF'  # default unknown to car DNF

all_grids = []

for _, race in calendar.iterrows():
    year = int(race['Year'])
    name = race['OfficialName']
    try:
        session = fastf1.get_session(year, name, 'R')
        session.load(telemetry=False)
        results = session.results[[
            'Abbreviation', 'TeamName', 'GridPosition',
            'Position', 'ClassifiedPosition', 'Status', 'Points'
        ]].copy()
        results['Year'] = year
        results['Race'] = name
        results['Round'] = race['Round']
        results['DNFType'] = results['Status'].apply(categorise_status)
        all_grids.append(results)
        print(f"  {year} {name}: {len(results)} drivers")
    except Exception as e:
        print(f"  SKIPPED {year} {name}: {e}")
    time.sleep(2)

combined = pd.concat(all_grids, ignore_index=True)
combined.to_csv('data/grid_positions.csv', index=False)
print(f"\nSaved {len(combined)} entries to data/grid_positions.csv")

# Summary of DNF types per team per season
print("\n── DNF Summary by Team/Season ──")
dnfs = combined[combined['DNFType'] != 'Finished']
summary = dnfs.groupby(['Year', 'TeamName', 'DNFType']).size().reset_index(name='Count')
print(summary.to_string())