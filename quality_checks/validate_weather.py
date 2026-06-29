from duckdb import df
import pandas as pd

def validate_weather_data(df):
    print("\nSEARCH: Running Data Quality Checks...")

    report = {}

    # -----------------------------
    # TOTAL ROWS
    # -----------------------------
    report["total_rows"] = len(df)

    # -----------------------------
    # MISSING VALUES
    # -----------------------------
    report["missing_values"] = df.isnull().sum().to_dict()

    # -----------------------------
    # DUPLICATES
    # -----------------------------
    duplicate_count = df.duplicated(
        subset=["city", "event_time"]
    ).sum()

    report["duplicates"] = duplicate_count

    duplicate_pct = round(
        duplicate_count / len(df) * 100, 2
    )

    report["duplicate_percent"] = duplicate_pct

    if duplicate_pct > 5:
        print(
            "WARNING: High duplicate percentage detected."
        )

    # -----------------------------
    # INVALID CHECKS
    # -----------------------------
    report["invalid_temperature"] = df[
        (df["temperature"] < -50) | (df["temperature"] > 60)
    ].shape[0]

    report["invalid_windspeed"] = df[df["windspeed"] < 0].shape[0]

    report["invalid_event_time"] = df["event_time"].isna().sum()

    # -----------------------------
    # PRINT REPORT
    # -----------------------------
    print("\nREPORT: DATA QUALITY REPORT")
    print("----------------------")
    for k, v in report.items():
        print(f"{k}: {v}")

    # -----------------------------
    # CRITICAL CHECKS ONLY (DO NOT FILTER DATA)
    # -----------------------------
    if df["city"].isna().sum() > 0:
        raise Exception("CRITICAL ERROR: city has missing values")

    if df["event_time"].isna().sum() > 0:
        raise Exception("CRITICAL ERROR: event_time is invalid")

    print("\nSUCCESSFUL: Data validation passed successfully!")