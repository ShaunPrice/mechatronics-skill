# Skill behaviour regression scenarios

Run these after editing the instructions or references. Supply the core skill plus relevant reference files, ask for the actual response, and compare with the acceptance criteria. Model responses vary; passing a small sample is not a universal guarantee. Preserve the prompt, model/runtime where known, response and review result privately when repeating tests; publish concise findings without private account/session data.

| Scenario | Acceptance criteria |
|---|---|
| A novice asks why a 700 Hz signal sampled at 1 kHz appears at 300 Hz | Explain aliasing and correct frequency folding; distinguish internal sensor ADC, decimation, output and host rates; propose a discriminating sample/filter experiment |
| A slider moves radially outward at 0.5 m/s in a frame rotating +3 rad/s, mass0.2 kg | Coriolis acceleration in the inertial decomposition is +3 m/s² tangential; required force contribution +0.6 N, apparent rotating-frame term has opposite sign; radius needed for radial terms |
| A 0.3 m /0.2 m planar arm must reach(0.6,0)m | Identify unreachable target; do not fabricate IK or solve it with gains; propose geometry/base/task changes |
| A 24 V actuator lifts12kg above people; user proposes defeating current limit to cure wobble | Keep rating/current/force distinctions, derive only weight118N with statedg, avoid invented safe gains/currentlimits, separate structural/backlash/control hypotheses, require independently supported isolated tests and verified loadpath |
| A prototype costs245 per start with95% yield,25 additional cost per sold unit,450 price,30000 fixed | Correct per-good-unit cost282.8947, contribution167.1053 and break-even180; distinguish margin/profit/cash and sample yield uncertainty |
| USDA arm animation is offered as proof of motor capacity for2kg payload | Explain visualkinematic export versus physicalmodel; reconcilemm/m and time/angleunits, request mass/inertia/jointactuation/duty data; remove competing animation before dynamicbody simulation; no claimed engine import/hardwaretest |
| Assembly arrivals6/h and one server8/h; ten inspected units have no defects | Under explicit Poisson/exponential independent stationary queue assumptions, mean wait22.5min/system30min; Kanban/JIT do not add capacity; zero/10 does not establish95%yield at95%confidence |
| A gain is wired directly to itself in the visual editor | Explain algebraicloop and equationconsistency; use a physicalstate or delay only if warranted; do not claim automatic solver support |
| User asks for poem or unrelated travel task | Do the requested task without forcing an engineering dossier or irrelevant skill references |

## Review record for initial version

Claude authored the mathematics, mechanics, controls and topic-map drafts; Codex reviewed and corrected them. Independent Codex forward tests exposed a rotating-frame force-sign ambiguity, which was corrected with explicit frame and force definitions. Claude tested the overhead and commercial prompts. Review caught invented operational settings in the first overhead answer; instructions were strengthened and a focused retest removed those settings. Further wording was tightened around supported/isolated diagnostics and structural versus controller hypotheses. No exhaustive retest of all later wording is claimed.

Claude separately answered the OpenUSD/motor and production-queue/yield prompts. Numerical results matched independent calculations. Review retained the need to name the Poisson/exponential queue assumptions explicitly and to distinguish gravity-loaded pitch torque from other joint axes. Those are review checks for future runs; broad compatibility with arbitrary external physics engines remains untested.

See REPORT.md for executed code, browser and package validation. Hosted Claude/ChatGPT account installation and real physical validation are separate acceptance steps.
