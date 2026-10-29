# Cross-check against the UN peacekeeping website

Each monthly "Uniformed Personnel Contributing Countries by Ranking" PDF from peacekeeping.un.org is
compared, country by country, with the panel built from the UN Peace and Security Data Hub files.

| Month (PDF) | Countries in PDF | Rows add up | PDF grand total | Panel total | Countries matched | Countries that differ |
|---|---:|---|---:|---:|---:|---:|
| 2025-06 (02_country_ranking_87_june_2025.pdf) | 118 | yes | 61,299 | 61,299 | 117 | 0 |
| 2025-10 (02_country_ranking_91_october_2025.pdf) | 118 | yes | 59,372 | 59,372 | 117 | 0 |
| 2026-01 (02_country_ranking_94_january_2026.pdf) | 120 | yes | 47,022 | 47,022 | 118 | 0 |
| 2026-02 (02_country_ranking_95_february_2026.pdf) | 120 | yes | 47,298 | 47,298 | 117 | 0 |

Countries are matched by the data hub's country code. The website spells five countries differently
(United Kingdom, Côte d'Ivoire, Turkiye, Bolivia, Czech Republic); these are matched by a short list in the script.
A country the PDF lists with 0 personnel and the panel does not list is not counted as a difference.

## Result

All months match exactly.
