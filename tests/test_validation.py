"""Calculator output against the hand calculations in validation/hand_calcs.md."""

from pathlib import Path

import pytest

from cablesizer import Circuit, size_circuit
from cablesizer.__main__ import read_circuits

CASES = Path(__file__).parent.parent / "validation" / "cases.csv"

# name prefix: (Ib, In, size, runs, VD %, governed by)
EXPECTED = {
    "C01": (41.74, 50, 6, 1, 2.74, "current rating"),
    "C02": (39.14, 40, 16, 1, 1.19, "current rating"),
    "C03": (14.49, 16, 4, 1, 2.21, "voltage drop"),
    "C04": (73.65, 80, 25, 1, 4.59, "voltage drop"),
    "C05": (23.19, 25, 10, 1, 0.49, "current rating"),
    "C06": (618.31, 630, 150, 2, 0.69, "current rating"),
    "C07": (7.73, 10, 35, 1, 0.03, "short-circuit withstand"),
    "C08": (64.36, 80, 25, 1, 2.70, "motor starting drop"),
    "C09": (115.93, 125, 70, 1, 0.83, "current rating"),
    "C10": (32.04, 40, 4, 1, 3.91, "current rating"),
    "C11": (150.0, 160, 70, 1, 1.58, "current rating"),
    "C12": (183.05, 200, 120, 1, 1.44, "current rating"),
}

circuits = read_circuits(CASES)


@pytest.mark.parametrize("circuit", circuits, ids=[c.name[:3] for c in circuits])
def test_against_hand_calc(circuit):
    ib, device, size, runs, vd, governed = EXPECTED[circuit.name[:3]]
    r = size_circuit(circuit)
    assert r.ib_a == pytest.approx(ib, abs=0.01)
    assert r.device_a == device
    assert r.size_mm2 == size
    assert r.runs == runs
    assert r.vd_pct == pytest.approx(vd, abs=0.01)
    assert r.governed_by == governed
    assert r.iz_a >= r.device_a


def test_all_twelve_cases_present():
    assert len(circuits) == 12


def test_upsizing_never_reduces_capacity():
    # a longer run can only make the cable bigger
    sizes = [size_circuit(Circuit("x", length_m=l, load_kw=45, pf=0.85)).size_mm2
             for l in (10, 50, 100, 200, 300)]
    assert sizes == sorted(sizes)


def test_device_below_design_current_rejected():
    with pytest.raises(ValueError):
        size_circuit(Circuit("x", length_m=10, ib_a=50, device_a=40))


def test_grouping_beyond_table_uses_last_entry():
    from cablesizer.sizing import grouping_factor
    assert grouping_factor("tray", 12) == 0.72
    assert grouping_factor("bunched", 10) == 0.45
