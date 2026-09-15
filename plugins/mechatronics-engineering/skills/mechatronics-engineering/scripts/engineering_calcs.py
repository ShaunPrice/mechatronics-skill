#!/usr/bin/env python3
"""Transparent educational sizing helpers; SI inputs, no hardware or network I/O."""
import argparse
import json
import math

G = 9.80665


def finite(name, value, minimum=None, positive=False):
    value = float(value)
    if not math.isfinite(value) or (minimum is not None and value < minimum) or (positive and value <= 0):
        raise ValueError(f"{name} is outside its finite allowed range")
    return value


def efficiency(name, value):
    value = finite(name, value, positive=True)
    if value > 1:
        raise ValueError(f"{name} must be in (0, 1]")
    return value


def screw_torque(force_n, lead_m_per_rev, eff):
    """Steady lifting torque; excludes screw inertia, bearing torque and acceleration."""
    return finite("force", force_n, minimum=0) * finite("lead", lead_m_per_rev, positive=True) / (2 * math.pi * efficiency("efficiency", eff))


def battery_runtime(voltage_v, capacity_ah, usable_fraction, eff, load_w):
    """Constant-load nominal energy estimate; excludes sag/temperature/age dynamics."""
    energy = finite("voltage", voltage_v, positive=True) * finite("capacity", capacity_ah, positive=True)
    return energy * efficiency("usable fraction", usable_fraction) * efficiency("efficiency", eff) / finite("load", load_w, positive=True)


def rover_sizing(mass_kg, radius_m, acceleration_m_s2, grade_deg, rolling_coefficient, drive_efficiency, driven_wheels, traction_coefficient):
    """Uphill, all weight on equally loaded driven wheels; no aerodynamic drag."""
    m = finite("mass", mass_kg, positive=True)
    r = finite("radius", radius_m, positive=True)
    a = finite("acceleration", acceleration_m_s2, minimum=0)
    grade = finite("grade", grade_deg, minimum=0)
    if grade >= 89:
        raise ValueError("grade must be less than 89 degrees; tipping/terrain need separate models")
    wheels = finite("driven wheels", driven_wheels, positive=True)
    if not wheels.is_integer():
        raise ValueError("driven wheels must be an integer")
    crr = finite("rolling coefficient", rolling_coefficient, minimum=0)
    mu = finite("traction coefficient", traction_coefficient, minimum=0)
    eta = efficiency("drive efficiency", drive_efficiency)
    theta = math.radians(grade)
    normal = m * G * math.cos(theta)
    force = m * a + m * G * math.sin(theta) + crr * normal
    return {"force_n": force, "wheel_load_torque_nm_each": force * r / wheels,
            "equivalent_input_torque_nm_each_at_1_to_1": force * r / (wheels * eta),
            "traction_limit_n": mu * normal, "traction_feasible_in_simple_model": force <= mu * normal}


def planar_2r_ik(l1_m, l2_m, x_m, y_m):
    """Two position-only planar arm solutions in radians; no collisions/joint limits."""
    l1 = finite("link 1", l1_m, positive=True)
    l2 = finite("link 2", l2_m, positive=True)
    x, y = finite("x", x_m), finite("y", y_m)
    radius = math.hypot(x, y)
    if radius < 1e-12 and abs(l1-l2) < 1e-12:
        raise ValueError("folded origin has infinitely many shoulder solutions; specify a posture")
    c2 = (x*x + y*y - l1*l1 - l2*l2) / (2*l1*l2)
    if abs(c2) > 1 + 1e-12:
        raise ValueError("target outside the annular reachable workspace")
    c2 = max(-1.0, min(1.0, c2))
    result = []
    for sign in (1, -1):
        q2 = sign * math.acos(c2)
        q1 = math.atan2(y, x) - math.atan2(l2*math.sin(q2), l1+l2*math.cos(q2))
        result.append({"q1_rad": q1, "q2_rad": q2, "singular": abs(math.sin(q2)) < 1e-10})
    return result


def contribution_model(cost_per_start, yield_fraction, variable_per_sold, net_price, fixed_cost):
    """All starts incur full production cost; failures scrapped with no recovery."""
    unit = finite("cost per start", cost_per_start, minimum=0) / efficiency("yield", yield_fraction) + finite("variable sold cost", variable_per_sold, minimum=0)
    price = finite("net price", net_price, positive=True)
    fixed = finite("fixed cost", fixed_cost, minimum=0)
    contribution = price-unit
    return {"variable_cost_per_good_unit": unit, "contribution_per_unit": contribution,
            "contribution_fraction": contribution/price,
            "break_even_units": math.ceil(fixed/contribution) if contribution > 0 else None,
            "break_even_possible": contribution > 0}


def demo():
    return {"evidence": "calculated educational examples; no hardware validation or market quotes",
            "screw_torque_nm": screw_torque(100, 0.005, 0.9),
            "battery_runtime_h": battery_runtime(24, 10, 0.8, 0.9, 60),
            "rover": rover_sizing(20, 0.1, 0.5, 5, 0.02, 0.8, 4, 0.6),
            "arm_solutions": planar_2r_ik(0.3, 0.2, 0.3, 0.2),
            "cost_base": contribution_model(245, 0.95, 25, 450, 30000),
            "cost_lower_yield": contribution_model(245, 0.85, 25, 450, 30000),
            "cost_lower_price": contribution_model(245, 0.95, 25, 400, 30000)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="print the documented examples as JSON")
    args = parser.parse_args()
    if args.demo:
        print(json.dumps(demo(), indent=2, allow_nan=False))
    else:
        parser.print_help()
