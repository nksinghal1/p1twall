import fastf1
import pandas as pd

fastf1.Cache.enable_cache('data')

COUNTRY_FLAGS = {
    'Bahrain': '🇧🇭', 'Saudi Arabia': '🇸🇦', 'Australia': '🇦🇺',
    'Japan': '🇯🇵', 'China': '🇨🇳', 'United States': '🇺🇸',
    'Italy': '🇮🇹', 'Monaco': '🇲🇨', 'Canada': '🇨🇦',
    'Spain': '🇪🇸', 'Austria': '🇦🇹', 'Great Britain': '🇬🇧',
    'Hungary': '🇭🇺', 'Belgium': '🇧🇪', 'Netherlands': '🇳🇱',
    'Azerbaijan': '🇦🇿', 'Singapore': '🇸🇬', 'Mexico': '🇲🇽',
    'Brazil': '🇧🇷', 'Las Vegas': '🇺🇸', 'Qatar': '🇶🇦',
    'Abu Dhabi': '🇦🇪', 'France': '🇫🇷', 'Miami': '🇺🇸',
}

all_races = []

for year in [2022, 2023, 2024, 2025]:
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventFormat'] != 'testing'].copy()
        schedule = schedule[schedule['EventFormat'].notna()].copy()
        for i, row in schedule.iterrows():
            country = row['Country']
            flag = COUNTRY_FLAGS.get(country, '🏁')
            all_races.append({
                'Year': year,
                'Round': row['RoundNumber'],
                'OfficialName': row['EventName'],
                'ShortName': row['OfficialEventName'] if 'OfficialEventName' in row else row['EventName'],
                'Country': country,
                'Flag': flag,
                'Location': row['Location'],
                'DisplayName': f"{flag} {row['EventName']}"
            })
        print(f"{year}: {len(schedule)} races")
    except Exception as e:
        print(f"SKIPPED {year}: {e}")

df = pd.DataFrame(all_races)
df.to_csv('data/race_calendar.csv', index=False)
print(f"\nSaved {len(df)} race entries to data/race_calendar.csv")