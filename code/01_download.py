"""Step 1: download the source files.

The UN files are downloaded into data/raw/ and are NOT stored in this
repository: the UN's terms of use allow personal, non-commercial use only and do
not allow the data to be redistributed. Running this script fetches your own copy
directly from the UN.

Natural Earth country borders (public domain) are fetched from Natural Earth's
own GitHub repository, pinned to release v5.1.2.

Usage: python code/01_download.py
"""

import hashlib
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

UN_API = "https://api.psdata.un.org/public/data/{id}/csv"

# UN Peace and Security Data Hub (psdata.un.org) dataset IDs
UN_DATASETS = {
    "DPO-UCHISTORICAL": "Historical Uniformed Personnel Contribution (monthly, 2010 onward)",
    "DPPADPO-UCPre2010": "Historical Uniformed Personnel Contribution prior to 2010 (monthly, 1990-2009)",
    "DPO-UHISTORICALPOL": "Police Personnel in Missions (monthly, 2010 onward; used only as a cross-check)",
}

NE_BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/110m_cultural/"
NE_FILES = [f"ne_110m_admin_0_countries.{ext}" for ext in ("shp", "shx", "dbf", "prj")]


def fetch(url: str, dest: Path) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "peacekeeping-tracker/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        body = r.read()
    dest.write_bytes(body)
    return {
        "file": dest.name,
        "url": url,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    log = {"downloaded_on": date.today().isoformat(), "files": []}
    for ds_id, label in UN_DATASETS.items():
        print(f"UN  {ds_id}: {label}")
        log["files"].append(fetch(UN_API.format(id=ds_id), RAW / f"{ds_id}.csv"))
    ne_dir = RAW / "natural_earth"
    ne_dir.mkdir(exist_ok=True)
    for name in NE_FILES:
        print(f"NE  {name}")
        log["files"].append(fetch(NE_BASE + name, ne_dir / name))
    (RAW / "download_log.json").write_text(json.dumps(log, indent=2))
    print(f"Done. Log written to {RAW / 'download_log.json'}")


if __name__ == "__main__":
    sys.exit(main())
