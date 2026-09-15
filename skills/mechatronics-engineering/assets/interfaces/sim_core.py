"""Pure Python selected-plant simulator. MIT. No ROS or hardware dependency."""
import math

SCHEMA = "mechatronics-selected-plant/v1"


def number(value, name, low=-1e308, high=1e308):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, not a string/bool")
    # Compare bounds before isfinite, which may overflow on huge JSON integers.
    if not low <= value <= high or not math.isfinite(value):
        raise ValueError(f"{name} outside finite range [{low}, {high}]")
    return float(value)


def plant_matrices(kind, params):
    """Known SISO continuous plants: x_dot=A*x+B*u, y=C*x+D*u."""
    if not isinstance(params, dict):
        raise ValueError("parameters must be an object")
    if kind == "massSpring":
        limits = {"m": (.02, 1000), "b": (.001, 100), "k": (.001, 1000),
                  "initialPosition": (-100, 100), "initialVelocity": (-1000, 1000)}
    elif kind == "firstOrder":
        limits = {"gain": (-1e4, 1e4), "tau": (.001, 100), "initial": (-1e5, 1e5)}
    else:
        raise ValueError("only massSpring and firstOrder plants can be exported")
    if set(params) != set(limits):
        raise ValueError("plant parameter fields do not match the selected model")
    p = {k: number(params[k], k, *bound) for k, bound in limits.items()}
    if kind == "massSpring":
        return {"A": [[0.0, 1.0], [-p["k"]/p["m"], -p["b"]/p["m"]]],
                "B": [[0.0], [1.0/p["m"]]], "C": [[1.0, 0.0]], "D": [[0.0]],
                "x0": [p["initialPosition"], p["initialVelocity"]],
                "rate_bound_s_inv": max(math.sqrt(p["k"]/p["m"]), p["b"]/p["m"])}
    return {"A": [[-1.0/p["tau"]]], "B": [[p["gain"]/p["tau"]]],
            "C": [[1.0]], "D": [[0.0]], "x0": [p["initial"]],
            "rate_bound_s_inv": 1.0/p["tau"]}


def sample_count(duration, dt):
    """Browser sample-count convention: snap near integral ratios, else ceil."""
    ratio = duration/dt
    nearest = math.floor(ratio + .5)
    return nearest if abs(ratio-nearest) <= 1e-10*max(1, abs(ratio)) else math.ceil(ratio)


class PlantSimulator:
    """Fixed dt RK4 with bounded substeps and receipt-age input watchdog.

    One call advances one simulation interval; elapsed wall time never causes
    catch-up integration. Physical real-time performance is not established.
    State order/units and plant-only boundary are carried in config metadata.
    """
    def __init__(self, config):
        if not isinstance(config, dict) or config.get("schema") != SCHEMA:
            raise ValueError("expected selected-plant schema")
        self.config = config
        expected = plant_matrices(config.get("plant_type"), config.get("parameters"))
        # Do not run arbitrary edited matrices with the known model's step bound.
        for key in ("A", "B", "C", "D", "x0"):
            if config.get(key) != expected[key]:
                raise ValueError(f"{key} differs from the documented plant parameters")
        self.dt = number(config.get("dt_s"), "dt_s", .001, .1)
        self.duration = number(config.get("requested_duration_s"), "duration", .1, 60)
        self.max_steps = sample_count(self.duration, self.dt)
        self.watchdog = number(config.get("watchdog_s"), "watchdog_s", .001, 10)
        self.input_limit = number(config.get("input_limit"), "input_limit", .001, 1e6)
        self.substeps = max(1, math.ceil(self.dt * expected["rate_bound_s_inv"] / .1))
        if self.substeps > 25000 or self.substeps * self.max_steps > 20000000:
            raise ValueError("selected plant exceeds bounded integration workload")
        self.A, self.B, self.C, self.D = (expected[k] for k in ("A", "B", "C", "D"))
        self.x = list(expected["x0"])
        self.index = 0
        self.command = 0.0
        self.last_receipt = None
        self.last_wall = None
        self.last_input = 0.0
        self.stale = True

    @property
    def done(self):
        return self.index >= self.max_steps

    def receive(self, value, wall_time_s):
        """Receive scalar command; invalid/out-of-envelope command clears it.

        wall_time_s is local monotonic receipt time, not a sender timestamp.
        The Float64 ROS transport cannot establish age before local receipt.
        """
        try:
            now = number(wall_time_s, "monotonic receipt time", 0)
            command = number(value, "input", -self.input_limit, self.input_limit)
            if ((self.last_wall is not None and now < self.last_wall) or
                    (self.last_receipt is not None and now < self.last_receipt)):
                raise ValueError("monotonic receipt clock moved backwards")
        except ValueError:
            self.command, self.last_receipt = 0.0, None
            return False
        self.command, self.last_receipt = command, now
        return True

    def derivative(self, state, value):
        return [sum(a*x for a, x in zip(row, state)) + self.B[i][0]*value
                for i, row in enumerate(self.A)]

    def advance(self, value):
        """One deterministic held-input step, for offline reference/tests."""
        value = number(value, "input", -self.input_limit, self.input_limit)
        if self.done:
            return self.snapshot()
        h = self.dt / self.substeps
        x = list(self.x)
        for _ in range(self.substeps):
            a = self.derivative(x, value)
            b = self.derivative([v+h*q/2 for v, q in zip(x, a)], value)
            c = self.derivative([v+h*q/2 for v, q in zip(x, b)], value)
            d = self.derivative([v+h*q for v, q in zip(x, c)], value)
            x = [v+h*(aa+2*bb+2*cc+dd)/6 for v, aa, bb, cc, dd in zip(x, a, b, c, d)]
            for item in x:
                number(item, "numerical state envelope", -1e8, 1e8)
        self.x = x
        self.index += 1
        self.last_input = value
        return self.snapshot()

    def tick(self, wall_time_s):
        """Use zero input if no command, stale receipt or backwards clock."""
        now = number(wall_time_s, "monotonic tick time", 0)
        backwards = self.last_wall is not None and now < self.last_wall
        self.last_wall = now
        self.stale = (backwards or self.last_receipt is None or
                      now < self.last_receipt or now - self.last_receipt > self.watchdog)
        if backwards:
            self.command, self.last_receipt = 0.0, None
        return self.advance(0.0 if self.stale else self.command)

    def snapshot(self):
        return {"simulation_time_s": self.index*self.dt, "step_index": self.index,
                "state": list(self.x), "output": sum(c*x for c, x in zip(self.C[0], self.x)),
                "applied_input": self.last_input, "input_stale": self.stale,
                "completed": self.done, "dt_s": self.dt,
                "state_order": self.config["state_order"],
                "state_units": self.config["state_units"],
                "input_unit": self.config["input_unit"], "output_unit": self.config["output_unit"],
                "boundary": "selected plant simulation only; no controller or hardware bridge"}
