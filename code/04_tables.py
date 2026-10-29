"""Step 4: write the headline tables in tables/.

These are short summary tables made from the panel. The full panel itself stays
on your computer (see the README for why).

  monthly_totals.csv          all contributing countries combined, by month and category
  bangladesh_by_year.csv      Bangladesh: average personnel, share of the total, rank
  top_contributors_latest.csv the 20 largest contributors in the latest month
  cut_2025.csv                the 2025-26 reduction for the 20 largest contributors of June 2025
  reimbursement_estimate.csv  estimated reimbursement owed at the UN's standard rate,
                              by UN fiscal year (July-June), all countries and Bangladesh

Usage: python code/04_tables.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "data" / "build"
REF = ROOT / "data" / "reference"
TABLES = ROOT / "tables"

CATEGORIES = ["troops", "staff_officers", "experts_on_mission", "police_individual",
              "police_formed_units", "police_unsplit"]
BEFORE_CUT = "2025-06"   # last month before the 2025-26 reduction began
CONTINGENT = ["troops", "police_formed_units"]  # personnel the UN reimburses countries for


def main() -> None:
    TABLES.mkdir(exist_ok=True)
    p = pd.read_csv(BUILD / "contributions_monthly.csv")
    latest = p["month"].max()

    # Monthly totals
    mt = p.pivot_table(index="month", columns="category", values="total", aggfunc="sum").reindex(columns=CATEGORIES)
    mt["total"] = mt.sum(axis=1)
    mt.round(0).astype("Int64").to_csv(TABLES / "monthly_totals.csv")

    # Country by month totals (used below; not written out)
    cm = p.groupby(["month", "iso3", "country"], as_index=False)["total"].sum()
    cm["rank"] = cm.groupby("month")["total"].rank(ascending=False, method="min").astype(int)
    cm = cm.merge(mt["total"].rename("all_countries"), left_on="month", right_index=True)
    cm["share_pct"] = cm["total"] / cm["all_countries"] * 100

    # Bangladesh by year
    bgd = cm[cm["iso3"] == "BGD"].copy()
    bgd["year"] = bgd["month"].str[:4].astype(int)
    by = bgd.groupby("year").agg(
        months_reported=("month", "nunique"),
        avg_personnel=("total", "mean"),
        avg_share_of_total_pct=("share_pct", "mean"),
        best_rank=("rank", "min"),
        worst_rank=("rank", "max"),
    )
    by["avg_personnel"] = by["avg_personnel"].round(0).astype(int)
    by["avg_share_of_total_pct"] = by["avg_share_of_total_pct"].round(2)
    by.to_csv(TABLES / "bangladesh_by_year.csv")

    # Top contributors, latest month
    top = cm[cm["month"] == latest].sort_values("total", ascending=False).head(20)
    top = top.assign(total=top["total"].round(0).astype(int))
    top[["month", "rank", "iso3", "country", "total", "share_pct"]].round({"share_pct": 2}).rename(
        columns={"total": "personnel"}).to_csv(TABLES / "top_contributors_latest.csv", index=False)

    # The 2025-26 reduction
    before = cm[cm["month"] == BEFORE_CUT].set_index("iso3")
    after = cm[cm["month"] == latest].set_index("iso3")
    top_before = before.sort_values("total", ascending=False).head(20).index
    cut = pd.DataFrame({
        "country": before.loc[top_before, "country"],
        f"personnel_{BEFORE_CUT}": before.loc[top_before, "total"],
        f"personnel_{latest}": after["total"].reindex(top_before).fillna(0),
    })
    cut["change"] = cut[f"personnel_{latest}"] - cut[f"personnel_{BEFORE_CUT}"]
    cut["change_pct"] = (cut["change"] / cut[f"personnel_{BEFORE_CUT}"] * 100).round(1)
    allrow = pd.DataFrame({
        "country": ["All contributing countries"],
        f"personnel_{BEFORE_CUT}": [mt.loc[BEFORE_CUT, "total"]],
        f"personnel_{latest}": [mt.loc[latest, "total"]],
    }, index=["ALL"])
    allrow["change"] = allrow[f"personnel_{latest}"] - allrow[f"personnel_{BEFORE_CUT}"]
    allrow["change_pct"] = (allrow["change"] / allrow[f"personnel_{BEFORE_CUT}"] * 100).round(1)
    cut = pd.concat([cut, allrow])
    cut.index.name = "iso3"
    for c in [f"personnel_{BEFORE_CUT}", f"personnel_{latest}", "change"]:
        cut[c] = cut[c].round(0).astype(int)
    cut.to_csv(TABLES / "cut_2025.csv")

    # Reimbursement estimate
    rates = pd.read_csv(REF / "reimbursement_rates.csv", parse_dates=["effective_from"])
    cont = p[p["category"].isin(CONTINGENT)].groupby(["month", "iso3"], as_index=False)["total"].sum()
    cont["date"] = pd.to_datetime(cont["month"])
    cont = cont[cont["date"] >= rates["effective_from"].min()]
    cont = pd.merge_asof(cont.sort_values("date"), rates.sort_values("effective_from"),
                         left_on="date", right_on="effective_from")
    cont["usd"] = cont["total"] * cont["usd_per_person_per_month"]
    start = cont["date"].dt.year - (cont["date"].dt.month < 7)
    cont["fiscal_year"] = start.astype(str) + "-" + (start + 1).astype(str).str[2:]

    def summarise(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
        g = df.groupby("fiscal_year").agg(months=("month", "nunique"), personnel_months=("total", "sum"),
                                          usd=("usd", "sum"))
        g["avg_contingent_personnel"] = (g["personnel_months"] / g["months"]).round(0).astype(int)
        g["estimated_usd_millions"] = (g["usd"] / 1e6).round(1)
        return g[["months", "avg_contingent_personnel", "estimated_usd_millions"]].add_prefix(prefix)

    allc = summarise(cont, "all_")
    bg = summarise(cont[cont["iso3"] == "BGD"], "bangladesh_")
    rate_by_fy = cont.groupby("fiscal_year")["usd_per_person_per_month"].agg(lambda s: "/".join(
        f"{v:,.2f}" for v in sorted(s.unique())))
    est = allc.join(bg.drop(columns="bangladesh_months")).rename(columns={"all_months": "months_in_data"})
    est.insert(1, "rate_usd_per_person_per_month", rate_by_fy)
    est["bangladesh_share_pct"] = (est["bangladesh_estimated_usd_millions"] / est["all_estimated_usd_millions"] * 100).round(1)
    est.to_csv(TABLES / "reimbursement_estimate.csv")

    print(f"Tables written to {TABLES}")


if __name__ == "__main__":
    main()
