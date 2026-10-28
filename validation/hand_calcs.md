# Hand calculations used to validate the calculator

The 12 circuits in `cases.csv` were worked by hand first, and
`tests/test_validation.py` checks the calculator against these numbers.

## Formulas

Design current

    3 phase:  Ib = P / (sqrt(3) * U * pf * eta)
    1 phase:  Ib = P / (U * pf * eta)

Current rating (IEC 60364-4-43, 433.1): pick In >= Ib from the standard
ratings, then the smallest size with

    It >= In / (runs * Ca * Cg)

Voltage drop, with the conductor resistance at maximum operating temperature
(70 degC PVC, 90 degC XLPE) and X = 0.08 Ohm/km

    R_theta = R20 * (1 + 0.00393 * (theta - 20))
    3 phase:  dU% = 100 * sqrt(3) * Ib * L * (R cos(phi) + X sin(phi)) / U
    1 phase:  dU% = 100 * 2 * Ib * L * (R cos(phi) + X sin(phi)) / U

Hot resistances used below (Ohm/km):

| Size (mm2) | R20 | R70 (PVC) | R90 (XLPE) |
|---|---|---|---|
| 1.5 | 12.1 | 14.48 | - |
| 2.5 | 7.41 | 8.87 | - |
| 4 | 4.61 | 5.52 | 5.88 |
| 6 | 3.08 | - | 3.927 |
| 10 | 1.83 | 2.190 | - |
| 16 | 1.15 | 1.376 | 1.466 |
| 25 | 0.727 | - | 0.927 |
| 70 | 0.268 | 0.321 | 0.342 |
| 120 | 0.153 | - | 0.195 |
| 150 | 0.124 | - | 0.158 |

Short-circuit withstand (adiabatic): S >= Ik * sqrt(t) / k, with k = 115 (PVC)
and 143 (XLPE).

## Cases

**C01 heater**: 30 kW, pf 1.0, 415 V, 40 m, XLPE method E, 30 degC, single circuit.
Ib = 30000 / (1.732 x 415 x 1.0) = 41.74 A, so In = 50 A. Ca = Cg = 1, It >= 50 A,
so 6 mm2 (It 54 A). dU = 1.732 x 41.74 x 0.040 x 3.927 / 415 = 2.74 %. **6 mm2**.

**C02 pump motor**: 22 kW, pf 0.85, eta 0.92, 60 m, PVC method C, 40 degC,
3 circuits on a wall. Ib = 22000 / 0.92 / (1.732 x 415 x 0.85) = 39.14 A, In = 40 A.
Ca = 0.87, Cg = 0.79, It >= 40 / (0.87 x 0.79) = 58.2 A. 10 mm2 gives 57 A (short),
so 16 mm2 (76 A). dU = 1.19 %. **16 mm2**, current rating governs.

**C03 lighting, single phase**: 3 kW, pf 0.9, 230 V, 35 m, PVC method C, limit 3 %.
Ib = 3000 / (230 x 0.9) = 14.49 A, In = 16 A, so 1.5 mm2 on current. Voltage drop:
1.5 mm2 5.76 %, 2.5 mm2 3.53 %, 4 mm2 2.21 %. **4 mm2**, voltage drop governs.

**C04 long feeder**: 45 kW, pf 0.85, 180 m, XLPE method E. Ib = 73.65 A, In = 80 A,
so 16 mm2 (100 A) on current. dU: 16 mm2 7.13 %, 25 mm2 4.59 %. **25 mm2**, voltage
drop governs.

**C05 bunched DB feeder**: 15 kW, pf 0.9, 25 m, PVC method C, 45 degC, 6 circuits
bunched. Ib = 23.19 A, In = 25 A. Ca = 0.79, Cg = 0.57, It >= 55.5 A, so 10 mm2
(57 A). Iz = 57 x 0.79 x 0.57 = 25.7 A. dU = 0.49 %. **10 mm2**.

**C06 parallel incomer**: 400 kW, pf 0.9, 30 m, 2 cables per phase, XLPE method E
on tray, 35 degC, limit 3 %. Ib = 618.3 A, In = 630 A. Ca = 0.96, Cg = 0.88 (two
cables side by side). Per run It >= 630 / (2 x 0.96 x 0.88) = 372.9 A: 120 mm2 is 346 A,
so 150 mm2 (399 A). dU with R and X halved = 0.69 %. **2 x 150 mm2**.

**C07 short-circuit governed**: 5 kW, pf 0.9, 15 m, PVC method C, 10 kA cleared in
0.1 s. Ib = 7.73 A, In = 10 A, so 1.5 mm2 on current. S >= 10000 x sqrt(0.1) / 115
= 27.5 mm2, so **35 mm2**. In practice a current-limiting breaker with a
let-through I2t figure from the maker would allow a much smaller cable; this case
checks the adiabatic branch of the code.

**C08 motor start**: 37 kW, pf 0.86, eta 0.93, 120 m, XLPE method E, DOL start at
6 x Ib with starting pf 0.3, starting limit 8 %. Ib = 64.36 A, In = 80 A, 16 mm2 on
current. Running dU 4.20 % (fine) but starting dU 9.98 %. 25 mm2: running 2.70 %,
starting 6.85 %. **25 mm2**, starting drop governs.

**C09 hot plant room**: 75 kW, pf 0.9, 50 m, XLPE method C, 50 degC, 5 circuits
on a wall. Ib = 115.93 A, In = 125 A. Ca = 0.82, Cg = 0.73, It >= 208.8 A: 50 mm2 is
180 A, so 70 mm2 (232 A). dU = 0.83 %. **70 mm2**.

**C10 EV charger, single phase**: 7 kW, pf 0.95, 230 V, 25 m, XLPE method E, 35 degC.
Ib = 32.04 A, which is just over 32 A, so In = 40 A. Ca = 0.96, It >= 41.7 A, so
4 mm2 (42 A). dU = 3.91 %. **4 mm2**.

**C11 given current and device**: Ib = 150 A, In = 160 A, pf 0.85, 80 m, PVC method E,
3 circuits on tray, limit 4 %. Cg = 0.82, It >= 195.1 A, so 70 mm2 (196 A).
dU = 1.58 %. **70 mm2**.

**C12 compressor**: 110 kW, pf 0.88, eta 0.95, 90 m, XLPE method E, 45 degC,
4 circuits on tray, 25 kA cleared in 0.2 s. Ib = 183.05 A, In = 200 A. Ca = 0.87,
Cg = 0.77, It >= 298.6 A: 95 mm2 is 298 A (just short), so 120 mm2 (346 A).
S >= 25000 x sqrt(0.2) / 143 = 78.2 mm2, already met. dU = 1.44 %. **120 mm2**.

## Summary

| Case | Ib (A) | In (A) | Size | VD (%) | Governed by |
|---|---|---|---|---|---|
| C01 | 41.74 | 50 | 6 | 2.74 | current |
| C02 | 39.14 | 40 | 16 | 1.19 | current |
| C03 | 14.49 | 16 | 4 | 2.21 | voltage drop |
| C04 | 73.65 | 80 | 25 | 4.59 | voltage drop |
| C05 | 23.19 | 25 | 10 | 0.49 | current |
| C06 | 618.3 | 630 | 2 x 150 | 0.69 | current |
| C07 | 7.73 | 10 | 35 | 0.03 | short circuit |
| C08 | 64.36 | 80 | 25 | 2.70 | motor starting |
| C09 | 115.93 | 125 | 70 | 0.83 | current |
| C10 | 32.04 | 40 | 4 | 3.91 | current |
| C11 | 150.0 | 160 | 70 | 1.58 | current |
| C12 | 183.05 | 200 | 120 | 1.44 | current |
