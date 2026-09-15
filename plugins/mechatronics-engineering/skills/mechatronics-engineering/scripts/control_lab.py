#!/usr/bin/env python3
"""Sampled PID/continuous plant teaching lab. Python 3.9+ standard library only."""
import argparse
import csv
import json
import math
from pathlib import Path


def rk4_step(x, v, force, dt, mass, damping, stiffness):
    """Integrate m*x'' + b*x' + k*x = force, with force held over this step."""
    def f(px, pv):
        return pv, (force-damping*pv-stiffness*px)/mass
    a = f(x, v)
    b = f(x+dt*a[0]/2, v+dt*a[1]/2)
    c = f(x+dt*b[0]/2, v+dt*b[1]/2)
    d = f(x+dt*c[0], v+dt*c[1])
    return (x+dt*(a[0]+2*b[0]+2*c[0]+d[0])/6,
            v+dt*(a[1]+2*b[1]+2*c[1]+d[1])/6)


class PID:
    """Parallel PID, derivative on measured position, conditional antiwindup."""
    def __init__(self, kp=80.0, ki=40.0, kd=12.0, limit=10.0, tau=0.02):
        for name, value in (("kp", kp), ("ki", ki), ("kd", kd), ("limit", limit), ("tau", tau)):
            if not math.isfinite(value) or value < 0 or (name == "limit" and value == 0):
                raise ValueError(f"invalid {name}")
        self.kp, self.ki, self.kd, self.limit, self.tau = kp, ki, kd, limit, tau
        self.integral = 0.0
        self.previous = None
        self.derivative = 0.0

    def update(self, target, measured, dt):
        if not all(math.isfinite(z) for z in (target, measured, dt)) or dt <= 0:
            raise ValueError("finite target/measurement and positive sample interval required")
        error = target-measured
        raw_d = 0.0 if self.previous is None else (measured-self.previous)/dt
        alpha = dt/(self.tau+dt)
        self.derivative += alpha*(raw_d-self.derivative)
        self.previous = measured
        candidate_i = self.integral+self.ki*error*dt
        candidate_u = self.kp*error+candidate_i-self.kd*self.derivative
        # Retain integration when unsaturated or when the error unwinds saturation.
        if abs(candidate_u) <= self.limit or candidate_u*error < 0:
            self.integral = candidate_i
        output = self.kp*error+self.integral-self.kd*self.derivative
        return max(-self.limit, min(self.limit, output))


def simulate(sample_s=0.01, substeps=10, duration_s=8.0):
    if not math.isfinite(sample_s) or sample_s <= 0 or not math.isfinite(duration_s) or duration_s <= 4:
        raise ValueError("positive sample time and duration over 4 s required")
    if not isinstance(substeps, int) or substeps < 1:
        raise ValueError("substeps must be a positive integer")
    count = round(duration_s/sample_s)
    if count > 1000000 or count < 2 or abs(count*sample_s-duration_s) > 1e-9:
        raise ValueError("duration must contain an integer number of samples, at most one million")
    mass, damping, stiffness = 1.0, 2.0, 20.0
    x = v = xo = vo = 0.0
    pid = PID()
    rows = []
    for i in range(count+1):
        t = i*sample_s
        target = 0.1 if t >= 0.5-1e-12 else 0.0
        disturbance = -1.0 if t >= 4.0-1e-12 else 0.0
        force = pid.update(target, x, sample_s)
        rows.append({"time_s": t, "reference_m": target, "closed_loop_m": x,
                     "open_loop_m": xo, "velocity_m_s": v, "control_force_n": force,
                     "disturbance_n": disturbance})
        if i == count:
            break
        for _ in range(substeps):
            h = sample_s/substeps
            x, v = rk4_step(x, v, force+disturbance, h, mass, damping, stiffness)
            xo, vo = rk4_step(xo, vo, stiffness*target+disturbance, h, mass, damping, stiffness)
    tracked = [r for r in rows if r["time_s"] >= 0.5]
    metrics = {"evidence": "simulated; no physical hardware tested",
               "parameters": {"mass_kg": mass, "damping_n_s_per_m": damping, "stiffness_n_per_m": stiffness,
                              "sample_s": sample_s, "plant_substeps": substeps, "duration_s": duration_s,
                              "kp_n_per_m": 80, "ki_n_per_m_s": 40, "kd_n_s_per_m": 12,
                              "derivative_filter_tau_s": 0.02, "force_limit_n": 10},
               "final_error_m": rows[-1]["reference_m"]-x,
               "final_open_loop_error_m": rows[-1]["reference_m"]-xo,
               "tracking_rmse_m": math.sqrt(sum((r["reference_m"]-r["closed_loop_m"])**2 for r in tracked)/len(tracked)),
               "peak_abs_command_n": max(abs(r["control_force_n"]) for r in rows),
               "saturation_fraction_of_intervals": sum(abs(r["control_force_n"]) >= 10-1e-12 for r in rows[:-1])/count}
    return rows, metrics


def frequency_response():
    rows = []
    for i in range(161):
        hz = 10**(-2+4*i/160)
        omega = 2*math.pi*hz
        h = 1/complex(20-omega**2, 2*omega)
        rows.append({"frequency_hz": hz, "omega_rad_s": omega,
                     "magnitude_db_re_1_m_per_n": 20*math.log10(abs(h)),
                     "phase_deg": math.degrees(math.atan2(h.imag, h.real))})
    return rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def write_html(path, rows, metrics):
    # Data is numeric, generated locally; no external assets or dependencies.
    payload = json.dumps({"rows": rows, "metrics": metrics}, allow_nan=False)
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mechatronics control lab</title><style>body{font:17px system-ui;max-width:1100px;margin:36px auto;padding:0 20px;background:#f4f6fa;color:#16253a}h1{margin-bottom:8px}section{background:white;padding:22px;margin:22px 0;border-radius:12px}svg{width:100%;height:auto}label{display:inline-block;margin:8px 20px 8px 0}pre{white-space:pre-wrap;font-size:14px}.note{color:#41536a}line{stroke:#d5dde7}text{font:14px system-ui;fill:#41536a}</style>
<h1>Sampled control, visible results</h1><p>Mass–spring–damper position control. Educational simulation; no hardware validation.</p>
<section><h2>Position versus time</h2><p class="note">Reference steps to 0.1 m at 0.5 s. A −1 N disturbance starts at 4 s. The open-loop baseline applies force k × reference. The sampled PID uses measured feedback.</p>
<div id="toggles"></div><svg id="plot" viewBox="0 0 1000 390" role="img" aria-label="Position in metres against time in seconds"></svg></section>
<section><h2>Force command</h2><svg id="force" viewBox="0 0 1000 390" role="img" aria-label="Control force and disturbance in newtons against time"></svg></section>
<section><h2>Metrics and reproducibility</h2><p>CSV files contain the raw traces and plant Bode data. Plant frequency response alone does not establish closed-loop stability margins. The trace omits noise, backlash, delay beyond sampling, temperature and unmodelled structural modes.</p><pre id="metrics"></pre></section>
<script>const data=PAYLOAD; const colors=['#6b7280','#006fc4','#c26000'];const series=['reference_m','closed_loop_m','open_loop_m'];const labels=['Reference','Closed loop PID','Open loop'];
function chart(id,keys,cols,unit){const svg=document.getElementById(id),rows=data.rows;let vals=rows.flatMap(r=>keys.map(k=>r[k])),lo=Math.min(...vals),hi=Math.max(...vals);const pad=Math.max((hi-lo)*.1,.005);lo-=pad;hi+=pad;let out='';for(let i=0;i<=5;i++){const yy=30+i*58,v=hi-(hi-lo)*i/5;out+=`<line x1="85" y1="${yy}" x2="970" y2="${yy}"/><text x="3" y="${yy+5}">${v.toFixed(3)}</text>`;}for(let i=0;i<=8;i++){let xx=85+i*885/8,t=rows.at(-1).time_s*i/8;out+=`<text x="${xx-6}" y="349">${t.toFixed(1)}</text>`;}out+=`<text x="470" y="379">Time (s)</text><text x="85" y="18">${unit}</text>`;keys.forEach((k,j)=>{const p=rows.map(r=>`${85+r.time_s/rows.at(-1).time_s*885},${30+(hi-r[k])/(hi-lo)*290}`).join(' ');out+=`<polyline data-key="${k}" fill="none" stroke="${cols[j]}" stroke-width="2.4" points="${p}"/>`;});svg.innerHTML=out;}
chart('plot',series,colors,'Position (m)');chart('force',['control_force_n','disturbance_n'],['#006fc4','#c26000'],'Force (N): blue = command; orange = disturbance');document.getElementById('metrics').textContent=JSON.stringify(data.metrics,null,2);series.forEach((k,i)=>{const l=document.createElement('label');l.style.color=colors[i];const c=document.createElement('input');c.type='checkbox';c.checked=true;c.onchange=()=>document.querySelector(`[data-key="${k}"]`).style.display=c.checked?'':'none';l.append(c,document.createTextNode(' '+labels[i]));document.getElementById('toggles').append(l);});</script></html>'''
    path.write_text(page.replace("PAYLOAD", payload), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="directory for CSV/JSON/HTML teaching results")
    parser.add_argument("--sample-s", type=float, default=0.01)
    parser.add_argument("--substeps", type=int, default=10)
    args = parser.parse_args()
    rows, metrics = simulate(args.sample_s, args.substeps)
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out/"step-response.csv", rows)
    write_csv(args.out/"plant-bode.csv", frequency_response())
    (args.out/"metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    write_html(args.out/"control-lab.html", rows, metrics)
    print(json.dumps(metrics, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
