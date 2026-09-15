# Actuation, instrumentation, electronics and embedded control

Use this guide to turn force/motion/measurement requirements into parts, circuits, interfaces and firmware. Start from the load and signal budget, then select hardware. A product family name is not a verified part specification.

## Actuator selection and sizing

| Technology | Good fit and selection inputs | Design outputs and checks |
|---|---|---|
| Brushed DC motor | Simple variable speed, moderate cost; torque-speed curve, voltage, duty | H-bridge, encoder, brush life, EMI, stall/continuous current and thermal limits |
| BLDC/PMSM servo | Efficient speed/torque/position control; inertia, bandwidth, feedback | Matched inverter, commutation/FOC configuration, current loop and thermal model; motor phase versus supply current differ |
| Stepper | Predictable incremental motion at suitable load/speed | Torque-speed margin, driver current, microstepping, acceleration limits, homing; microstep resolution is not accuracy and steps can be lost |
| Linear motor, voice coil | Direct force, high dynamics, short or long travel by design | Force constant, stroke, bearing/guide and cooling; power-loss behaviour |
| Solenoid | On/off movement or holding at short stroke | Force versus gap, inrush/hold duty, return spring, flyback/release time |
| Piezoelectric | Fine displacement and fast small motion | High-voltage driver, hysteresis/creep, preload, travel and feedback |
| Pneumatic | Fast compliant motion, available compressed air | Cylinder bore, pressure/flow, valve response, exhaust/noise, compressibility and fail state |
| Hydraulic | High force/power density | Pressure, flow, load-holding valves, leakage, contamination, fluid compatibility and stored pressure |
| Shape-memory/soft actuator | Compliant or unusual form factor | Thermal/time hysteresis, fatigue, force and cycle-rate limits; characterize experimentally |

For a wheel, required tangential force includes acceleration, rolling resistance, grade and drag. At each driven wheel, shaft torque is force × radius; do not assume equal sharing on uneven ground. For a screw with lead p (m/rev), torque approximately F p/(2π η) under the stated efficiency η, plus rotational acceleration and friction. Check buckling, critical speed, backdriving, support bearings and holding arrangements. Gear reductions multiply torque with efficiency and divide speed; reflect load inertia by the square of reduction ratio. RMS torque is useful for thermal comparison only with a justified motor thermal/duty model; peak torque and driver limits still apply.

Output a selection sheet with peak/continuous loads, operating curve, cooling, duty cycle, gear ratio, backlash/compliance, brake, encoder and actual driver compatibility. An oversized motor may increase inertia and cost; a small motor may meet peak torque briefly but fail thermally.

### Gravity loads and overhead mechanisms

For a lifted mass, m g is only its weight. Linkage leverage, actuator angle, moving hardware, acceleration, friction and dynamic events determine actuator force. A voltage label and payload do not justify a force rating or current-limit percentage. Verify current-to-force behaviour, drive limits, duty/thermal data, load path, rated holding mechanism and applicable lifting/application requirements. Self-locking must be established for the actual drive under wear/vibration and all relevant conditions; do not assume it from “worm” or “lead screw”.

If a user proposes defeating a limit to cure wobble, keep the limits and separate structural modes, feedback underdamping, backlash and limit cycles through measurements. Offer calculations and a supported/isolated bench plan. Do not prescribe new operational gains or current limits without the plant and rating data. Treat waveform/frequency clues as competing hypotheses rather than a unique diagnosis. Structural vibration can sometimes be reduced by input shaping, notch filtering or active damping, but those require a validated model and suitable sensing/actuation; they do not repair an inadequate load path. Observe without touching moving or energised equipment; touching/bump tests require isolation and independently supported loads. A brake, catch or secondary retention is an engineered system; do not direct a novice to improvise it or infer a legal requirement without the applicable source. For power-loss/backdrive tests, first independently support/restrain the load and exclude people from the fall/crush zone.

## Instrumentation: from physical quantity to trustworthy number

Design the full chain: measurand → transducer → excitation/conditioning → anti-alias filter → ADC/timestamp → calibration → estimate → control decision. Set required range, uncertainty, bandwidth, latency, drift, environmental compatibility and failure detection. Use an error budget; bit count alone says little about accuracy.

| Quantity / device family | When to use | Common failure and useful test |
|---|---|---|
| Incremental/absolute encoder, resolver | Rotation/position; choose reference and power-loss needs | Missed counts, eccentricity, wrong quadrature scaling; rotate a known angle and compare independent reference |
| Potentiometer, inductive/LVDT, magnetic/Hall | Linear/rotary displacement or current | Wear, temperature or magnetic interference; multi-point calibration in both directions |
| Strain bridge, load cell, force/torque transducer | Contact force, weighing, structural load | Mounting strain, creep, cross-axis sensitivity; known loads with uncertainty and overload protection |
| Thermocouple, RTD, thermistor, IR | Temperature over suitable range/time constant | Cold-junction/lead resistance/emissivity/self-heating; compare at several known conditions |
| IMU: gyro/accelerometer/magnetometer | Attitude and short-term motion sensing | Bias, vibration, time skew and magnetic disturbance; stationary, multi-orientation and dynamic calibration |
| Camera/stereo/ToF/event camera | Geometry, inspection or high-speed events | Lighting, rolling shutter, reflective surfaces, calibration and motion blur; test operating scenes |
| LiDAR/radar/ultrasonic | Ranging and obstacle perception | Reflectivity, multipath, weather, minimum range; test difficult targets and occlusions |
| GNSS/RTK, UWB, visual-inertial or acoustic localisation | Position relative to global/local infrastructure | Multipath, outages, false precision; record covariance/quality, ground truth and dropout response |
| Pressure, flow, depth, leak, gas and chemical sensors | Fluids, underwater systems, process monitoring | Fouling, hysteresis, temperature compensation; traceable pressure/flow references and leak tests |
| Tactile, proximity, capacitive, fibre-optic, vibration/acoustic sensors | Manipulation, condition monitoring or special environments | Mounting sensitivity, contamination, bandwidth and conditioning; mission-specific test fixture |

Calibrate with model y = a x + b only if a linear relationship is justified; use residuals to select a better model when needed. Record reference uncertainty, coefficients, date, temperature, range and recalibration trigger. Separate repeatability, bias correction and uncertainty. For multiple sensors, align frames and timestamps before fusion; a better filter cannot repair a wrong frame or stale packet.

## Analog, digital and power electronics

**Analog:** use Ohm/Kirchhoff laws to check ranges and loading. Design op-amp signal conditioning for input common-mode range, output swing, gain-bandwidth, stability, offset, noise and power rails. Use differential or instrumentation amplifiers for small bridge signals. Select RC/active filters from useful signal and disturbance spectra; filtering after an ADC cannot undo aliasing already acquired. Check ADC acquisition time against source impedance, reference quality and effective number of bits. Include DAC settling, impedance matching where relevant and grounding/return-current paths.

Example: an ideal 12-bit ADC spanning 3.3 V has about 3.3/4096 = 0.806 mV per code. At a sensor sensitivity of 10 mV/N, ideal quantisation is about 0.0806 N/code. This excludes reference error, noise, gain error, drift and mechanical effects; it does not establish 0.08 N measurement accuracy.

**Digital:** verify VIH/VIL thresholds, absolute maximum ratings, pull-ups, drive strength, fanout and rise time. Open-drain and push-pull outputs are different. Document reset/boot strapping pins and power sequencing. Use debounce/edge capture for switches and timers for encoders/PWM; avoid timing control by arbitrary blocking delays. Consider metastability for asynchronous inputs and synchronisers; a software read is not an FPGA clock-domain crossing strategy.

**Power:** derive average/peak power and transient current from the mission. Choose conversion topology, efficiency, switch/inductor/capacitor ratings, ripple and thermal path. Design fuse/protection coordination, reverse-polarity handling, transient suppression, inrush, grounding and cable/connector ratings. A bench supply's current limit does not replace fault protection in a final product. Inductive loads need a verified flyback/clamp path; a diode may slow release. Regeneration can raise a DC bus above its rating if the supply cannot absorb energy. Account for battery BMS disconnect during regeneration.

**Motor drives:** match voltage/current, switching frequency, gate drive, dead time, shoot-through protection and current sensing. Estimate conduction/switching loss and temperature rise under real cooling. Keep high-current commutation loops small; protect sensitive measurements from switching return currents. Follow the actual driver's datasheet and layout guide; firmware current limits do not establish short-circuit interruption capability.

**PCB and harness deliverables:** schematic, ERC/DRC report, layout/stackup constraints, assembly drawings, Gerber/drill or fabricator-supported exports, BOM/approved alternates, pick-and-place, harness lengths/pin-to-pin map, test points, test procedure and revisions. Creepage/clearance, isolation and protective-earth requirements depend on voltage, environment and applicable product rules; determine those inputs and use the actual standard.

## Communications and radio

Choose I²C/SPI for suitable board-level links, UART for simple point-to-point, CAN/CAN FD or RS-485 for suitable robust networks, industrial Ethernet/fieldbus where synchronization and tooling justify them, and USB/Ethernet for higher throughput. Verify cable length, termination, common-mode voltage, isolation, topology and connector pinouts. Protocol names do not establish wire compatibility.

For wireless, define range/environment, data rate, latency/outage tolerance, energy and regional spectrum requirements before choosing BLE/Wi-Fi/LoRa/cellular or proprietary radio. A link budget includes transmitter power, antenna gains, losses, receiver sensitivity and fading margin. Bench range is not field range; antennas are affected by enclosures, water, carbon fibre and nearby metal. Wired or autonomous local control may be necessary when radio loses service. Set command authentication, freshness, bounded authority and a local response to disconnect. Verify current radio/product obligations for the sales jurisdiction through [sources](sources.md).

## MCU, RTOS, SBC, PLC and FPGA

| Compute choice | Select when | Required evidence |
|---|---|---|
| Bare-metal microcontroller | Small deterministic loop, local I/O, low energy | Timer/interrupt schedule, worst-case execution time, watchdog, stack/memory bounds |
| MCU + RTOS | Multiple concurrent timing tasks | Priorities, deadlines, mutex/priority inversion design, task monitoring and load test |
| SBC/Linux computer | Vision, planning, UI, networking | Measured latency/resource bounds, process restart, storage robustness and interface to local control |
| PLC/industrial motion controller | Maintainability, industrial I/O and established machine support | Cycle time, program/config backup, hardware environment and suitable protective architecture |
| FPGA/SoC | Parallel high-rate I/O/DSP, precise timing, custom interfaces | HDL simulation, synthesis, timing closure, clock/reset domain analysis and board tests |

Choose FPGA after a measured bottleneck justifies development/verification cost. Document fixed-point scaling, rounding, overflow, coefficient quantisation and numeric error versus a reference model. A successful bitstream build is not successful timing closure or hardware validation.

For firmware, define a state machine: boot/self-test, disabled, homing/calibration as needed, ready, active, stopping, latched fault, recovery. Fault recovery must not unexpectedly restart motion. Include parameter validation, brownout behaviour, watchdog cause logging, sensor plausibility/freshness and version reporting. Protect update credentials; record secure boot/update/rollback design for connected products. Deliver a build command/toolchain, pin map, timing table, configuration schema, logs, unit/interface tests and a staged board test. Never invent a device's pinout from a similar board.

Further authoritative starting points: [ROS interface and QoS documentation, NIST measurement guidance, and device documentation sources](sources.md).
