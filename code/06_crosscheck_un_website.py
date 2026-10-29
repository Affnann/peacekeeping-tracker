"""Step 6 (optional): cross-check against the UN peacekeeping website's own reports.

The UN peacekeeping website (peacekeeping.un.org) publishes a monthly PDF,
"Uniformed Personnel Contributing Countries by Ranking", with every contributing
country's male, female and total personnel. This step compares those PDFs,
country by country, with the panel built in step 2.

The website refuses automated downloads, so the PDFs are downloaded by hand
from https://peacekeeping.un.org/en/troop-and-police-contributors and saved,
with their original file names, in data/raw/peacekeeping_un_org/. Like the other
UN files, they are not stored in this repository.

PDFs used for this release (SHA-256):
  02_country_ranking_87_june_2025.pdf      77eab5927702ff0188c8c821235604e1c6fbc1907fba5545ec638547ce841848
  02_country_ranking_91_october_2025.pdf   0a692982f8810eb1c868dcaaf5cdef55030cc0ccb450e98d8f863e69ee125b80
  02_country_ranking_94_january_2026.pdf   8346a5e82bc1d3ef22516504d7db08dc3124838e5105c424be2b4282c8e41bc9
  02_country_ranking_95_february_2026.pdf  f5896fe44e71a204fa4e37f05de482c898e158d523e3dc4d7e6c0146d0cc9e3a

Output: data/crosscheck_un_website.md

Needs Poppler's pdftotext.

Usage: python code/06_crosscheck_un_website.py
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "raw" / "peacekeeping_un_org"
BUILD = ROOT / "data" / "build"
REPORT = ROOT / "data" / "crosscheck_un_website.md"

ROW = re.compile(r"^\s*(\d+)\s+(\d+)\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d{1,2}/\d{1,2}/\d{4})\s*$")
GRAND = re.compile(r"Grand Total\s+(\d+)\s+(\d+)\s+(\d+)")
# The website spells five countries differently from the data hub. Only these are matched by hand.
WEBSITE_NAMES = {
    "United Kingdom": "GBR",
    "C\u00f4te d'Ivoire": "CIV",
    "Turkiye": "TUR",
    "Bolivia": "BOL",
    "Czech Republic": "CZE",
}
AS_OF = re.compile(r"As of:\s*(\d{1,2}/\d{1,2}/\d{4})")


def read_pdf(path: Path) -> tuple[str, pd.DataFrame, tuple[int, int, int]]:
    text = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout
    month = datetime.strptime(AS_OF.search(text).group(1), "%d/%m/%Y").strftime("%Y-%m")
    rows = [m.groups() for m in map(ROW.match, text.splitlines()) if m]
    df = pd.DataFrame(rows, columns=["line", "rank", "country", "male", "female", "total", "date"])
    for c in ["line", "rank", "male", "female", "total"]:
        df[c] = df[c].astype(int)
    g = tuple(int(x) for x in GRAND.search(text).groups())
    return month, df, g


def main() -> None:
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {PDF_DIR}. See the instructions at the top of this script.")
    panel = pd.read_csv(BUILD / "contributions_monthly.csv")
    lines = ["# Cross-check against the UN peacekeeping website", "",
             "Each monthly \"Uniformed Personnel Contributing Countries by Ranking\" PDF from peacekeeping.un.org is",
             "compared, country by country, with the panel built from the UN Peace and Security Data Hub files.", "",
             "| Month (PDF) | Countries in PDF | Rows add up | PDF grand total | Panel total | Countries matched | Countries that differ |",
             "|---|---:|---|---:|---:|---:|---:|"]
    details, failures = [], 0
    for pdf in pdfs:
        month, df, (gm, gf, gt) = read_pdf(pdf)
        p = panel[panel["month"] == month]
        bycode = p.groupby(["iso3", "country"])["total"].sum().reset_index()
        name_to_code = dict(zip(p["country_as_published"], p["iso3"])) | WEBSITE_NAMES
        df["iso3"] = df["country"].map(name_to_code)
        adds_up = bool((df["male"] + df["female"] == df["total"]).all()) and df["total"].sum() == gt \
            and df["male"].sum() == gm and df["female"].sum() == gf
        df["panel"] = df["iso3"].map(bycode.set_index("iso3")["total"])
        unmatched_names = df[df["panel"].isna() & (df["total"] > 0)]["country"].tolist()
        differ = df[df["panel"].notna() & (df["panel"] != df["total"])]
        # countries in the panel but not in the PDF
        pdf_codes = set(df["iso3"].dropna())
        missing_in_pdf = bycode[~bycode["iso3"].isin(pdf_codes) & (bycode["total"] > 0)]
        matched = int((df["panel"] == df["total"]).sum())
        bad = len(differ) + len(unmatched_names) + len(missing_in_pdf)
        failures += bad + (0 if adds_up else 1) + (0 if p["total"].sum() == gt else 1)
        lines.append(f"| {month} ({pdf.name}) | {len(df)} | {'yes' if adds_up else 'NO'} | {gt:,} | "
                     f"{p['total'].sum():,.0f} | {matched} | {bad} |")
        for _, r in differ.iterrows():
            details.append(f"- {month}, {r['country']}: website {r['total']:,}, panel {r['panel']:,.0f}")
        for n in unmatched_names:
            details.append(f"- {month}, {n}: in the website PDF but not found by name in the panel")
        for _, r in missing_in_pdf.iterrows():
            details.append(f"- {month}, {r['country']}: in the panel ({r['total']:,.0f}) but not in the website PDF")
    lines.append("")
    lines.append("Countries are matched by the data hub's country code. The website spells five countries differently")
    lines.append("(United Kingdom, Côte d'Ivoire, Turkiye, Bolivia, Czech Republic); these are matched by a short list in the script.")
    lines.append("A country the PDF lists with 0 personnel and the panel does not list is not counted as a difference.")
    lines.append("")
    if details:
        lines += ["## Differences", ""] + details + [""]
    lines += ["## Result", "", "All months match exactly." if failures == 0 else f"{failures} differences found (listed above)."]
    REPORT.write_text("\n".join(lines) + "\n")
    print(lines[-1])
    print(f"Report written to {REPORT}")


if __name__ == "__main__":
    main()
