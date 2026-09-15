#!/usr/bin/env python3
"""Live ROS 2 middleware test of the generated simulation package, not hardware.

Run inside the isolated container after sourcing ROS and the built workspace.
Starts the simulator as a separate process group and exchanges actual DDS topics.
"""
import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, String


class Probe(Node):
    def __init__(self):
        super().__init__("mechatronics_container_validation")
        self.states = []
        self.metadata = []
        self.state_sub = self.create_subscription(String, "/mechatronics_sim/state", self.state, 100)
        self.meta_sub = self.create_subscription(String, "/mechatronics_sim/metadata", self.meta, 10)
        self.command = self.create_publisher(Float64, "/mechatronics_sim/force_n", 1)

    def state(self, message):
        self.states.append({"received_monotonic_s": time.monotonic(), "sample": json.loads(message.data)})

    def meta(self, message):
        self.metadata.append(json.loads(message.data))

    def publish(self, value):
        message = Float64()
        message.data = float(value)
        self.command.publish(message)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def spin_until(probe, predicate, timeout, message):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        rclpy.spin_once(probe, timeout_sec=.01)
        if predicate():
            return
    raise AssertionError(message)


def spin_for(probe, seconds, command=None):
    end = time.monotonic() + seconds
    last_publish = -math.inf
    while time.monotonic() < end:
        if command is not None and time.monotonic()-last_publish >= .05:
            probe.publish(command)
            last_publish = time.monotonic()
        rclpy.spin_once(probe, timeout_sec=.01)
    return last_publish


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="/workspace/evidence/ros2-topic-test.json")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {"schema": "mechatronics-ros2-runtime-validation/v1", "status": "running",
              "evidence": "Actual ROS 2 topics and generated numerical plant inside a Docker container; no hardware, external robot, or hard-real-time validation",
              "process_model": "Probe and generated simulator are separate processes using ROS middleware",
              "checks": {}, "environment": {key: os.environ.get(key) for key in
                  ("ROS_DISTRO", "ROS_DOMAIN_ID", "ROS_LOCALHOST_ONLY", "RMW_IMPLEMENTATION")}}
    rclpy.init()
    probe = Probe()
    process = None
    paused = False
    started = time.monotonic()
    log_path = output.with_name("plant-simulator.log")
    try:
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(["ros2", "run", "mechatronics_sim", "plant_sim"],
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            spin_until(probe, lambda: bool(probe.metadata) and len(probe.states) >= 3, 8,
                       "Did not receive both simulator metadata and state topics")
            metadata = probe.metadata[-1]
            config = metadata["config"]
            require(config["plant_type"] == "massSpring", "This runtime test expects the mechanical example")
            require(metadata["input_topic"] == "/mechatronics_sim/force_n", "Unexpected command topic")
            require(config["input_unit"] == "N" and config["output_unit"] == "m", "Missing mechanical units")
            require(config["state_order"] == ["position", "velocity"], "Unexpected state ordering")
            require("local monotonic" in metadata["watchdog_clock"], "Watchdog clock semantics missing")
            require("no catch-up" in metadata["time_semantics"], "Fixed simulation clock semantics missing")
            report["checks"]["metadata_and_state_received"] = {
                "input_topic": metadata["input_topic"], "input_unit": config["input_unit"],
                "output_unit": config["output_unit"], "state_order": config["state_order"],
                "watchdog_s": config["watchdog_s"], "dt_s": config["dt_s"]}

            phase_start = len(probe.states)
            last_publish = spin_for(probe, 1.5, command=1.0)
            driven = [r for r in probe.states[phase_start:] if r["sample"]["applied_input"] == 1.0]
            require(len(driven) >= 10, "1 N command did not reach the simulation")
            require(max(r["sample"]["output"] for r in driven) > .01, "1 N did not produce positive position")
            report["checks"]["one_newton_moves_positive"] = {
                "samples_with_1N": len(driven), "maximum_position_m": max(r["sample"]["output"] for r in driven)}

            stopped_at = time.monotonic()
            phase_start = len(probe.states)
            spin_until(probe, lambda: any(r["sample"]["input_stale"] and r["sample"]["applied_input"] == 0
                                         for r in probe.states[phase_start:]), config["watchdog_s"]+1.5,
                       "Stopping publisher did not clear stale input")
            zero = next(r for r in probe.states[phase_start:]
                        if r["sample"]["input_stale"] and r["sample"]["applied_input"] == 0)
            report["checks"]["publisher_stop_watchdog"] = {
                "zero_seen_after_last_publish_wall_s": zero["received_monotonic_s"]-last_publish,
                "zero_seen_after_publish_loop_stop_wall_s": zero["received_monotonic_s"]-stopped_at,
                "sample": zero["sample"]}

            def invalid_command_case(value, name):
                spin_for(probe, .3, command=.75)
                require(probe.states[-1]["sample"]["applied_input"] == .75, "Valid command did not recover before invalid-input test")
                index = len(probe.states)
                sent = time.monotonic()
                probe.publish(value)
                timeout = min(.35, config["watchdog_s"]*.7)
                spin_until(probe, lambda: any(r["sample"]["input_stale"] and r["sample"]["applied_input"] == 0
                                             for r in probe.states[index:]), timeout,
                           "Invalid input was not cleared before the ordinary watchdog expiry")
                rejected = next(r for r in probe.states[index:] if r["sample"]["input_stale"] and r["sample"]["applied_input"] == 0)
                report["checks"][name] = {"invalid_command": "NaN" if math.isnan(value) else value,
                    "zero_observed_latency_wall_s": rejected["received_monotonic_s"]-sent,
                    "bounded_before_watchdog_s": timeout, "applied_input": rejected["sample"]["applied_input"]}

            invalid_command_case(float("nan"), "nonfinite_command_clears_input")
            invalid_command_case(config["input_limit"]+1, "out_of_envelope_command_clears_input")

            # Pause only the simulator process group. The probe's wall clock keeps running.
            spin_for(probe, .3, command=1.0)
            os.killpg(process.pid, signal.SIGSTOP)
            paused = True
            spin_for(probe, .08)  # Drain any already-sent state message.
            before = probe.states[-1]
            spin_for(probe, .7)
            resume_index = len(probe.states)
            os.killpg(process.pid, signal.SIGCONT)
            paused = False
            spin_until(probe, lambda: len(probe.states) > resume_index, 2, "No state after resuming simulator")
            after = probe.states[resume_index]
            sim_gap = after["sample"]["simulation_time_s"]-before["sample"]["simulation_time_s"]
            wall_gap = after["received_monotonic_s"]-before["received_monotonic_s"]
            require(wall_gap > .65, "Pause did not establish a wall-time gap")
            require(0 < sim_gap <= config["dt_s"]*3.01, "Simulation caught up by a large elapsed-wall interval")
            require(after["sample"]["applied_input"] == 0 and after["sample"]["input_stale"],
                    "Monotonic watchdog did not expire across simulator pause")
            report["checks"]["simulation_clock_separate_from_wall"] = {
                "received_wall_gap_s": wall_gap, "simulation_gap_s": sim_gap,
                "dt_s": config["dt_s"], "resume_applied_input": after["sample"]["applied_input"],
                "note": "The numerical clock advanced by fixed callbacks; middleware scheduling and hard real-time behavior are not guaranteed."}

            require(all(abs(row["sample"]["simulation_time_s"]-row["sample"]["step_index"]*config["dt_s"]) < 1e-10
                        for row in probe.states), "Simulation timestamps are not integer step index × dt")
            report["checks"]["integer_sample_timestamps"] = {"received_states_checked": len(probe.states)}
            report["status"] = "passed"
            report["configuration"] = config
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = type(exc).__name__+": "+str(exc)
        raise
    finally:
        if process is not None and process.poll() is None:
            if paused:
                os.killpg(process.pid, signal.SIGCONT)
            os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=2)
        report["elapsed_wall_s"] = time.monotonic()-started
        report["received_state_count"] = len(probe.states)
        report["received_metadata_count"] = len(probe.metadata)
        report["last_received_state"] = probe.states[-1]["sample"] if probe.states else None
        output.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        probe.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        print(json.dumps({"status": report["status"], "checks": list(report["checks"]),
                          "report": str(output), "elapsed_wall_s": report["elapsed_wall_s"]}, indent=2))


if __name__ == "__main__":
    main()
