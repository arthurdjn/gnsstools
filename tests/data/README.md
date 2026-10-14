# Test data

Small excerpts of real files, so the tests run in well under a second and the repository stays light.
The files keep their original names; the RINEX 2 navigation and RINEX 3 observation files are derived from the others,
because no sample of those formats was available.

| File | Format | Content |
| --- | --- | --- |
| `BRDC00IGS_R_20182850000_01D_MN.rnx` | RINEX 3.03 navigation | IGS merged broadcast ephemerides of 2018-10-12 (day 285): header, every G01 record, and the first two records of G02, R01 and E01 (E01 has the same epoch twice, from its F/NAV and I/NAV messages). |
| `brdc2850.18n` | RINEX 2.11 navigation | The G01 and G02 records above, rewritten with the RINEX 2 layout (3-space indent, 2-digit PRN and year, `D` exponents). |
| `brdc2850.18g` | RINEX 2.11 navigation | The R01 records above, rewritten with the RINEX 2 layout. |
| `edf1285b.18o` | RINEX 2.11 observation | Hourly session `b` (01h) of 2018-10-12 recorded at ENSG: header and the first 3 epochs (15 s interval). |
| `ENSG00FRA_R_20182850100_01H_15S_MO.rnx` | RINEX 3.03 observation | The first two epochs of G02, G06 and E07 above, rewritten with the RINEX 3 layout, keeping C1, L1, D1 and S1 and leaving the loss of lock and signal strength flags blank. |
| `COM20225_15M.SP3` | SP3-c | CODE final orbits of GPS week 2022, day 5 (2018-10-12): header and the first 7 epochs (00:00 to 01:30, 15 min interval). |
| `com20225.eph` | SP3-d | CODE multi-GNSS (MGEX) final orbits of the same day: header, and the Galileo, BeiDou and QZSS records of 7 epochs (00:00 to 01:30, every 15 min out of 5), the GLONASS R15 records of these epochs, and the R15 record at 18:15, whose clock is absent (`999999.999999`). |
| `COM20225_PV.SP3` | SP3-c | G01 and G02 at 00:15 and 00:30 from `COM20225_15M.SP3`, with velocity records added: velocities and clock rates are the central differences of the positions and clocks 15 minutes apart. |
