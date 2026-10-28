"""Cable sizing checks: current rating with derating, voltage drop and
short-circuit thermal withstand.

The order follows the usual design sequence:
  1. design current Ib from the load
  2. protective device rating In >= Ib
  3. smallest size with Iz = It * Ca * Cg >= In        (IEC 60364-4-43, 433.1)
  4. upsize until voltage drop is within the limit      (IEC 60364-5-52, Annex G),
     and the motor starting drop if a start multiplier is given
  5. upsize until S >= sqrt(I^2 t) / k                  (IEC 60364-4-43, 434.5.2),
     with I^2 t either Ik^2 * t or the device let-through energy
"""

import math
from dataclasses import dataclass, field

from . import tables as T


@dataclass
class Circuit:
    name: str
    length_m: float
    load_kw: float = None          # either load_kw or ib_a must be given
    ib_a: float = None
    voltage_v: float = 415.0       # line-line for 3 phase, line-neutral for 1 phase
    phases: int = 3
    pf: float = 0.85
    efficiency: float = 1.0        # motor efficiency, 1.0 for non-motor loads
    insulation: str = "XLPE"
    method: str = "E"
    ambient_c: float = 30.0
    grouped: int = 1
    arrangement: str = "tray"
    runs: int = 1                  # parallel cables per phase
    device_a: float = None         # protective device rating, picked if None
    fault_ka: float = 0.0          # prospective fault current at the cable origin
    clearing_s: float = 0.1        # device operating time for that fault
    let_through_a2s: float = 0.0   # device I2t let-through, used instead of Ik^2 t
    vd_limit_pct: float = 5.0
    start_multiplier: float = 0.0  # >0 to check motor starting voltage drop
    start_pf: float = 0.3
    start_vd_limit_pct: float = 15.0


@dataclass
class Result:
    name: str
    ib_a: float
    device_a: float
    size_mm2: float
    runs: int
    it_a: float
    iz_a: float
    ca: float
    cg: float
    vd_pct: float
    s_min_sc_mm2: float
    governed_by: str
    start_vd_pct: float = None
    notes: list = field(default_factory=list)

    @property
    def designation(self):
        prefix = f"{self.runs} x " if self.runs > 1 else ""
        return f"{prefix}{self.size_mm2:g} mm2"


def design_current(c: Circuit) -> float:
    if c.ib_a is not None:
        return c.ib_a
    if c.load_kw is None:
        raise ValueError(f"{c.name}: give load_kw or ib_a")
    p = c.load_kw * 1000 / c.efficiency
    if c.phases == 3:
        return p / (math.sqrt(3) * c.voltage_v * c.pf)
    return p / (c.voltage_v * c.pf)


def pick_device(ib: float) -> float:
    for r in T.DEVICE_RATINGS:
        if r >= ib:
            return r
    raise ValueError(f"design current {ib:.0f} A exceeds largest device rating")


def ambient_factor(insulation: str, ambient_c: float) -> float:
    table = T.AMBIENT_FACTOR[insulation]
    # use the next tabulated temperature at or above the actual one
    for temp in sorted(table):
        if temp >= ambient_c:
            return table[temp]
    raise ValueError(f"ambient {ambient_c} degC outside table")


def grouping_factor(arrangement: str, n: int) -> float:
    table = T.GROUPING_FACTOR[arrangement]
    for count in sorted(table):
        if count >= n:
            return table[count]
    # beyond the last entry the table gives no further reduction
    return table[max(table)]


def resistance_hot(index: int, insulation: str) -> float:
    """Conductor resistance (Ohm/km) at maximum operating temperature."""
    theta = T.THETA_MAX[insulation]
    return T.R20[index] * (1 + T.ALPHA_CU * (theta - 20))


def voltage_drop_pct(c: Circuit, index: int, current: float, pf: float) -> float:
    r = resistance_hot(index, c.insulation) / c.runs
    x = T.X_MULTICORE / c.runs
    sin_phi = math.sqrt(1 - pf ** 2)
    length_km = c.length_m / 1000
    factor = math.sqrt(3) if c.phases == 3 else 2
    dv = factor * current * length_km * (r * pf + x * sin_phi)
    return 100 * dv / c.voltage_v


def size_circuit(c: Circuit) -> Result:
    ib = design_current(c)
    device = c.device_a if c.device_a else pick_device(ib)
    if device < ib:
        raise ValueError(f"{c.name}: device {device} A is below Ib {ib:.1f} A")

    ca = ambient_factor(c.insulation, c.ambient_c)
    cg = grouping_factor(c.arrangement, c.grouped)
    capacities = T.AMPACITY[(c.insulation, c.method)]

    # 1. current rating, per run
    it_required = device / (c.runs * ca * cg)
    idx = next((i for i, it in enumerate(capacities) if it >= it_required), None)
    if idx is None:
        raise ValueError(f"{c.name}: needs more parallel runs "
                         f"(It required {it_required:.0f} A per run)")
    governed = "current rating"

    # 2. voltage drop at design current
    while voltage_drop_pct(c, idx, ib, c.pf) > c.vd_limit_pct:
        idx += 1
        governed = "voltage drop"
        if idx == len(T.SIZES):
            raise ValueError(f"{c.name}: voltage drop not met at 300 mm2")
    if c.start_multiplier > 0:
        i_start = c.start_multiplier * ib
        while voltage_drop_pct(c, idx, i_start, c.start_pf) > c.start_vd_limit_pct:
            idx += 1
            governed = "motor starting drop"
            if idx == len(T.SIZES):
                raise ValueError(f"{c.name}: starting drop not met at 300 mm2")

    # 3. short-circuit withstand of each run
    s_min = 0.0
    if c.let_through_a2s > 0 or c.fault_ka > 0:
        k = T.K_ADIABATIC[c.insulation]
        if c.let_through_a2s > 0:
            # current-limiting device clearing in under 0.1 s: use the maker's
            # let-through energy rather than Ik^2 t (IEC 60364-4-43, 434.5.2)
            s_min = math.sqrt(c.let_through_a2s) / c.runs / k
        else:
            # each parallel run must withstand its share of the fault
            s_min = c.fault_ka * 1000 / c.runs * math.sqrt(c.clearing_s) / k
        while T.SIZES[idx] < s_min:
            idx += 1
            governed = "short-circuit withstand"
            if idx == len(T.SIZES):
                raise ValueError(f"{c.name}: fault withstand not met at 300 mm2")

    it = capacities[idx]
    iz = it * ca * cg * c.runs
    res = Result(
        name=c.name, ib_a=ib, device_a=device, size_mm2=T.SIZES[idx],
        runs=c.runs, it_a=it, iz_a=iz, ca=ca, cg=cg,
        vd_pct=voltage_drop_pct(c, idx, ib, c.pf),
        s_min_sc_mm2=s_min, governed_by=governed,
    )

    # overload coordination I2 <= 1.45 Iz; I2 = 1.3 In for IEC 60947-2 breakers
    if 1.3 * device > 1.45 * iz:
        res.notes.append("I2 > 1.45 Iz")

    if c.start_multiplier > 0:
        res.start_vd_pct = voltage_drop_pct(c, idx, c.start_multiplier * ib, c.start_pf)
    return res
