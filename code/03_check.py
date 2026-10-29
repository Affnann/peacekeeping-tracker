"""Step 3: check the panel and write data/check_report.md.

Checks
  1. Which months are missing from the UN files.
  2. No duplicate rows (month x country x mission x category).
  3. The two overlaps removed in step 2 really are overlaps (Nov-Dec 2009).
  4. Male + female = total wherever both are reported (2010 onward).
  5. Police numbers match the UN's separate police file exactly, row by row.
  6. The join between the two UN files (Dec 2009 -> Jan 2010) has no break.
  7. Large month-to-month changes are listed for review.
  8. Rows with no number, and countries the UN has listed under more than one name.
  9. If tables/monthly_totals.csv exists, the rebuilt panel must match it exactly.
     This lets anyone (including other projects that build on this one) confirm
     they have rebuilt the same data as this release.

Usage: python code/03_check.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
BUILD = ROOT / "data" / "build"
REPORT = ROOT / "data" / "check_report.md"
TOTALS = ROOT / "tables" / "monthly_totals.csv"

lines: list[str] = []
failures: list[str] = []


def say(text: str = "") -> None:
    lines.append(text)


def result(name: str, ok: bool, detail: str = "") -> None:
    say(f"- **{'PASS' if ok else 'FAIL'}** {name}{': ' + detail if detail else ''}")
    if not ok:
        failures.append(name)


def main() -> None:
    p = pd.read_csv(BUILD / "contributions_monthly.csv")
    say("# Check report")
    say()
    say(f"Panel: {len(p):,} rows, {p['month'].min()} to {p['month'].max()}, "
        f"{p['month'].nunique()} months, {p['iso3'].nunique()} contributing countries.")
    say()

    # 1. Missing months
    say("## 1. Months missing from the UN files")
    say()
    all_months = pd.period_range(p["month"].min(), p["month"].max(), freq="M").astype(str)
    missing = sorted(set(all_months) - set(p["month"]))
    if missing:
        say(f"{len(missing)} of {len(all_months)} months have no data in the UN files: {', '.join(missing)}. "
            "They are left empty, never filled in.")
    else:
        say(f"None: all {len(all_months)} months from {all_months[0]} to {all_months[-1]} are present. "
            "(The UN files do not always date a month on its last day, for example 30 October 2024, "
            "so months are matched by calendar month, not by exact date.)")
    say()

    # 2. Duplicates
    say("## 2. Duplicates")
    say()
    dups = p.duplicated(["month", "iso3", "mission", "category"]).sum()
    result("No duplicate month x country x mission x category rows", dups == 0, f"{dups} found")
    say()

    # 3. Overlaps in the pre-2010 file
    say("## 3. Overlapping columns in the pre-2010 file")
    say()
    pre = pd.read_csv(RAW / "DPPADPO-UCPre2010.csv")
    split = pre["Individual_Police"].notna() | pre["Formed_Police_Units"].notna()
    s = pre[split]
    same = (s["Civilian_Police"].fillna(0) == s["Individual_Police"].fillna(0) + s["Formed_Police_Units"].fillna(0)).all()
    result("Where police are split, Civilian_Police = Individual_Police + Formed_Police_Units",
           bool(same), f"{len(s)} rows, months {', '.join(sorted(pd.to_datetime(s['Date']).dt.to_period('M').astype(str).unique()))}")
    both = pre[pre["Experts_on_Mission"].notna() & pre["Observers"].notna()]
    result("Where both are given, Experts_on_Mission = Observers",
           bool((both["Experts_on_Mission"] == both["Observers"]).all()), f"{len(both)} rows")
    say()

    # 4. Male + female
    say("## 4. Male + female = total")
    say()
    post = p[p["source"] == "DPO-UCHISTORICAL"]
    b = post.dropna(subset=["male", "female"])
    result("Male + female = total (2010 onward)", bool((b["male"] + b["female"] == b["total"]).all()), f"{len(b):,} rows")
    say()

    # 5. Police cross-check
    say("## 5. Police: main file vs the UN's separate police file")
    say()
    pol = pd.read_csv(RAW / "DPO-UHISTORICALPOL.csv")
    pol["month"] = pd.to_datetime(pol["last_reporting_date"]).dt.to_period("M").astype(str)
    pol = pol[pol["month"] <= p["month"].max()]
    pol["total_pol"] = pol[["male_personnel", "female_personnel"]].sum(axis=1, min_count=1)
    pol["category"] = pol["personnel_type"].map({"Individual Police": "police_individual",
                                                 "Formed Police Units": "police_formed_units"})
    main_pol = post[post["category"].isin(["police_individual", "police_formed_units"])]
    m = main_pol.merge(pol.rename(columns={"isocode3": "iso3", "mission_acronym": "mission"})
                       [["month", "iso3", "mission", "category", "total_pol"]],
                       on=["month", "iso3", "mission", "category"], how="outer", indicator=True)
    unmatched = (m["_merge"] != "both").sum()
    differ = (m["_merge"] == "both") & (m["total"].fillna(-1) != m["total_pol"].fillna(-1))
    result("Every police row appears in both files", unmatched == 0, f"{unmatched} unmatched of {len(m):,}")
    result("Every police number is identical in both files", int(differ.sum()) == 0, f"{int(differ.sum())} differ")
    say()

    # 6. Join between the two files
    say("## 6. Join between the two UN files")
    say()
    tot = p.groupby("month")["total"].sum()
    d09, j10 = tot.get("2009-12"), tot.get("2010-01")
    change = (j10 - d09) / d09 * 100
    result("Total changes by less than 3% from December 2009 to January 2010", abs(change) < 3,
           f"{d09:,.0f} -> {j10:,.0f} ({change:+.1f}%)")
    say()

    # 7. Large changes
    say("## 7. Large month-to-month changes (more than 5% of the total), for review")
    say()
    say("Gaps from missing months are skipped. These are not errors by themselves; each one is listed so it can be")
    say("compared with known events (missions opening or closing).")
    say()
    ts = tot.reindex(all_months)
    pct = ts.pct_change(fill_method=None) * 100
    big = pct[pct.abs() > 5].dropna()
    say("| Month | Total | Change from previous month |")
    say("|---|---:|---:|")
    for mth, v in big.items():
        say(f"| {mth} | {ts[mth]:,.0f} | {v:+.1f}% |")
    say()

    # 8. Missing numbers and names
    say("## 8. Rows with no number, and country names")
    say()
    nan_rows = p[p["total"].isna()]
    say(f"{len(nan_rows)} rows list a country and mission but give no number (both male and female empty). "
        "They are kept and count as missing, not zero.")
    say()
    names = p.groupby("iso3")["country_as_published"].unique()
    multi = names[names.apply(len) > 1]
    say(f"{len(multi)} country codes appear under more than one name; the panel uses the most recent name for each:")
    say()
    for code, n in multi.items():
        say(f"- {code}: {' / '.join(sorted(map(str, n)))}")
    say()

    # 9. Match against the release
    say("## 9. Match against this release's published monthly totals")
    say()
    if TOTALS.exists():
        pub = pd.read_csv(TOTALS, dtype={"month": str}).set_index("month")
        rebuilt = p.pivot_table(index="month", columns="category", values="total", aggfunc="sum")
        rebuilt["total"] = rebuilt.sum(axis=1)
        rebuilt = rebuilt.reindex(columns=pub.columns)
        a = rebuilt.round(0).fillna(-1).astype(float)
        b = pub.reindex(rebuilt.index).round(0).fillna(-1).astype(float)
        n_diff = int((a != b).sum().sum()) + abs(len(pub) - len(rebuilt))
        result("Rebuilt panel matches tables/monthly_totals.csv for every month and category", n_diff == 0,
               f"{len(rebuilt)} months compared, {n_diff} differences")
    else:
        say("tables/monthly_totals.csv not found yet (it is written by step 4). Re-run this step after step 4.")
    say()

    say("## Result")
    say()
    say("All checks passed." if not failures else f"FAILED: {', '.join(failures)}")
    REPORT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[-1:]))
    print(f"Report written to {REPORT}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
