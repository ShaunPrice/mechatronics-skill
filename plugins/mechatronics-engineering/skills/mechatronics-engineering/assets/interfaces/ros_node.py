"""Original rclpy adapter for a bounded educational plant simulation. MIT."""
import json
from pathlib import Path
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, String

from .sim_core import PlantSimulator


class SimulationNode(Node):
    def __init__(self):
        super().__init__("mechatronics_selected_plant_sim")
        default_path = str(Path(__file__).with_name("plant.json"))
        self.declare_parameter("config", default_path)
        config_path = self.get_parameter("config").value
        with open(config_path, encoding="utf-8") as stream:
            config = json.load(stream)
        self.sim = PlantSimulator(config)
        topic = "/mechatronics_sim/force_n" if config["plant_type"] == "massSpring" else "/mechatronics_sim/input"
        self.state_pub = self.create_publisher(String, "/mechatronics_sim/state", 1)
        self.metadata_pub = self.create_publisher(String, "/mechatronics_sim/metadata", 1)
        self.command_sub = self.create_subscription(Float64, topic, self.on_input, 1)
        self.metadata = json.dumps({"config": config, "input_topic": topic,
                                   "watchdog_clock": "local monotonic receipt time",
                                   "time_semantics": "one fixed simulation dt per timer callback; no catch-up"},
                                  allow_nan=False)
        self.timer = self.create_timer(self.sim.dt, self.on_tick)
        self.metadata_timer = self.create_timer(1.0, self.publish_metadata)
        self.get_logger().info("Simulation only. Input: " + topic + "; state: /mechatronics_sim/state")
        self.publish_metadata()
        self.publish_state(self.sim.snapshot())

    def publish_metadata(self):
        message = String()
        message.data = self.metadata
        self.metadata_pub.publish(message)

    def publish_state(self, state):
        message = String()
        message.data = json.dumps(state, allow_nan=False)
        self.state_pub.publish(message)

    def on_input(self, message):
        if not self.sim.receive(message.data, time.monotonic()):
            self.get_logger().warning("Rejected invalid input; simulation command cleared to zero")

    def on_tick(self):
        try:
            state = self.sim.tick(time.monotonic())
        except ValueError as exc:
            self.timer.cancel()
            self.sim.command, self.sim.last_receipt = 0.0, None
            state = self.sim.snapshot()
            state.update({"fault": str(exc), "stopped": True})
            self.publish_state(state)
            self.get_logger().error("Simulation stopped: " + str(exc))
            return
        self.publish_state(state)
        if state["completed"]:
            self.timer.cancel()
            self.get_logger().info("Configured simulation duration completed; restart node to reset")


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = SimulationNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
