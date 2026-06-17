import pandas as pd

def validate_weather_data(df: pd.DataFrame):
    print("SEARCH: Running Data Quality Checks...\n")

    report = {}

    # -----------------------------
    # 1. Missing Values Check
    # -----------------------------
    null_counts = df.isnull().sum()
    report["missing_values"] = null_counts.to_dict()

    # -----------------------------
    # 2. Duplicate Check
    # -----------------------------
    duplicates = df.duplicated(subset=["city", "event_time"]).sum()
    report["duplicates"] = int(duplicates)

    # -----------------------------
    # 3. Range Validation
    # -----------------------------
    invalid_temp = df[
        (df["temperature"] < -50) | (df["temperature"] > 60)
    ].shape[0]

    invalid_wind = df[df["windspeed"] < 0].shape[0]

    report["invalid_temperature"] = int(invalid_temp)
    report["invalid_windspeed"] = int(invalid_wind)

    # -----------------------------
    # 4. Timestamp Validation
    # -----------------------------
    invalid_time = df["event_time"].isna().sum()
    report["invalid_event_time"] = int(invalid_time)

    # -----------------------------
    # 5. Basic Row Count
    # -----------------------------
    report["total_rows"] = len(df)

    # -----------------------------
    # PRINT REPORT
    # -----------------------------
    print("REPORT: DATA QUALITY REPORT")
    print("----------------------")

    for k, v in report.items():
        print(f"{k}: {v}")

    # -----------------------------
    # FAIL CONDITION (optional)
    # -----------------------------
    if (
        invalid_temp > 0
        or invalid_wind > 0
        or invalid_time > 0
    ):
        raise Exception("Failed: Data validation failed!")

    print("\nSUCCESSFUL:Data validation passed successfully!")

    return True