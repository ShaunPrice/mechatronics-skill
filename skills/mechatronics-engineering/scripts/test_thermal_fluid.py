"""Independent physical/limiting-case checks for educational thermal/fluid helpers."""
import json
import math
import unittest

from thermal_fluid_calcs import (
    buoyancy_force, darcy_friction_factor, demo, hydrostatic_gauge_pressure,
    lumped_temperature, minor_pressure_loss, net_radiation_w, pipe_pressure_loss,
    plane_wall_resistance, pump_power, reynolds_number, sealed_gas_pressure,
)


class ThermalTests(unittest.TestCase):
    def test_initial_equilibrium_and_time_constant(self):
        self.assertEqual(lumped_temperature(293.15, 293.15, 20, 100, 2, 0), 293.15)
        self.assertAlmostEqual(lumped_temperature(303.15, 293.15, 20, 100, 2, 500), 303.15)
        # At one time constant, 1-exp(-1) of the 10 K rise has occurred.
        self.assertAlmostEqual(lumped_temperature(293.15, 293.15, 20, 100, 2, 50),
                               293.15 + 10 * (1 - math.exp(-1)))
        self.assertAlmostEqual(lumped_temperature(293.15, 293.15, 20, 100, 2, 2000),
                               303.15)

    def test_adiabatic_energy_and_zero_conductance_limit(self):
        final = lumped_temperature(300, 290, 20, 100, 0, 50)
        self.assertAlmostEqual(100 * (final - 300), 20 * 50)
        self.assertAlmostEqual(lumped_temperature(300, 290, 20, 100, 1e-12, 50),
                               final, places=9)
        self.assertAlmostEqual(lumped_temperature(300, 290, -20, 100, 0, 50), 290)

    def test_heat_balance_derivative(self):
        # Independent numerical derivative must satisfy the specified ODE.
        t, dt = 23.0, 0.001
        temp = lambda at: lumped_temperature(280, 293, 12, 75, 1.5, at)
        derivative = (temp(t + dt) - temp(t - dt)) / (2 * dt)
        self.assertAlmostEqual(75 * derivative, 12 - 1.5 * (temp(t) - 293), places=6)

    def test_time_composition(self):
        at_20 = lumped_temperature(280, 293, 12, 75, 1.5, 20)
        two_intervals = lumped_temperature(at_20, 293, 12, 75, 1.5, 30)
        self.assertAlmostEqual(two_intervals,
                               lumped_temperature(280, 293, 12, 75, 1.5, 50))

    def test_wall_resistance_and_fourier_heat_rate(self):
        resistance = plane_wall_resistance(0.01, 0.2, 0.1)
        self.assertAlmostEqual(resistance, 0.5)
        # A 20 K drop gives 40 W; doubling area doubles that rate.
        self.assertAlmostEqual(20 / resistance, 40)
        self.assertAlmostEqual(plane_wall_resistance(0.01, 0.2, 0.2), resistance / 2)
        self.assertEqual(plane_wall_resistance(0, 0.2, 0.1), 0)

    def test_radiation_zero_sign_and_independent_value(self):
        self.assertEqual(net_radiation_w(0.8, 0.1, 300, 300), 0)
        self.assertEqual(net_radiation_w(0, 0.1, 330, 300), 0)
        hot = net_radiation_w(0.8, 0.1, 330, 300)
        self.assertGreater(hot, 0)
        self.assertAlmostEqual(net_radiation_w(0.8, 0.1, 300, 330), -hot)
        self.assertAlmostEqual(hot, 5.670374419e-8 * 0.8 * 0.1 * (330**4 - 300**4))


class FluidTests(unittest.TestCase):
    def test_reynolds_laminar_and_hagen_poiseuille(self):
        # rho=1000, mu=.001, D=.01, mean v=.1 => Re=1000.
        self.assertAlmostEqual(reynolds_number(1000, 0.1, 0.01, 0.001), 1000)
        flow = 0.1 * math.pi * 0.01**2 / 4
        result = pipe_pressure_loss(1000, 0.001, 0.01, 2, flow)
        self.assertEqual(result["regime"], "laminar")
        self.assertAlmostEqual(result["darcy_friction_factor"], 0.064)
        # Independent Poiseuille form, dp=128*mu*L*Q/(pi*D^4).
        reference = 128 * 0.001 * 2 * flow / (math.pi * 0.01**4)
        self.assertAlmostEqual(result["total_loss_pa"], reference)
        self.assertAlmostEqual(reference, 64.0)

    def test_turbulent_roughness_and_colebrook_residual(self):
        smooth = darcy_friction_factor(100000, 0)
        rough = darcy_friction_factor(100000, 0.001)
        self.assertGreater(rough, smooth)
        self.assertTrue(0.01 < smooth < 0.03)
        # Haaland approximates Colebrook; verify an independently expressed
        # implicit relation at this one point, without claiming uniform accuracy.
        inverse_root = 1 / math.sqrt(rough)
        colebrook_rhs = -2 * math.log10(0.001 / 3.7 + 2.51 * inverse_root / 100000)
        self.assertLess(abs(inverse_root - colebrook_rhs) / colebrook_rhs, 0.01)
        flow = 0.0002
        result = pipe_pressure_loss(1000, 0.001, 0.02, 2, flow, 0.00001, 2)
        self.assertEqual(result["regime"], "turbulent_haaland")
        self.assertGreater(result["major_loss_pa"], 0)
        self.assertAlmostEqual(result["total_loss_pa"],
                               result["major_loss_pa"] + result["minor_loss_pa"])

    def test_transition_and_correlation_domain_rejected(self):
        for re in (2300, 3000, 3999.999):
            with self.subTest(reynolds=re), self.assertRaisesRegex(ValueError, "transitional"):
                darcy_friction_factor(re)
        self.assertGreater(darcy_friction_factor(4000), 0)
        for re, rough in ((1e8 + 1, 0), (10000, 0.051), (0, 0)):
            with self.subTest(reynolds=re, roughness=rough), self.assertRaises(ValueError):
                darcy_friction_factor(re, rough)
        transition_flow = 0.3 * math.pi * 0.01**2 / 4  # Re=3000
        with self.assertRaisesRegex(ValueError, "transitional"):
            pipe_pressure_loss(1000, 0.001, 0.01, 2, transition_flow)

    def test_minor_loss_and_zero_flow(self):
        self.assertEqual(minor_pressure_loss(3, 1000, 2), 6000)
        result = pipe_pressure_loss(1000, 0.001, 0.02, 2, 0, minor_k=3)
        self.assertEqual(result["regime"], "no_flow")
        self.assertIsNone(result["darcy_friction_factor"])
        for name in ("mean_speed_m_s", "reynolds", "major_loss_pa", "minor_loss_pa", "total_loss_pa"):
            self.assertEqual(result[name], 0)

    def test_hydrostatic_buoyancy_and_gravity_scaling(self):
        self.assertAlmostEqual(hydrostatic_gauge_pressure(1000, 2), 19613.3)
        self.assertAlmostEqual(buoyancy_force(1000, 0.003), 29.41995)
        self.assertEqual(hydrostatic_gauge_pressure(1000, 0), 0)
        self.assertEqual(buoyancy_force(1000, 0), 0)
        self.assertAlmostEqual(hydrostatic_gauge_pressure(1000, 2, 4.903325), 19613.3 / 2)

    def test_pump_energy_and_efficiency_boundary(self):
        result = pump_power(1000, 0.001, 10, 0.5)
        self.assertAlmostEqual(result["hydraulic_power_w"], 98.0665)
        self.assertAlmostEqual(result["input_power_w"], 196.133)
        self.assertAlmostEqual(result["input_power_w"] * 0.5, result["hydraulic_power_w"])
        ideal = pump_power(1000, 0.001, 10, 1)
        self.assertEqual(ideal["input_power_w"], ideal["hydraulic_power_w"])
        self.assertEqual(pump_power(1000, 0, 10, 0.5)["hydraulic_power_w"], 0)

    def test_sealed_ideal_gas_absolute_pressure(self):
        self.assertEqual(sealed_gas_pressure(100000, 300, 600), 200000)
        self.assertEqual(sealed_gas_pressure(100000, 300, 300), 100000)


class InputAndDemoTests(unittest.TestCase):
    def test_guide_worked_examples(self):
        self.assertAlmostEqual(lumped_temperature(298.15, 298.15, 50, 500, 5, 30),
                               300.7418178, places=7)
        self.assertAlmostEqual(lumped_temperature(298.15, 298.15, 50, 500, 5, 100),
                               304.4712056, places=7)
        pipe = pipe_pressure_loss(1000, 0.001, 0.01, 2, 0.00001)
        self.assertAlmostEqual(pipe["reynolds"], 1273.2395447, places=7)
        self.assertAlmostEqual(pipe["major_loss_pa"], 81.48733086, places=7)
        self.assertAlmostEqual(pump_power(1000, 0.001, 1, 0.6, 9.81)["input_power_w"], 16.35)

    def test_nonfinite_inputs_each_helper(self):
        calls = (
            (lumped_temperature, (300, 290, 20, 100, 2, 50)),
            (plane_wall_resistance, (0.01, 0.2, 0.1)),
            (net_radiation_w, (0.8, 0.1, 330, 300)),
            (reynolds_number, (1000, 0.1, 0.01, 0.001)),
            (darcy_friction_factor, (10000, 0.001)),
            (minor_pressure_loss, (2, 1000, 0.1)),
            (pipe_pressure_loss, (1000, 0.001, 0.02, 2, 0.0002, 0.00001, 2)),
            (hydrostatic_gauge_pressure, (1000, 2, 9.80665)),
            (buoyancy_force, (1000, 0.003, 9.80665)),
            (pump_power, (1000, 0.0002, 3, 0.6, 9.80665)),
            (sealed_gas_pressure, (101325, 293.15, 333.15)),
        )
        for function, original in calls:
            for index in range(len(original)):
                for invalid in (math.nan, math.inf, -math.inf):
                    args = list(original)
                    args[index] = invalid
                    with self.subTest(function=function.__name__, argument=index, value=invalid):
                        with self.assertRaises(ValueError):
                            function(*args)

    def test_invalid_physical_domains(self):
        calls = (
            (lumped_temperature, (0, 290, 20, 100, 2, 50)),
            (lumped_temperature, (300, 290, 20, 0, 2, 50)),
            (lumped_temperature, (300, 290, 20, 100, -2, 50)),
            (lumped_temperature, (300, 290, 20, 100, 2, -1)),
            (lumped_temperature, (300, 290, -1000, 1, 0, 1)),
            (plane_wall_resistance, (-0.01, 0.2, 0.1)),
            (plane_wall_resistance, (0.01, 0, 0.1)),
            (plane_wall_resistance, (0.01, 0.2, 0)),
            (net_radiation_w, (1.1, 0.1, 330, 300)),
            (net_radiation_w, (0.8, 0.1, -10, 300)),
            (reynolds_number, (1000, -1, 0.01, 0.001)),
            (reynolds_number, (1000, 1, 0.01, 0)),
            (minor_pressure_loss, (-1, 1000, 1)),
            (pipe_pressure_loss, (1000, 0.001, 0, 2, 0)),
            (pipe_pressure_loss, (1000, 0.001, 0.02, 2, -1)),
            (hydrostatic_gauge_pressure, (1000, -1)),
            (buoyancy_force, (1000, -1)),
            (pump_power, (1000, 0.001, 10, 0)),
            (pump_power, (1000, 0.001, 10, 1.1)),
            (pump_power, (1000, 0.001, -10, 0.6)),
            (sealed_gas_pressure, (0, 300, 350)),
            (sealed_gas_pressure, (100000, 0, 350)),
        )
        for function, args in calls:
            with self.subTest(function=function.__name__, args=args), self.assertRaises(ValueError):
                function(*args)

    def test_demo_strict_json(self):
        result = json.loads(json.dumps(demo(), allow_nan=False))
        self.assertIn("calculated", result["evidence"])
        self.assertIn("assumptions", result["thermal"])
        self.assertEqual(result["pipe"]["result"]["regime"], "turbulent_haaland")


if __name__ == "__main__":
    unittest.main()
