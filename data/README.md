# Data

## Sources

| Item | Details |
|---|---|
| Publisher | United Nations, Peace and Security Data Hub (https://psdata.un.org), with data from the UN Department of Peace Operations |
| Main file, 2010 onward | "Historical Uniformed Personnel Contribution", dataset `DPO-UCHISTORICAL`, monthly, by country, mission, personnel type and sex |
| Main file, 1990-2009 | "Historical Uniformed Personnel Contribution prior to 2010", dataset `DPPADPO-UCPre2010`, monthly, by country, mission and personnel type (archived by the UN) |
| Cross-check file | "Police Personnel in Missions", dataset `DPO-UHISTORICALPOL`, used only to check the police numbers |
| Download address | `https://api.psdata.un.org/public/data/<dataset>/csv` |
| Downloaded on | 29 October 2026 (the UN lists the main file as last updated 31 July 2026) |
| Months used | November 1990 to July 2026 |
| Terms | UN website terms of use: download for personal, non-commercial use; no redistribution. That is why the files are not in this repository. Run `code/01_download.py` to get your own copy. |

| Item | Details |
|---|---|
| Reimbursement rates | UN General Assembly resolutions 68/281 (30 June 2014), 72/285 (5 July 2018), 76/276 (29 June 2022) and 80/272 (30 June 2026), read from the UN Official Document System (https://documents.un.org) |
| Table | `reference/reimbursement_rates.csv`: the rate, the date it took effect, the resolution and the paragraph that sets it |
| Not included | The temporary US$4.90 per person per month for COVID-19 testing (resolution 76/276, para. 10), and one-off supplemental payments before 2014 |

| Item | Details |
|---|---|
| Map borders | Natural Earth, Admin 0 countries, 1:110m, release v5.1.2 |
| Where from | Natural Earth's own GitHub repository (https://github.com/nvkelso/natural-earth-vector, tag v5.1.2). The download link on naturalearthdata.com returned a server error on 29 October 2026; the files are the same |
| Terms | Public domain |

## Files

- `raw/` is created by `code/01_download.py`. It holds the UN files and the map borders, plus `download_log.json` with each file's address, size and SHA-256 fingerprint.
- `build/` is created by `code/02_build_panel.py`. It holds the full monthly dataset (see the main README).
- `reference/reimbursement_rates.csv` is in the repository.
- `check_report.md` is the output of `code/03_check.py`.

Fingerprints of the UN files used for this release (SHA-256):

| File | Bytes | SHA-256 |
|---|---:|---|
| DPO-UCHISTORICAL.csv | 13,282,978 | a3174ccab744a3b3e7c4c37880ee848c58123275071b2f5d1a670b6412754646 |
| DPPADPO-UCPre2010.csv | 32,661,718 | 3cc13cd1b1537258fa2c6c4f37782fe14e8e892428749aafadae06aea49399dc |
| DPO-UHISTORICALPOL.csv | 3,885,328 | 50c536102731f088fee1623b472920eea0f1ec04b433de3307e7e6c293da7b5c |

If the UN updates a file, your fingerprint will differ. That is expected: the build is fixed to end in July 2026, and the last check in `code/03_check.py` will tell you whether the months used here are unchanged.
