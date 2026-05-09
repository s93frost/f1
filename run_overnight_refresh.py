# run_overnight_refresh.py

from app import refresh_all_drivers, drivers_all_years, previous_race
from app import all_drivers_dict, DRIVERS_SEASON, CURRENT_SEASON

def main():
    global DRIVERS_SEASON
    DRIVERS_SEASON = refresh_all_drivers(
        all_drivers_dict,
        drivers_all_years,
        previous_race,
        DRIVERS_SEASON,
        CURRENT_SEASON
    )

if __name__ == "__main__":
    main()
