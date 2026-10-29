"""Step 5: draw the charts and the map in figures/.

Usage: python code/05_figures.py
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "data" / "build"
TABLES = ROOT / "tables"
FIG = ROOT / "figures"
NE = ROOT / "data" / "raw" / "natural_earth" / "ne_110m_admin_0_countries.shp"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3de"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
SOURCE = "Source: UN Peace and Security Data Hub (psdata.un.org). Chart: peacekeeping-tracker."

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "xtick.major.size": 0, "ytick.major.size": 0,
})


def finish(fig, name: str, title: str, subtitle: str, source: str = SOURCE) -> None:
    fig.suptitle(title, x=0.02, y=0.985, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.02, 0.925, subtitle, ha="left", fontsize=10, color=INK2)
    fig.text(0.02, 0.012, source, ha="left", fontsize=8, color=INK2)
    fig.savefig(FIG / name, dpi=160)
    plt.close(fig)


def thousands(ax):
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))


def fig_total(mt: pd.DataFrame) -> None:
    s = mt["total"]
    x = pd.PeriodIndex(s.index, freq="M").to_timestamp()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    fig.subplots_adjust(top=0.84, bottom=0.12, left=0.08, right=0.95)
    ax.axvspan(pd.Timestamp("2025-07-01"), x.max() + pd.Timedelta(days=20), color="#eef3fb", lw=0)
    ax.plot(x, s.values, color=BLUE, lw=2)
    ax.annotate(f"{s.iloc[-1]:,.0f}\n{s.index[-1]}", (x[-1], s.iloc[-1]), xytext=(6, -4),
                textcoords="offset points", fontsize=9, color=INK)
    peak = s.idxmax()
    ax.annotate(f"Peak {s.max():,.0f} ({peak})", (pd.Period(peak, "M").to_timestamp(), s.max()),
                xytext=(-10, 8), textcoords="offset points", ha="right", fontsize=9, color=INK)
    ax.text(pd.Timestamp("2025-08-01"), s.max() * 0.9, "2025-26\ncut", fontsize=9, color=INK2)
    ax.set_ylim(0, s.max() * 1.12)
    ax.set_xlim(pd.Timestamp("1990-06-01"), pd.Timestamp("2027-06-01"))
    thousands(ax)
    ax.set_ylabel("Uniformed personnel")
    finish(fig, "total_personnel.png", "UN uniformed personnel, all contributing countries",
           "Troops, staff officers, military experts and police in UN missions, monthly, Nov 1990 to Jul 2026")


def fig_bangladesh(cm: pd.DataFrame) -> None:
    b = cm[cm["iso3"] == "BGD"].set_index("month")
    x = pd.PeriodIndex(b.index, freq="M").to_timestamp()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.6), sharex=True)
    fig.subplots_adjust(top=0.86, bottom=0.09, left=0.08, right=0.95, hspace=0.32)
    a1.plot(x, b["total"], color=ORANGE, lw=2)
    a1.set_title("Bangladeshi personnel deployed", loc="left", fontsize=10, color=INK)
    thousands(a1)
    a2.plot(x, b["share_pct"], color=ORANGE, lw=2)
    a2.set_title("Bangladesh's share of all UN uniformed personnel (%)", loc="left", fontsize=10, color=INK)
    a2.yaxis.set_major_locator(plt.MultipleLocator(2))
    a2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    a2.set_xlim(pd.Timestamp("1990-06-01"), pd.Timestamp("2027-06-01"))
    for ax, col, fmt in ((a1, "total", "{:,.0f}"), (a2, "share_pct", "{:.1f}%")):
        ax.annotate(fmt.format(b[col].iloc[-1]), (x[-1], b[col].iloc[-1]), xytext=(6, -3),
                    textcoords="offset points", fontsize=9)
        ax.set_ylim(0, b[col].max() * 1.15)
    finish(fig, "bangladesh.png", "Bangladesh in UN peacekeeping, 1990-2026",
           f"Monthly; latest month {b.index[-1]}, when Bangladesh ranked no. {int(b['rank'].iloc[-1])} among contributors")


def fig_cut(cut: pd.DataFrame) -> None:
    allpct = cut.loc["ALL", "change_pct"]
    c = cut.drop(index="ALL").sort_values("change_pct", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 7.4))
    fig.subplots_adjust(top=0.87, bottom=0.08, left=0.27, right=0.93)
    colors = [ORANGE if i == "BGD" else BLUE for i in c.index]
    y = range(len(c))
    ax.barh(list(y), c["change_pct"], color=colors, height=0.68)
    ax.set_yticks(list(y))
    before_col = [k for k in c.columns if k.startswith("personnel_")][0]
    after_col = [k for k in c.columns if k.startswith("personnel_")][1]
    ax.set_yticklabels([f"{n}  ({int(b):,} → {int(a):,})" for n, b, a in
                        zip(c["country"].str.replace("United Republic of Tanzania", "Tanzania"), c[before_col], c[after_col])],
                       fontsize=9)
    for yi, v in zip(y, c["change_pct"]):
        ax.text(v - 1, yi, f"{v:.0f}%", va="center", ha="right", fontsize=8.5, color=INK,
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.6), zorder=4)
    ax.axvline(allpct, color=INK2, lw=1, ls=(0, (3, 3)))
    ax.text(allpct + 1, len(c) - 0.4, f"All countries {allpct:.0f}%", fontsize=9, color=INK2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlim(min(c["change_pct"].min() - 12, -100), 2)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Change in personnel, June 2025 to July 2026")
    finish(fig, "cut_2025.png", "The 2025-26 cut, by contributing country",
           "The 20 largest contributors of June 2025; personnel before → after in brackets. Bangladesh in orange.")


def fig_map(cm: pd.DataFrame) -> None:
    latest = cm["month"].max()
    d = cm[cm["month"] == latest].set_index("iso3")["total"]
    w = gpd.read_file(NE)
    code = w["ISO_A3"].where(w["ISO_A3"] != "-99", w["ADM0_A3"])
    w["personnel"] = code.map(d)
    w = w[w["CONTINENT"] != "Antarctica"].to_crs("+proj=robin")
    bins = [1, 50, 250, 1000, 2500, 10000]
    cmap = ListedColormap(["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
    norm = BoundaryNorm(bins, cmap.N)
    fig, ax = plt.subplots(figsize=(11, 6.2))
    fig.subplots_adjust(top=0.88, bottom=0.06, left=0.01, right=0.99)
    w[w["personnel"].isna()].plot(ax=ax, color="#ebeae6", edgecolor=SURFACE, linewidth=0.4)
    w[w["personnel"].notna()].plot(ax=ax, column="personnel", cmap=cmap, norm=norm, edgecolor=SURFACE, linewidth=0.4)
    bgd = w[code.loc[w.index] == "BGD"]
    bgd.boundary.plot(ax=ax, color=ORANGE, linewidth=1.6)
    ax.set_axis_off()
    labels = ["1-49", "50-249", "250-999", "1,000-2,499", "2,500 or more"]
    handles = [Patch(facecolor=cmap(i), label=l) for i, l in enumerate(labels)]
    handles.append(Patch(facecolor="#ebeae6", label="None"))
    handles.append(Patch(facecolor="none", edgecolor=ORANGE, linewidth=1.6, label="Bangladesh"))
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=9, title="Personnel", title_fontsize=9)
    unmapped = sorted(set(d.index) - set(code))
    note = f"  Not shown (too small for this map): {', '.join(unmapped)}." if unmapped else ""
    finish(fig, "map_latest.png", f"Who supplies UN uniformed personnel ({latest})",
           f"{len(d)} contributing countries, {d.sum():,.0f} personnel in total.{note}")


def fig_money(est: pd.DataFrame) -> None:
    e = est[est["months_in_data"] == 12]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.6), sharex=True)
    fig.subplots_adjust(top=0.85, bottom=0.12, left=0.09, right=0.97, hspace=0.32)
    x = range(len(e))
    a1.bar(x, e["all_estimated_usd_millions"], color=BLUE, width=0.66)
    a1.set_title("All contributing countries (US$ millions)", loc="left", fontsize=10)
    a2.bar(x, e["bangladesh_estimated_usd_millions"], color=ORANGE, width=0.66)
    a2.set_title("Bangladesh (US$ millions)", loc="left", fontsize=10)
    for ax, col in ((a1, "all_estimated_usd_millions"), (a2, "bangladesh_estimated_usd_millions")):
        ax.set_ylim(0, e[col].max() * 1.18)
        for xi, v in zip(x, e[col]):
            ax.text(xi, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=8, color=INK)
        ax.grid(axis="x", visible=False)
    a2.set_xticks(list(x))
    a2.set_xticklabels(e.index, fontsize=8.5)
    a2.set_xlabel("UN fiscal year (July to June)")
    finish(fig, "reimbursement_estimate.png", "Estimated reimbursement owed for contingent personnel",
           "Troops and formed police units × the UN's standard monthly rate. An estimate of money owed, not of cash paid.",
           "Sources: UN Peace and Security Data Hub (personnel); UN General Assembly resolutions 68/281, 72/285, 76/276 "
           "(rates). Chart: peacekeeping-tracker.")


def main() -> None:
    FIG.mkdir(exist_ok=True)
    p = pd.read_csv(BUILD / "contributions_monthly.csv")
    mt = pd.read_csv(TABLES / "monthly_totals.csv", dtype={"month": str}).set_index("month")
    cm = p.groupby(["month", "iso3", "country"], as_index=False)["total"].sum()
    cm["rank"] = cm.groupby("month")["total"].rank(ascending=False, method="min").astype(int)
    cm = cm.merge(mt["total"].rename("all"), left_on="month", right_index=True)
    cm["share_pct"] = cm["total"] / cm["all"] * 100
    fig_total(mt)
    fig_bangladesh(cm)
    fig_cut(pd.read_csv(TABLES / "cut_2025.csv").set_index("iso3"))
    fig_map(cm)
    fig_money(pd.read_csv(TABLES / "reimbursement_estimate.csv").set_index("fiscal_year"))
    print(f"Figures written to {FIG}")


if __name__ == "__main__":
    main()
