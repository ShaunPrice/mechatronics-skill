"""Numerical/property checks for the teaching helpers. Run with Python unittest."""
import math
import unittest
from control_lab import PID, rk4_step, simulate, frequency_response
from engineering_calcs import screw_torque, battery_runtime, rover_sizing, planar_2r_ik, contribution_model


class EngineeringTests(unittest.TestCase):
    def test_energy_and_screw_work_balance(self):
        self.assertAlmostEqual(screw_torque(100, .005, .9)*2*math.pi*.9, 100*.005)
        self.assertAlmostEqual(battery_runtime(24, 10, .8, .9, 60), 2.88)

    def test_rover_force_and_traction(self):
        r = rover_sizing(20, .1, .5, 0, 0, 1, 4, .01)
        self.assertAlmostEqual(r["force_n"], 10)
        self.assertAlmostEqual(r["wheel_load_torque_nm_each"], .25)
        self.assertFalse(r["traction_feasible_in_simple_model"])

    def test_ik_round_trip_both_branches(self):
        for x, y in ((.3, .2), (-.2, .2), (.1, -.25), (.5, 0)):
            for s in planar_2r_ik(.3, .2, x, y):
                q1, q2 = s["q1_rad"], s["q2_rad"]
                self.assertAlmostEqual(.3*math.cos(q1)+.2*math.cos(q1+q2), x)
                self.assertAlmostEqual(.3*math.sin(q1)+.2*math.sin(q1+q2), y)

    def test_ik_rejects_unreachable_and_underdetermined(self):
        for args in ((.3,.2,.6,0), (.3,.2,.01,0), (.3,.3,0,0)):
            with self.assertRaises(ValueError):
                planar_2r_ik(*args)

    def test_cost_sensitivity_and_no_false_break_even(self):
        self.assertEqual(contribution_model(245,.95,25,450,30000)["break_even_units"],180)
        self.assertEqual(contribution_model(245,.85,25,450,30000)["break_even_units"],220)
        self.assertEqual(contribution_model(245,.95,25,400,30000)["break_even_units"],257)
        self.assertIsNone(contribution_model(500,1,0,450,30000)["break_even_units"])

    def test_invalid_inputs(self):
        for f, args in ((battery_runtime,(24,10,1.1,1,60)),(screw_torque,(1,.005,0)),(contribution_model,(1,0,0,1,1)),(planar_2r_ik,(.3,.2,float('nan'),0))):
            with self.assertRaises(ValueError):
                f(*args)

    def test_rk4_matches_undamped_analytic_oscillator(self):
        x,v=1.,0.
        for _ in range(1000):
            x,v=rk4_step(x,v,0,.001,1,0,4)
        self.assertAlmostEqual(x,math.cos(2),places=10)
        self.assertAlmostEqual(v,-2*math.sin(2),places=10)
        self.assertAlmostEqual(.5*v*v+2*x*x,2,places=10)

    def test_pid_saturation_antiwindup_and_no_derivative_kick(self):
        p=PID()
        for _ in range(1000):
            self.assertLessEqual(abs(p.update(100,0,.01)),10)
        self.assertEqual(p.integral,0)
        self.assertEqual(p.update(0,0,.01),0)
        derivative_only=PID(kp=0,ki=0,kd=10)
        derivative_only.update(0,0,.01)
        self.assertEqual(derivative_only.update(100,0,.01),0)

    def test_simulation_convergence_and_disturbance_rejection(self):
        rows,m=simulate(substeps=5)
        refined,m2=simulate(substeps=10)
        self.assertLess(max(abs(a["closed_loop_m"]-b["closed_loop_m"]) for a,b in zip(rows,refined)),1e-8)
        self.assertLess(abs(m["final_error_m"]),.005)
        self.assertGreater(abs(m["final_open_loop_error_m"]),.04)
        self.assertLessEqual(m["peak_abs_command_n"],10)

    def test_bode_low_frequency_gain_and_high_frequency_phase(self):
        f=frequency_response()
        self.assertAlmostEqual(f[0]["magnitude_db_re_1_m_per_n"],20*math.log10(1/20),places=2)
        self.assertLess(f[-1]["phase_deg"],-179)


if __name__ == "__main__":
    unittest.main()
