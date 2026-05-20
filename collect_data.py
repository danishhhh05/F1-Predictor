import fastf1
import pandas as pd
import time

fastf1.Cache.enable_cache('data/cache')

def collect_race_data(start_year=2022, end_year=2024):
    all_races = []

    for year in range(start_year, end_year + 1):
        print(f"\n📅 Collecting {year} season...")

        schedule = fastf1.get_event_schedule(year, include_testing=False)
        time.sleep(2)  # pause between requests

        for _, event in schedule.iterrows():
            round_num = event['RoundNumber']
            gp_name = event['EventName']

            try:
                print(f"  🏁 {gp_name}...")
                session = fastf1.get_session(year, round_num, 'R')
                session.load(telemetry=False, weather=False, messages=False)

                results = session.results

                for _, driver in results.iterrows():
                    all_races.append({
                        'year': year,
                        'round': round_num,
                        'gp_name': gp_name,
                        'driver': driver['Abbreviation'],
                        'team': driver['TeamName'],
                        'grid_position': driver['GridPosition'],
                        'finish_position': driver['Position'],
                        'points': driver['Points'],
                        'status': driver['Status'],
                    })

                time.sleep(3)  # pause between each race

            except Exception as e:
                print(f"  ⚠️ Skipped {gp_name}: {e}")
                time.sleep(5)  # longer pause on error
                continue

    df = pd.DataFrame(all_races)
    df.to_csv('data/race_results.csv', index=False)
    print(f"\n✅ Done! Saved {len(df)} rows to data/race_results.csv")
    return df

if __name__ == "__main__":
    df = collect_race_data()
    print(df.head(10))