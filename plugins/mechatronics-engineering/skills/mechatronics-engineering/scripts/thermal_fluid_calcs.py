#!/usr/bin/env python3
"""SI educational heat/fluid helpers; standard library only, no hardware/network I/O.

The models assume constant properties and are not CFD, pressure-vessel design,
material qualification, or measured performance. All temperatures are kelvin;
all pressures are pascals. Read each function's assumptions before applying it.
"""
import argparse
import json
import math

STANDARD_GRAVITY_M_S2 = 9.80665
STEFAN_BOLTZMANN_W_M2_K4 = 5.670374419e-8


def _number(name, value, minimum=None, positive=False):
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if (not math.isfinite(result) or
            (minimum is not None and result < minimum) or
            (positive and result <= 0)):
        raise ValueError(f"{name} is outside its finite allowed range")
    return result


def _efficiency(value):
    result = _number("efficiency", value, positive=True)
    if result > 1:
        raise ValueError("efficiency must be in (0, 1]")
    return result


def lumped_temperature(initial_k, ambient_k, power_w, heat_capacity_j_k,
                       thermal_conductance_w_k, time_s):
    """Exact T(t) for C*dT/dt = P - UA*(T-Ta); returns kelvin.

    Constant net heat input P (negative allows cooling), constant ambient Ta,
    positive lumped heat capacity C, nonnegative conductance UA. Assumes the
    body is adequately represented by one uniform temperature; assess internal
    gradients/Biot number separately. No phase change or radiation nonlinearity.
    UA=0 gives T=T0+P*t/C. A result at/below zero kelvin is rejected.
    """
    t0 = _number("initial temperature K", initial_k, positive=True)
    ta = _number("ambient temperature K", ambient_k, positive=True)
    power = _number("power W", power_w)
    capacity = _number("heat capacity J/K", heat_capacity_j_k, positive=True)
    conductance = _number("thermal conductance W/K", thermal_conductance_w_k,
                          minimum=0)
    duration = _number("time s", time_s, minimum=0)
    if duration == 0:
        return t0
    time_over_capacity = _number("time/capacity", duration / capacity)
    if conductance == 0:
        return _number("calculated temperature K", t0 + power * time_over_capacity,
                       positive=True)
    exponent = _number("UA*t/C", conductance * time_over_capacity)
    # expm1 avoids loss of the short-time temperature change when t << C/UA.
    fraction = -math.expm1(-exponent)
    response_ratio = fraction / exponent if exponent != 0 else 1.0
    temperature = (t0 + (ta - t0) * fraction +
                   power * time_over_capacity * response_ratio)
    return _number("calculated temperature K", temperature, positive=True)


def plane_wall_resistance(thickness_m, conductivity_w_m_k, area_m2):
    """R=L/(k*A), K/W: steady 1-D planar conduction, constant k.

    Excludes contact, convection, radiation, spreading resistance and heat
    generation in the wall. Zero thickness gives zero resistance.
    """
    length = _number("thickness m", thickness_m, minimum=0)
    conductivity = _number("conductivity W/(m K)", conductivity_w_m_k,
                           positive=True)
    area = _number("area m2", area_m2, positive=True)
    denominator = _number("k*A", conductivity * area, positive=True)
    return _number("thermal resistance K/W", length / denominator, minimum=0)


def net_radiation_w(emissivity, area_m2, surface_k, surroundings_k):
    """Net outward radiation eps*sigma*A*(Ts**4-Ta**4), watts.

    Diffuse-gray surface in a large isothermal black enclosure, view factor 1;
    constant emissivity. Positive means heat leaves the surface. Arbitrary
    multiple surfaces need view factors/radiosity instead. Temperatures: K.
    """
    eps = _number("emissivity", emissivity, minimum=0)
    if eps > 1:
        raise ValueError("emissivity must be in [0, 1]")
    area = _number("radiating area m2", area_m2, minimum=0)
    ts = _number("surface temperature K", surface_k, positive=True)
    ta = _number("surroundings temperature K", surroundings_k, positive=True)
    if eps == 0 or area == 0 or ts == ta:
        return 0.0
    # Factored fourth-power difference reduces cancellation near equilibrium.
    fourth_power_difference = (ts - ta) * (ts + ta) * (ts * ts + ta * ta)
    return _number("net outward radiation W",
                   eps * STEFAN_BOLTZMANN_W_M2_K4 * area * fourth_power_difference)


def reynolds_number(density_kg_m3, speed_m_s, diameter_m, dynamic_viscosity_pa_s):
    """Pipe Re=rho*v*D/mu, dimensionless; speed is a nonnegative magnitude."""
    rho = _number("density kg/m3", density_kg_m3, positive=True)
    speed = _number("speed m/s", speed_m_s, minimum=0)
    diameter = _number("diameter m", diameter_m, positive=True)
    viscosity = _number("dynamic viscosity Pa s", dynamic_viscosity_pa_s,
                        positive=True)
    return _number("Reynolds number", rho * speed * diameter / viscosity, minimum=0)


def darcy_friction_factor(reynolds, relative_roughness=0.0):
    """Darcy (not Fanning) factor for fully developed circular-pipe flow.

    Laminar: 64/Re for 0<Re<2300. Transition 2300<=Re<4000 is rejected.
    Turbulent: Haaland's explicit approximation to the Colebrook relation,
      1/sqrt(f) = -1.8*log10((eps/D/3.7)**1.11 + 6.9/Re).
    This educational helper deliberately bounds its turbulent inputs to
    4000<=Re<=1e8 and 0<=eps/D<=0.05. Those limits are an implementation domain,
    not a claim of a universal flow transition or guaranteed correlation error.
    Disturbances/entrance conditions can shift actual transition. Assumes a
    single-phase Newtonian fluid, fixed roughness and steady developed flow.
    At zero flow f is undefined; pipe_pressure_loss handles that case separately.
    """
    re = _number("Reynolds number", reynolds, positive=True)
    rough = _number("relative roughness", relative_roughness, minimum=0)
    if rough > 0.05:
        raise ValueError("relative roughness exceeds this helper's 0.05 limit")
    if re < 2300:
        return _number("Darcy friction factor", 64.0 / re, positive=True)
    if re < 4000:
        raise ValueError("transitional flow: no friction factor is provided for 2300<=Re<4000")
    if re > 1e8:
        raise ValueError("Reynolds number exceeds this helper's turbulent limit 1e8")
    inverse_sqrt = -1.8 * math.log10((rough / 3.7) ** 1.11 + 6.9 / re)
    return _number("Darcy friction factor", 1.0 / (inverse_sqrt * inverse_sqrt),
                   positive=True)


def minor_pressure_loss(loss_coefficient, density_kg_m3, speed_m_s):
    """K*rho*v**2/2, Pa; K must refer to the stated section's velocity.

    K is supplied, not inferred from an unidentified fitting. Losses sharing a
    velocity reference may sum K. Reynolds-dependent fittings need suitable K.
    """
    coefficient = _number("minor-loss coefficient K", loss_coefficient, minimum=0)
    rho = _number("density kg/m3", density_kg_m3, positive=True)
    speed = _number("speed m/s", speed_m_s, minimum=0)
    return _number("minor pressure loss Pa", coefficient * rho * speed * speed / 2,
                   minimum=0)


def pipe_pressure_loss(density_kg_m3, dynamic_viscosity_pa_s, diameter_m,
                       length_m, flow_m3_s, roughness_m=0.0, minor_k=0.0):
    """Darcy-Weisbach friction + minor loss for one constant-bore pipe, SI.

    Q is a nonnegative volumetric flow magnitude. Returns positive dissipative
    losses, not a signed pressure difference or static elevation head. Constant
    density/viscosity, Newtonian incompressible single-phase fully developed
    steady flow. Excludes entrance development, water hammer and cavitation.
    Use pump/system-curve analysis separately; a pressure-loss number is not a
    pump operating point. Minor K uses this pipe's mean speed.
    """
    rho = _number("density kg/m3", density_kg_m3, positive=True)
    viscosity = _number("dynamic viscosity Pa s", dynamic_viscosity_pa_s,
                        positive=True)
    diameter = _number("diameter m", diameter_m, positive=True)
    length = _number("length m", length_m, minimum=0)
    flow = _number("volumetric flow m3/s", flow_m3_s, minimum=0)
    roughness = _number("absolute roughness m", roughness_m, minimum=0)
    coefficient = _number("minor-loss coefficient K", minor_k, minimum=0)
    rough_ratio = _number("relative roughness", roughness / diameter, minimum=0)
    if rough_ratio > 0.05:
        raise ValueError("relative roughness exceeds this helper's 0.05 limit")
    area = _number("pipe cross-sectional area m2", math.pi * diameter * diameter / 4,
                   positive=True)
    speed = _number("mean speed m/s", flow / area, minimum=0)
    re = reynolds_number(rho, speed, diameter, viscosity)
    if flow == 0:
        factor, major, minor, regime = None, 0.0, 0.0, "no_flow"
    else:
        factor = darcy_friction_factor(re, rough_ratio)
        major = _number("major pressure loss Pa",
                        factor * (length / diameter) * rho * speed * speed / 2,
                        minimum=0)
        minor = minor_pressure_loss(coefficient, rho, speed)
        regime = "laminar" if re < 2300 else "turbulent_haaland"
    return {"flow_m3_s": flow, "mean_speed_m_s": speed, "reynolds": re,
            "relative_roughness": rough_ratio, "regime": regime,
            "darcy_friction_factor": factor, "major_loss_pa": major,
            "minor_loss_pa": minor,
            "total_loss_pa": _number("total pressure loss Pa", major + minor,
                                     minimum=0)}


def hydrostatic_gauge_pressure(density_kg_m3, depth_m, gravity_m_s2=STANDARD_GRAVITY_M_S2):
    """rho*g*h, Pa relative to surface pressure; constant-density static fluid."""
    rho = _number("density kg/m3", density_kg_m3, positive=True)
    depth = _number("depth below surface m", depth_m, minimum=0)
    gravity = _number("gravity m/s2", gravity_m_s2, positive=True)
    return _number("hydrostatic gauge pressure Pa", rho * gravity * depth, minimum=0)


def buoyancy_force(density_kg_m3, displaced_volume_m3, gravity_m_s2=STANDARD_GRAVITY_M_S2):
    """Upward force rho*g*V, N, for static constant-density fluid.

    V is submerged displaced volume. Net lift subtracts body weight; attitude
    stability, drag and added mass require separate models.
    """
    rho = _number("fluid density kg/m3", density_kg_m3, positive=True)
    volume = _number("displaced volume m3", displaced_volume_m3, minimum=0)
    gravity = _number("gravity m/s2", gravity_m_s2, positive=True)
    return _number("upward buoyancy N", rho * gravity * volume, minimum=0)


def pump_power(density_kg_m3, flow_m3_s, head_m, efficiency,
               gravity_m_s2=STANDARD_GRAVITY_M_S2):
    """Hydraulic rho*g*Q*H and input power, W, for supplied operating point.

    Head H is total developed head. Efficiency must describe the desired input
    boundary: pump-only for shaft input or overall wire-to-water for electrical
    input. Constant density; no claim about pump curve, NPSH or motor selection.
    At zero useful hydraulic power the ideal estimate is zero; real no-load
    electrical consumption cannot be inferred from this efficiency model.
    """
    rho = _number("density kg/m3", density_kg_m3, positive=True)
    flow = _number("flow m3/s", flow_m3_s, minimum=0)
    head = _number("head m", head_m, minimum=0)
    eta = _efficiency(efficiency)
    gravity = _number("gravity m/s2", gravity_m_s2, positive=True)
    hydraulic = _number("hydraulic power W", rho * gravity * flow * head, minimum=0)
    return {"hydraulic_power_w": hydraulic,
            "input_power_w": _number("input power W", hydraulic / eta, minimum=0),
            "efficiency": eta}


def sealed_gas_pressure(initial_absolute_pa, initial_k, final_k):
    """P2=P1*T2/T1, absolute Pa: sealed rigid volume, fixed ideal-gas amount.

    Both temperatures are kelvin; do not use gauge pressure in the ratio.
    Excludes leakage, condensation, changing volume and nonideal-gas effects.
    This relation does not establish an enclosure's pressure rating.
    """
    pressure = _number("initial absolute pressure Pa", initial_absolute_pa,
                       positive=True)
    t1 = _number("initial temperature K", initial_k, positive=True)
    t2 = _number("final temperature K", final_k, positive=True)
    return _number("final absolute pressure Pa", pressure * (t2 / t1), positive=True)


def demo():
    """Illustrative values only; properties are assumptions, not material data."""
    return {
        "evidence": "calculated educational examples; no hardware/CFD validation",
        "units": "SI: m, kg, s, K, Pa, W; temperatures absolute kelvin",
        "thermal": {
            "assumptions": "uniform body; T0=Ta=298.15 K, P=50 W, C=500 J/K, UA=5 W/K; constant properties",
            "time_constant_s": 100.0,
            "equilibrium_k": 308.15,
            "temperature_after_30_s_k": lumped_temperature(298.15, 298.15, 50, 500, 5, 30),
            "temperature_after_100_s_k": lumped_temperature(298.15, 298.15, 50, 500, 5, 100),
            "adiabatic_temperature_after_100_s_k": lumped_temperature(298.15, 298.15, 50, 500, 0, 100),
        },
        "wall": {
            "assumptions": "1-D plane wall L=0.01 m, k=0.2 W/(m K), A=0.1 m2; no contacts",
            "resistance_k_w": plane_wall_resistance(0.01, 0.2, 0.1),
        },
        "radiation": {
            "assumptions": "eps=0.8, A=0.1 m2, Ts=330 K, large black surroundings=293.15 K, view factor=1",
            "net_outward_w": net_radiation_w(0.8, 0.1, 330, 293.15),
        },
        "pipe": {
            "assumptions": "single-phase Newtonian fluid; rho=1000 kg/m3, mu=0.001 Pa s, D=0.02 m, L=2 m, Q=0.0002 m3/s, roughness=0.00001 m, K=2; developed flow",
            "result": pipe_pressure_loss(1000, 0.001, 0.02, 2, 0.0002, 0.00001, 2),
        },
        "laminar_pipe": {
            "assumptions": "illustrative water properties rho=1000 kg/m3, mu=0.001 Pa s, D=0.01 m, L=2 m, Q=0.00001 m3/s, K=0; developed flow, no elevation difference",
            "result": pipe_pressure_loss(1000, 0.001, 0.01, 2, 0.00001),
        },
        "hydrostatics": {
            "assumptions": "static constant rho=1000 kg/m3; depth=2 m; submerged displacement=0.003 m3",
            "gauge_pressure_pa": hydrostatic_gauge_pressure(1000, 2),
            "upward_buoyancy_n": buoyancy_force(1000, 0.003),
        },
        "pump": {
            "assumptions": "rho=1000 kg/m3, supplied Q=0.001 m3/s and developed head=1 m, g=9.81 m/s2; overall electrical-to-hydraulic efficiency=0.6",
            "result": pump_power(1000, 0.001, 1, 0.6, gravity_m_s2=9.81),
        },
        "sealed_gas": {
            "assumptions": "fixed amount of ideal gas in rigid sealed volume; initial absolute pressure=101325 Pa, initial=293.15 K, final=333.15 K",
            "final_absolute_pa": sealed_gas_pressure(101325, 293.15, 333.15),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="print illustrative SI examples as JSON")
    args = parser.parse_args()
    if args.demo:
        print(json.dumps(demo(), indent=2, allow_nan=False))
    else:
        parser.print_help()
