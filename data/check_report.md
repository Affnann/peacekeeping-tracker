# Check report

Panel: 306,172 rows, 1990-11 to 2026-07, 429 months, 162 contributing countries.

## 1. Months missing from the UN files

None: all 429 months from 1990-11 to 2026-07 are present. (The UN files do not always date a month on its last day, for example 30 October 2024, so months are matched by calendar month, not by exact date.)

## 2. Duplicates

- **PASS** No duplicate month x country x mission x category rows: 0 found

## 3. Overlapping columns in the pre-2010 file

- **PASS** Where police are split, Civilian_Police = Individual_Police + Formed_Police_Units: 596 rows, months 2009-11, 2009-12
- **PASS** Where both are given, Experts_on_Mission = Observers: 699 rows

## 4. Male + female = total

- **PASS** Male + female = total (2010 onward): 182,206 rows

## 5. Police: main file vs the UN's separate police file

- **PASS** Every police row appears in both files: 0 unmatched of 51,972
- **PASS** Every police number is identical in both files: 0 differ

## 6. Join between the two UN files

- **PASS** Total changes by less than 3% from December 2009 to January 2010: 98,194 -> 99,943 (+1.8%)

## 7. Large month-to-month changes (more than 5% of the total), for review

Gaps from missing months are skipped. These are not errors by themselves; each one is listed so it can be
compared with known events (missions opening or closing).

| Month | Total | Change from previous month |
|---|---:|---:|
| 1991-03 | 9,781 | -5.3% |
| 1991-04 | 10,713 | +9.5% |
| 1992-02 | 12,418 | +7.0% |
| 1992-03 | 14,677 | +18.2% |
| 1992-04 | 24,998 | +70.3% |
| 1992-08 | 43,838 | +75.4% |
| 1992-11 | 50,991 | +15.3% |
| 1993-04 | 57,396 | +6.2% |
| 1993-05 | 74,654 | +30.1% |
| 1994-12 | 70,225 | -7.0% |
| 1995-01 | 64,318 | -8.4% |
| 1995-02 | 57,784 | -10.2% |
| 1995-03 | 61,761 | +6.9% |
| 1995-05 | 65,075 | +5.3% |
| 1995-09 | 62,498 | -9.3% |
| 1995-11 | 53,208 | -11.4% |
| 1995-12 | 31,101 | -41.5% |
| 1996-01 | 29,150 | -6.3% |
| 1996-02 | 26,379 | -9.5% |
| 1996-07 | 25,047 | -5.1% |
| 1997-07 | 20,538 | -8.5% |
| 1997-08 | 19,212 | -6.5% |
| 1997-11 | 16,842 | -8.1% |
| 1997-12 | 14,888 | -11.6% |
| 1998-01 | 13,201 | -11.3% |
| 1998-04 | 14,545 | +9.8% |
| 1999-03 | 12,397 | -9.6% |
| 1999-08 | 13,344 | +6.8% |
| 1999-09 | 14,247 | +6.8% |
| 1999-12 | 18,167 | +25.0% |
| 2000-02 | 26,740 | +43.5% |
| 2000-03 | 29,417 | +10.0% |
| 2000-04 | 31,438 | +6.9% |
| 2000-05 | 35,587 | +13.2% |
| 2001-03 | 41,654 | +6.5% |
| 2001-08 | 47,163 | +5.2% |
| 2002-12 | 39,652 | -5.4% |
| 2003-05 | 34,947 | -5.5% |
| 2003-10 | 42,597 | +11.3% |
| 2003-12 | 45,815 | +5.2% |
| 2004-01 | 48,590 | +6.1% |
| 2006-10 | 80,848 | +5.1% |
| 2008-01 | 90,883 | +7.8% |
| 2013-07 | 97,602 | +7.0% |
| 2014-09 | 104,184 | +6.4% |
| 2023-11 | 66,844 | -5.4% |
| 2025-11 | 54,275 | -8.6% |
| 2025-12 | 49,251 | -9.3% |

## 8. Rows with no number, and country names

12 rows list a country and mission but give no number (both male and female empty). They are kept and count as missing, not zero.

12 country codes appear under more than one name; the panel uses the most recent name for each:

- BOL: Bolivia / Bolivia (Plurinational State of)
- BRN: Brunei / Brunei Darussalam
- CIV: Cote d Ivoire / Côte d’Ivoire
- COD: DR Congo / Democratic Republic of the Congo
- CPV: Cabo Verde / Cape Verde
- CZE: Czech Republic / Czechia
- GBR: United Kingdom / United Kingdom of Great Britain and Northern Ireland
- IRN: Iran / Iran (Islamic Republic of)
- MDA: Moldova / Republic of Moldova
- MKD: Macedonia / North Macedonia
- TUR: Turkey / Türkiye
- TZA: Tanzania / United Republic of Tanzania

## 9. Match against this release's published monthly totals

- **PASS** Rebuilt panel matches tables/monthly_totals.csv for every month and category: 429 months compared, 0 differences

## Result

All checks passed.
