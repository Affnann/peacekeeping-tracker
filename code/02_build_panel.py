"""Step 2: combine the two UN files into one monthly panel.

Output (kept on your computer, not in the repository):
    data/build/contributions_monthly.csv
    one row per month x contributing country x mission x personnel category

Harmonised personnel categories
    troops                 "Troops"
    staff_officers         "Staff Officer" (reported separately only from May 2017;
                           before that, staff officers are inside "Troops")
    experts_on_mission     "Experts on Mission", and "Observers" before 2010
                           (military observers)
    police_individual      "Individual Police"
    police_formed_units    "Formed Police Units"
    police_unsplit         "Civilian_Police" before November 2009, when police were
                           not split into individual officers and formed units

Two overlaps in the pre-2010 file are removed (see code/03_check.py, which
verifies both):
  * In November and December 2009 the file has both the new police split and
    the old "Civilian_Police" column, which is their sum. Only the split is kept.
  * In those same months "Experts_on_Mission" repeats "Observers". Only one is kept.

Numbers are never filled in, estimated or corrected. Months the UN files do not
contain stay missing.

Usage: python code/02_build_panel.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
BUILD = ROOT / "data" / "build"

# The panel is fixed to end here, so every run gives the same data even after the
# UN adds new months. Change this (and the version number) to extend the series.
END_MONTH = "2026-07"

POST_MAP = {
    "Troops": "troops",
    "Staff Officer": "staff_officers",
    "Experts on Mission": "experts_on_mission",
    "Individual Police": "police_individual",
    "Formed Police Units": "police_formed_units",
}


def build_post2010() -> pd.DataFrame:
    df = pd.read_csv(RAW / "DPO-UCHISTORICAL.csv")
    out = pd.DataFrame(
        {
            "month": pd.to_datetime(df["last_reporting_date"]).dt.to_period("M").astype(str),
            "country": df["contributing_country"],
            "iso3": df["isocode3"],
            "mission": df["mission_acronym"],
            "category": df["personnel_type"].map(POST_MAP),
            "category_as_published": df["personnel_type"],
            "male": df["male_personnel"],
            "female": df["female_personnel"],
        }
    )
    if out["category"].isna().any():
        raise ValueError(f"Unknown personnel types: {df.loc[out['category'].isna(), 'personnel_type'].unique()}")
    # A row counts as reported if either sex is reported.
    out["total"] = out[["male", "female"]].sum(axis=1, min_count=1)
    out["source"] = "DPO-UCHISTORICAL"
    return out


def build_pre2010() -> pd.DataFrame:
    df = pd.read_csv(RAW / "DPPADPO-UCPre2010.csv")
    base = pd.DataFrame(
        {
            "month": pd.to_datetime(df["Date"]).dt.to_period("M").astype(str),
            "country": df["Contributor"],
            "iso3": df["Contributor_ISO-3"],
            "mission": df["Mission"],
        }
    )
    split = df["Individual_Police"].notna() | df["Formed_Police_Units"].notna()
    experts = df["Experts_on_Mission"].where(df["Experts_on_Mission"].notna(), df["Observers"])
    experts_src = pd.Series("Observers", index=df.index).where(df["Experts_on_Mission"].isna(), "Experts_on_Mission")

    parts = [
        ("troops", df["Troops"], pd.Series("Troops", index=df.index)),
        ("experts_on_mission", experts, experts_src),
        ("police_individual", df["Individual_Police"].where(split), pd.Series("Individual_Police", index=df.index)),
        ("police_formed_units", df["Formed_Police_Units"].where(split), pd.Series("Formed_Police_Units", index=df.index)),
        ("police_unsplit", df["Civilian_Police"].where(~split), pd.Series("Civilian_Police", index=df.index)),
    ]
    frames = []
    for cat, values, published in parts:
        f = base.copy()
        f["category"] = cat
        f["category_as_published"] = published
        f["male"] = pd.NA
        f["female"] = pd.NA
        f["total"] = values
        frames.append(f[values.notna()])
    out = pd.concat(frames, ignore_index=True)
    out["source"] = "DPPADPO-UCPre2010"
    return out


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    panel = pd.concat([build_pre2010(), build_post2010()], ignore_index=True)
    panel = panel[panel["month"] <= END_MONTH]
    # One consistent name per country code (the most recent name used by the UN).
    latest_name = panel.sort_values("month").groupby("iso3")["country"].last()
    panel["country_as_published"] = panel["country"]
    panel["country"] = panel["iso3"].map(latest_name)
    cols = ["month", "iso3", "country", "country_as_published", "mission", "category",
            "category_as_published", "male", "female", "total", "source"]
    panel = panel[cols].sort_values(["month", "iso3", "mission", "category"]).reset_index(drop=True)
    panel.to_csv(BUILD / "contributions_monthly.csv", index=False)
    print(f"{len(panel):,} rows, {panel['month'].min()} to {panel['month'].max()}, "
          f"{panel['month'].nunique()} months, {panel['iso3'].nunique()} countries")


if __name__ == "__main__":
    main()
