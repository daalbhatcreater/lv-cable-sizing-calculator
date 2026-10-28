# LV Cable Sizing & Voltage-Drop Calculator

Sizes low-voltage copper cables the way a design engineer does it by hand,
following the IEC 60364 approach:

1. design current `Ib` from the load (kW, pf, efficiency, 1 or 3 phase)
2. protective device `In >= Ib` from standard ratings
3. smallest cable with `Iz = It x Ca x Cg >= In` (IEC 60364-4-43, 433.1), using the
   tabulated capacities of IEC 60364-5-52 Annex B and its ambient and grouping
   correction factors
4. upsize until the running voltage drop is within the limit, and the motor
   starting drop if a DOL start is specified
5. upsize until the cable survives the fault: `S >= sqrt(I2t) / k`, with `I2t`
   either `Ik^2 x t` or the protective device's let-through energy

It reports which of these checks set the final size, so a long feeder shows up as
"voltage drop", a small circuit on a stiff bus as "short-circuit withstand", and so on.

The calculator was checked against 12 hand-calculated circuits covering every
branch of the logic: see [`validation/hand_calcs.md`](validation/hand_calcs.md).

## Usage

```bash
pip install -r requirements.txt
python -m cablesizer examples/feeders.csv -o results/cable_schedule.xlsx
python -m pytest
```

Output for the example plant schedule:

```
Circuit                     Ib     In          Cable      Iz    VD%  governed by
MCC-1 incomer            404.4    500    2 x 120 mm2   516.4   0.62  current rating
Chilled water pump 1      52.2     63         16 mm2    66.4   1.98  current rating
Chilled water pump 2      52.2     63         16 mm2    66.4   2.13  current rating
Cooling tower fan         27.3     32          6 mm2    34.3   4.19  current rating
Air compressor            93.6    100         35 mm2   105.0   1.33  current rating
Lighting DB-L1            18.5     20          4 mm2    22.6   2.32  current rating
Lighting final circuit     8.7     10        2.5 mm2    11.3   2.42  current rating
Small power DB-P1         40.9     50         16 mm2    53.6   0.93  current rating
Workshop socket ring      16.9     20         10 mm2    26.8   0.88  current rating
Welding outlet            39.7     40         10 mm2    49.8   1.40  current rating
```

The same results are written to `results/cable_schedule.xlsx` as a cable schedule.

From Python:

```python
from cablesizer import Circuit, size_circuit

r = size_circuit(Circuit("AHU-3", length_m=85, load_kw=18.5, pf=0.86,
                         efficiency=0.92, insulation="XLPE", method="E",
                         ambient_c=40, grouped=4, arrangement="tray"))
print(r.designation, r.governed_by, f"{r.vd_pct:.2f} %")
```

## Input columns

| Column | Meaning |
|---|---|
| `load_kw` or `ib_a` | load in kW, or the design current directly |
| `voltage_v`, `phases` | 415 V / 3 phase or 230 V / 1 phase |
| `pf`, `efficiency` | load power factor; motor efficiency (1.0 otherwise) |
| `insulation` | `PVC` (70 degC) or `XLPE` (90 degC) |
| `method` | installation method `C` (on a wall) or `E` (free air / perforated tray) |
| `ambient_c` | air temperature; the next higher tabulated value is used |
| `grouped`, `arrangement` | number of circuits and `bunched`, `wall` or `tray` |
| `runs` | parallel cables per phase |
| `device_a` | protective device rating; picked automatically if blank |
| `fault_ka`, `clearing_s` | prospective fault and clearing time, for `Ik^2 t` |
| `let_through_a2s` | device let-through I2t; use this for current-limiting breakers |
| `vd_limit_pct` | running voltage drop limit |
| `start_multiplier`, `start_pf`, `start_vd_limit_pct` | DOL starting check |

## Assumptions and limits

- Copper conductors, multicore cables, three loaded conductors (or two for single
  phase circuits, which is conservative with the three-conductor table).
- Only methods C and E are tabulated. Buried cables (method D) need soil thermal
  resistivity and depth factors which are not included.
- Voltage drop uses the conductor resistance at maximum operating temperature,
  which slightly overstates the drop on lightly loaded cables. Reactance is taken
  as 0.08 Ohm/km for all sizes.
- DC resistance is used up to 300 mm2; skin effect at 50 Hz adds about 1-3 % above
  185 mm2 and is ignored.
- The let-through values in the example schedule are typical figures for
  current-limiting MCCBs and energy class 3 MCBs; a real design should take them
  from the selected device's let-through curve.
- Overload coordination `I2 <= 1.45 Iz` is checked with `I2 = 1.3 In` (IEC 60947-2
  breakers). It is always met when `In <= Iz`, but it is flagged if a fuse or other
  device with a different conventional tripping current is modelled.

## Layout

```
cablesizer/tables.py     IEC 60364-5-52 capacities, correction factors, IEC 60228 resistances
cablesizer/sizing.py     the sizing sequence
cablesizer/__main__.py   CSV in, console table and Excel cable schedule out
validation/              12 hand-calculated cases and their inputs
tests/                   pytest checks against the hand calculations
```
