# Installed ROS 2 Jazzy test container

The generated `mechatronics_sim` package was built with colcon and tested through actual ROS 2 topics on **2026-09-15** in a Linux arm64 container on Docker Desktop. The reusable container **`mechatronics-ros2-test` is installed and stopped**. Its source, build, installed package, and test reports remain inside it.

This tests the selected numerical plant and its ROS middleware adapter. It does not test hardware, a robot controller, full browser-graph conversion, or hard real-time operation.

## Start, test, inspect, and stop the installed container

Run these commands on the host with Docker Desktop running:

```sh
docker start mechatronics-ros2-test

docker exec mechatronics-ros2-test bash -lc \
  'source /opt/ros/jazzy/setup.bash && source /workspace/ros2_ws/install/setup.bash && python3 /workspace/test_ros_topics.py --output /workspace/evidence/ros2-topic-test.json'

docker stop --timeout 5 mechatronics-ros2-test
```

The test starts a generated simulator and a separate ROS publisher/subscriber process, checks communication and behavior, and shuts down that simulator process group. The container itself remains running until `docker stop`. A repeat test replaces only the container's previous test report and simulator log.

For an interactive ROS terminal:

```sh
docker start mechatronics-ros2-test
docker exec -it mechatronics-ros2-test bash
```

Inside that terminal:

```sh
source /opt/ros/jazzy/setup.bash
source /workspace/ros2_ws/install/setup.bash
ros2 run mechatronics_sim plant_sim
```

For a second terminal, run another `docker exec -it mechatronics-ros2-test bash`, source both setup files again, then inspect or publish **simulation-only** topics:

```sh
ros2 topic echo /mechatronics_sim/state
ros2 topic echo /mechatronics_sim/metadata
ros2 topic pub --rate 10 /mechatronics_sim/force_n std_msgs/msg/Float64 '{data: 1.0}'
```

Each command above that watches/publishes topics occupies its terminal until interrupted. Stop the command publisher to observe the input watchdog; restart the simulator to reset its initial state. The provided mechanical configuration runs for 20 simulated seconds; it does not automatically repeat. Leave the container stopped after use:

```sh
docker stop --timeout 5 mechatronics-ros2-test
docker inspect mechatronics-ros2-test --format '{{.State.Status}}'
```

Expected stopped status: `exited`. The recorded exit code 143 resulted from the intentional SIGTERM sent to the container's idle `sleep` process, not a failed ROS test.

## Verified checks

The [sanitized middleware report](evidence/ros2-topic-test.json), [colcon output](evidence/colcon-build.log), [simulator log](evidence/plant-simulator.log), and [installation record](evidence/installation.json) retain the evidence.

| Check | Observed result |
|---|---|
| `colcon build --packages-select mechatronics_sim` | One package built successfully; reported total 0.62 s |
| Metadata and state topics | Received from the separate generated simulator process; N input, m output, position/velocity states confirmed |
| 1 N command | 150 received samples carried 1 N; maximum observed position in that phase was 0.281089 m |
| Stop publisher | Applied input became zero and stale; observed 0.507673 s after the last test publish, with a configured 0.5 s receipt watchdog |
| NaN command | Cleared input to zero; observed in 0.009332 s, before ordinary watchdog expiry |
| Out-of-envelope command, 1001 N | Cleared input to zero; observed in 0.008292 s, before ordinary watchdog expiry |
| Suspend/resume simulator | A 0.784475 s received-message wall-time gap produced one 0.01 s simulation step; the monotonic watchdog had expired on resume |
| Timestamp consistency | All 381 received state messages had `simulation_time_s = step_index × dt_s` |

The bounded live test took 5.07 wall seconds and ended at 3.89 simulated seconds. It intentionally terminated the simulator after these checks; it does not claim a live test of the entire configured 20-second run. Recorded message latencies are observations from this container run, not latency guarantees. The configuration embedded in the report retains its original export-time evidence statement; the report's top-level status records this later runtime validation.

The selected model is `m = 1 kg`, `b = 2 N·s/m`, `k = 4 N/m`, zero initial state, `dt = 0.01 s`, watchdog `0.5 s`, numerical input envelope `±1000 N`. This envelope is an educational simulator limit, not an actuator rating.

## Container isolation and installed versions

- Runtime network: `none`; DDS communication was verified between processes inside the same container.
- No published ports, host-folder mounts, host networking, hardware-device mappings, or Docker-socket mount.
- Private IPC, all Linux capabilities dropped, `no-new-privileges`, 128-process limit, 1 GiB memory, and two CPU cores.
- `ROS_DOMAIN_ID=73`, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`, and `ROS_LOCALHOST_ONLY=1`. Jazzy emits a deprecation warning for `ROS_LOCALHOST_ONLY` while explicitly honoring it; runtime isolation is also enforced by Docker's `network=none` setting.
- Python 3.12, `rclpy` 7.1.11, Fast DDS RMW 8.4.4, colcon core 0.21.1. Exact Debian package versions are in the installation record.

The [Dockerfile](Dockerfile) pins the official [ROS image](https://hub.docker.com/_/ros) by its pulled digest. Its build checks/installs colcon and setuptools only inside the Docker image. During the recorded build, those dependencies were already installed; no host package or Docker configuration changed.

## Reproduce from a clean container

Run from this repository's root. The export destination must be new or empty. Check the requested container name first; if it exists, use the reuse commands above or choose a different name throughout these commands. Do not replace an unrelated container.

```sh
docker container inspect mechatronics-ros2-test

python3 -B skills/mechatronics-engineering/scripts/export_interfaces.py \
  --diagram skills/mechatronics-engineering/assets/interfaces/example-diagram.json \
  --plant-node plant --out work/ros2-interface-example

docker build --tag mechatronics-ros2-test:jazzy integrations/ros2-docker

docker create --name mechatronics-ros2-test \
  --label io.mechatronics.role=simulation-test \
  --label io.mechatronics.source=mechatronics-skill \
  --network none --ipc private --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --pids-limit 128 --memory 1g --cpus 2 --init \
  mechatronics-ros2-test:jazzy

docker cp work/ros2-interface-example/ros2_ws \
  mechatronics-ros2-test:/workspace/imported-ros2_ws
docker cp integrations/ros2-docker/test_ros_topics.py \
  mechatronics-ros2-test:/workspace/test_ros_topics.py
docker start mechatronics-ros2-test

docker exec mechatronics-ros2-test bash -lc \
  'cp -R /workspace/imported-ros2_ws /workspace/ros2_ws && source /opt/ros/jazzy/setup.bash && cd /workspace/ros2_ws && colcon build --packages-select mechatronics_sim --event-handlers console_direct+'

docker exec mechatronics-ros2-test bash -lc \
  'source /opt/ros/jazzy/setup.bash && source /workspace/ros2_ws/install/setup.bash && python3 /workspace/test_ros_topics.py --output /workspace/evidence/ros2-topic-test.json'

docker stop --timeout 5 mechatronics-ros2-test
```

The intermediate import directory matters: Docker Desktop preserved host UID 501 in the recorded `docker cp`. Copying that readable source into a new container-owned workspace allowed the capability-restricted container user to build without relaxing isolation or changing host permissions. The `cp -R` build command above is for a **fresh** container where `/workspace/ros2_ws` does not already exist. Use the installed workspace for repeat tests; create a fresh, separately named workspace when changing source.

The pinned base-image contents are fixed by digest. A clean build can still resolve newer colcon/setuptools dependencies if the package repositories change. Review versions and rerun checks after rebuilding; this Dockerfile is not a bit-for-bit frozen apt repository snapshot. Architecture/platforms beyond the recorded Linux arm64 runtime require their own test.

To copy fresh evidence out without a host mount, create a new local destination and use:

```sh
mkdir -p work/ros2-runtime-report
docker cp mechatronics-ros2-test:/workspace/evidence/. work/ros2-runtime-report/
```

## Optional cleanup

These commands delete this installation's container workspace and local derived image. They were **not** run as part of installation, because the container is intended for reuse. Export anything you want to keep first.

```sh
docker stop --timeout 5 mechatronics-ros2-test
docker rm mechatronics-ros2-test
docker image rm mechatronics-ros2-test:jazzy
```

The official `ros:jazzy-ros-base` image is retained by those commands because other projects may reuse it.
