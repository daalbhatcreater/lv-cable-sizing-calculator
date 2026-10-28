"""Reference data for LV copper cable sizing.

Current-carrying capacities are for multicore copper cables, three loaded
conductors, taken from IEC 60364-5-52 Annex B:
  - Method C (clipped direct / on a wall): Tables B.52.4 (PVC) and B.52.5 (XLPE)
  - Method E (multicore in free air / perforated tray): Tables B.52.10 (PVC)
    and B.52.12 (XLPE)
Reference ambient is 30 degC in air.

Conductor resistances are IEC 60228 class 2 maximum DC values at 20 degC.
"""

SIZES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]

# Tabulated current It (A), indexed in the same order as SIZES
AMPACITY = {
    ("PVC", "C"): [17.5, 24, 32, 41, 57, 76, 96, 119, 144, 184, 223, 259, 299, 341, 403, 464],
    ("PVC", "E"): [18.5, 25, 34, 43, 60, 80, 101, 126, 153, 196, 238, 276, 319, 364, 430, 497],
    ("XLPE", "C"): [22, 30, 40, 51, 70, 94, 119, 148, 180, 232, 282, 328, 379, 434, 514, 593],
    ("XLPE", "E"): [23, 32, 42, 54, 75, 100, 127, 158, 192, 246, 298, 346, 399, 456, 538, 621],
}

# Ohm/km at 20 degC
R20 = [12.1, 7.41, 4.61, 3.08, 1.83, 1.15, 0.727, 0.524, 0.387, 0.268,
       0.193, 0.153, 0.124, 0.0991, 0.0754, 0.0601]

# Typical reactance of a multicore LV cable, Ohm/km at 50 Hz
X_MULTICORE = 0.08

ALPHA_CU = 0.00393  # 1/K

# Maximum continuous conductor temperature (degC)
THETA_MAX = {"PVC": 70, "XLPE": 90}

# k for the adiabatic equation S = sqrt(I^2 t) / k  (IEC 60364-4-43, Table 43A)
K_ADIABATIC = {"PVC": 115, "XLPE": 143}

# Ambient air temperature correction, Table B.52.14
AMBIENT_FACTOR = {
    "PVC": {10: 1.22, 15: 1.17, 20: 1.12, 25: 1.06, 30: 1.00, 35: 0.94,
            40: 0.87, 45: 0.79, 50: 0.71, 55: 0.61, 60: 0.50},
    "XLPE": {10: 1.15, 15: 1.12, 20: 1.08, 25: 1.04, 30: 1.00, 35: 0.96,
             40: 0.91, 45: 0.87, 50: 0.82, 55: 0.76, 60: 0.71},
}

# Grouping factors, Table B.52.17 (number of circuits -> factor)
GROUPING_FACTOR = {
    # item 1: bunched in air, on a surface, embedded or enclosed
    "bunched": {1: 1.00, 2: 0.80, 3: 0.70, 4: 0.65, 5: 0.60, 6: 0.57,
                7: 0.54, 8: 0.52, 9: 0.50, 12: 0.45, 16: 0.41, 20: 0.38},
    # item 2: single layer on wall, floor or unperforated tray, touching
    "wall": {1: 1.00, 2: 0.85, 3: 0.79, 4: 0.75, 5: 0.73, 6: 0.72,
             7: 0.72, 8: 0.71, 9: 0.70},
    # item 4: single layer on a perforated horizontal tray, touching
    "tray": {1: 1.00, 2: 0.88, 3: 0.82, 4: 0.77, 5: 0.75, 6: 0.73,
             7: 0.73, 8: 0.72, 9: 0.72},
}

# Preferred protective device ratings (A)
DEVICE_RATINGS = [6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160,
                  200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600]
