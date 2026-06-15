import fastf1
import pandas as pd

fastf1.Cache.enable_cache('data')

RACES_2024 = [
    'Bahrain', 'Saudi Arabian', 'Australian', 'Japanese', 'Chinese',
    'Miami', 'Emilia Romagna', 'Monaco', 'Canadian', 'Spanish',
    'Austrian', 'British', 'Hungarian', 'Belgian', 'Dutch',
    'Italian', 'Azerbaijan', 'Singapore', 'United States', 'Mexico City',
    'São Paulo', 'Las Vegas', 'Qatar', 'Abu Dhabi'
]

RACES_2022_2023 = [
    'Bahrain', 'Saudi Arabian', 'Australian', 'Miami', 'Emilia Romagna',
    'Monaco', 'Canadian', 'British', 'Austrian', 'French', 'Hungarian',
    'Belgian', 'Dutch', 'Italian', 'Singapore', 'Japanese', 'United States',
    'Mexico City', 'São Paulo', 'Abu Dhabi'
]

RACES_2025 = [
    'Australian', 'Chinese', 'Japanese', 'Bahrain', 'Saudi Arabian',
    'Miami', 'Emilia Romagna', 'Monaco', 'Spanish', 'Canadian', 'Austrian',
    'British', 'Belgian', 'Hungarian', 'Dutch', 'Italian', 'Azerbaijan',
    'Singapore', 'United States', 'Mexico City', 'São Paulo', 'Las Vegas',
    'Qatar', 'Abu Dhabi'
]

def fetch_qualifying(year: int, race: str) -> pd.DataFrame:
    try:
        session = fastf1.get_session(year, race, 'Q')
        session.load(telemetry=False)

        laps = session.laps.pick_quicklaps()
        weather = session.weather_data[['Time', 'AirTemp', 'TrackTemp']].copy()
        laps = pd.merge_asof(laps.sort_values('Time'), weather.sort_values('Time'), on='Time')

        driver_info = session.results[['Abbreviation', 'TeamName']].copy()
        laps = laps.merge(driver_info, left_on='Driver', right_on='Abbreviation', how='left')

        cols = ['Driver', 'TeamName', 'LapNumber', 'LapTime',
                'Compound', 'TyreLife', 'AirTemp', 'TrackTemp']
        laps = laps[cols].dropna(subset=['Driver', 'LapTime', 'Compound'])
        laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
        laps.drop(columns=['LapTime'], inplace=True)
        laps['Race'] = race
        laps['Year'] = year
        return laps

    except Exception as e:
        print(f"  SKIPPED {year} {race}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    all_laps = []

    for year, races in [(2022, RACES_2022_2023), (2023, RACES_2022_2023), (2024, RACES_2024), (2025, RACES_2025)]:
        for race in races:
            print(f"Fetching qualifying {year} {race}...")
            df = fetch_qualifying(year, race)
            if not df.empty:
                all_laps.append(df)
                print(f"  {len(df)} laps")

    if all_laps:
        combined = pd.concat(all_laps, ignore_index=True)
        combined.to_csv('data/qualifying.csv', index=False)
        print(f"\nDone. Total laps: {len(combined)}")
        print("Saved to data/qualifying.csv")
    else:
        print("No data fetched.")