import fastf1
import pandas as pd

fastf1.Cache.enable_cache('data')

all_drivers = []

for year in [2022, 2023, 2024, 2025]:
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        first_race = schedule[schedule['EventFormat'] != 'testing'].iloc[0]['EventName']
        session = fastf1.get_session(year, first_race, 'R')
        session.load(telemetry=False)
        results = session.results[['Abbreviation','FirstName','LastName','TeamName','CountryCode']].copy()
        results['Year'] = year
        all_drivers.append(results)
        print(f"{year}: {len(results)} drivers")
    except Exception as e:
        print(f"SKIPPED {year}: {e}")

combined = pd.concat(all_drivers, ignore_index=True)
combined.drop_duplicates(subset=['Abbreviation'], keep='last', inplace=True)
combined['FullName'] = combined['FirstName'] + ' ' + combined['LastName']
combined.to_csv('data/driver_info.csv', index=False)
print(f"\nSaved {len(combined)} drivers to data/driver_info.csv")
print(combined[['Abbreviation','FullName','TeamName','CountryCode']].to_string())