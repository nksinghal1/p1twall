import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error
import xgboost as xgb
import pickle

def load_and_prepare(csv_path: str):
    df = pd.read_csv(csv_path)

    df['LapTimeNorm'] = df.groupby(['Race', 'Year'])['LapTimeSeconds'].transform(
        lambda x: (x - x.mean()) / x.std()
    )

    # Drop rows where normalisation failed (single-lap groups, std=0)
    df = df.dropna(subset=['LapTimeNorm'])
    df = df[~df['LapTimeNorm'].isin([float('inf'), float('-inf')])]

    le_driver = LabelEncoder()
    le_compound = LabelEncoder()
    le_race = LabelEncoder()
    le_team = LabelEncoder()

    df['Driver'] = le_driver.fit_transform(df['Driver'])
    df['Compound'] = le_compound.fit_transform(df['Compound'])
    df['Race'] = le_race.fit_transform(df['Race'])
    df['TeamName'] = le_team.fit_transform(df['TeamName'])

    features = ['Driver', 'TeamName', 'LapNumber', 'Compound',
                'TyreLife', 'AirTemp', 'TrackTemp', 'Race', 'Year']
    target = 'LapTimeNorm'

    X = df[features]
    y = df[target]

    race_stats = df.groupby(['Race', 'Year'])['LapTimeSeconds'].agg(['mean', 'std']).reset_index()

    return X, y, le_driver, le_compound, le_race, le_team, race_stats

def train(csv_path: str):
    X, y, le_driver, le_compound, le_race, le_team, race_stats = load_and_prepare(csv_path)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"MAE (normalised): {mae:.4f} std devs")

    with open('data/model_qualifying.pkl', 'wb') as f:
        pickle.dump({
            'model': model,
            'le_driver': le_driver,
            'le_compound': le_compound,
            'le_race': le_race,
            'le_team': le_team,
            'race_stats': race_stats
        }, f)
    print("Model saved to data/model_qualifying.pkl")

if __name__ == "__main__":
    train('data/qualifying.csv')