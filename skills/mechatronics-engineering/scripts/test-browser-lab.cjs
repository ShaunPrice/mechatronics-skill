#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const M=require('../assets/browser-lab/math.js');
const USD=require('../assets/browser-lab/usd.js');
let passed=0;
function test(name,fn){fn();passed++;process.stdout.write(`PASS ${name}\n`);}
function close(actual,expected,tolerance=1e-8){assert.ok(Math.abs(actual-expected)<=tolerance,`${actual} differs from ${expected} by more than ${tolerance}`);}
function residual(coeff,r){const scale=coeff.reduce((sum,c,i)=>sum+Math.abs(c)*Math.pow(Math.max(1,M.abs(r)),coeff.length-i-1),0);return M.abs(M.evaluate(coeff,r))/Math.max(1,scale);}
test('analytic real, complex and badly scaled quadratic roots',()=>{
  const real=M.polynomialRoots([1,3,2]).map(r=>r.re).sort((a,b)=>a-b);close(real[0],-2);close(real[1],-1);
  const complex=M.polynomialRoots([1,0,4]);complex.forEach(r=>{close(r.re,0);close(Math.abs(r.im),2);});
  M.polynomialRoots([1,1e8,1]).forEach(r=>assert.ok(residual([1,1e8,1],r)<1e-12));
});
test('cubic and quartic known roots and residuals',()=>{
  const cubic=M.polynomialRoots([1,6,11,6]).map(r=>r.re).sort((a,b)=>a-b);[-3,-2,-1].forEach((v,i)=>close(cubic[i],v));
  const quartic=M.polynomialRoots([1,0,0,0,1]);quartic.forEach(r=>{close(Math.abs(r.re),Math.SQRT1_2);close(Math.abs(r.im),Math.SQRT1_2);assert.ok(residual([1,0,0,0,1],r)<1e-12);});
  M.polynomialRoots([1,4,6,4,1]).forEach(r=>{close(r.re,-1,.001);close(r.im,0,.001);assert.ok(residual([1,4,6,4,1],r)<1e-12);});
  assert.deepEqual(M.polynomialRoots([1,0,0,0,0]),Array.from({length:4},()=>({re:0,im:0})));
});
test('absent integral and derivative states cancel before root solving',()=>{
  const p={...M.defaults};assert.equal(M.characteristic(p).length,5);
  assert.equal(M.characteristic({...p,ki:0}).length,4);
  assert.equal(M.characteristic({...p,kd:0}).length,4);
  assert.equal(M.characteristic({...p,ki:0,kd:0}).length,3);
  assert.deepEqual(M.characteristic({...p,ki:0,kd:0}),[p.m,p.b,p.k+p.g*p.kp]);
  assert.deepEqual(M.characteristic({...p,ki:0,kd:0,kp:0}),[p.m,p.b,p.k]);
  assert.deepEqual(M.characteristic({...p,kd:0,tf:5}),M.characteristic({...p,kd:0,tf:.001}));
});
test('full filtered PID characteristic coefficients follow D + g N',()=>{
  const p={...M.defaults};const expected=[p.m*p.tf,p.m+p.b*p.tf,p.b+p.k*p.tf+p.g*(p.kp*p.tf+p.kd),p.k+p.g*(p.kp+p.ki*p.tf),p.g*p.ki];
  M.characteristic(p).forEach((v,i)=>close(v,expected[i]));
  [0,.01,.2,1,5,20].forEach(g=>{const coeff=M.characteristic(p,g),roots=M.poles(p,g);roots.forEach(r=>{assert.ok(residual(coeff,r)<1e-10);if(Math.abs(r.im)>1e-7)assert.ok(roots.some(q=>Math.abs(q.re-r.re)<1e-6&&Math.abs(q.im+r.im)<1e-6));});});
});
test('root locus uses fixed controller shape and marks actual current gain',()=>{
  const p={...M.defaults,g:3,locusMax:8},data=M.rootLocus(p,41);assert.equal(data.rows.length,41);close(data.rows[0].g,0);close(data.rows.at(-1).g,8);assert.deepEqual(data.current,M.poles(p,3));
  data.rows.forEach(row=>row.poles.forEach(r=>assert.ok(residual(M.characteristic(p,row.g),r)<1e-10)));
});
test('dimensionless full loop frequency response and conjugate symmetry',()=>{
  const p={...M.defaults,kp:2,ki:0,kd:0,g:3,m:1,b:2,k:4};
  const z=M.loop(p,2);close(z.re,0);close(z.im,-1.5);
  const q={...M.defaults};[.01,.1,1,10,100].forEach(w=>{const plus=M.loop(q,w),minus=M.loop(q,-w);close(plus.re,minus.re);close(plus.im,-minus.im);});
  const f=M.frequency(q);assert.equal(f.length,600);for(let i=1;i<f.length;i++)assert.ok(Math.abs(f[i].phase-f[i-1].phase)<=180);
});
test('finite margin estimates preserve missing and multiple crossings',()=>{
  const zero=M.margins(M.frequency({...M.defaults,g:0}));assert.equal(zero.gainCrossings.length,0);assert.equal(zero.phaseCrossings.length,0);
  const fixture=[{omega:1,magnitude:10,phase:-100},{omega:10,magnitude:-10,phase:-200},{omega:100,magnitude:10,phase:-160},{omega:1000,magnitude:-10,phase:-220}];
  const margins=M.margins(fixture);assert.equal(margins.gainCrossings.length,3);assert.equal(margins.phaseCrossings.length,3);close(margins.gainCrossings[0].omega,Math.sqrt(10));close(margins.gainCrossings[0].phaseMargin,30);
});
test('default ideal continuous poles are stable; unstable tuning is detected',()=>{
  assert.equal(M.poleStatus(M.poles(M.defaults)),'stable');
  assert.equal(M.poleStatus(M.poles({...M.defaults,kd:0,ki:1000})),'unstable');
  assert.equal(M.poleStatus([{re:0,im:2},{re:0,im:-2}]),'boundary / numerically near boundary');
});
test('sampled run is deterministic with bounded force and integral recovery',()=>{
  const p={...M.defaults,limit:2,duration:8},a=new M.Simulation(p),b=new M.Simulation(p);a.run();b.run();assert.deepEqual(a.data,b.data);assert.ok(a.data.every(r=>Math.abs(r.u)<=p.limit+1e-12));assert.ok(a.data.every(r=>Number.isFinite(r.energy)&&r.energy>=0));assert.ok(Math.abs(a.x-.5)<.02);assert.ok(Math.abs(a.integral)<1,'integrator must not wind up under unachievable target');
  const enough=new M.Simulation({...M.defaults,duration:30});enough.run();close(enough.x,1,2e-5);assert.ok(enough.data.some(r=>r.u<10));
});
test('proportional equilibrium agrees with static force balance including disturbance',()=>{
  const p={...M.defaults,ki:0,kd:0,target:1,disturbance:1,duration:35,b:3},s=new M.Simulation(p);s.run();close(s.x,(p.g*p.kp*p.target+p.disturbance)/(p.k+p.g*p.kp),1e-8);
  const zero=new M.Simulation({...M.defaults,g:0,target:1,disturbance:0,duration:3});zero.run();close(zero.x,0);close(zero.v,0);
});
test('sample-step refinement converges; sample rate affects the implemented response',()=>{
  const xs=[.04,.02,.01,.005].map(ts=>{const s=new M.Simulation({...M.defaults,ts,duration:1});s.run();return s.x;});
  const d1=Math.abs(xs[0]-xs[1]),d2=Math.abs(xs[1]-xs[2]),d3=Math.abs(xs[2]-xs[3]);assert.ok(d1>d2&&d2>d3);assert.ok(d1>1e-4);assert.ok(d2/d3>1.6&&d2/d3<2.5);
});
test('physical mass and controller parameters alter motion as expected',()=>{
  const normal=new M.Simulation({...M.defaults,duration:.1}),heavy=new M.Simulation({...M.defaults,m:4,duration:.1});normal.run();heavy.run();assert.ok(heavy.x<normal.x);
  const p=M.poles({...M.defaults,ki:0,kd:0,g:0});const heavyP=M.poles({...M.defaults,ki:0,kd:0,g:0,m:4});assert.ok(Math.abs(heavyP[0].im)<Math.abs(p[0].im));
});
test('derivative acts on measurement without a setpoint kick',()=>{
  const a=new M.Simulation({...M.defaults,target:1,limit:10000}),b=new M.Simulation({...M.defaults,target:1,kd:0,limit:10000});close(a.u,b.u);close(a.derivative,0);close(a.u,M.defaults.g*M.defaults.kp);
});
test('damped free motion obeys the mechanical energy balance',()=>{
  const s=new M.Simulation({...M.defaults,g:0,duration:3});s.x=1;s.prevX=1;s.data=[];s.record();s.run();let previous=s.data[0].energy;for(const row of s.data){assert.ok(row.energy<=previous+1e-10);previous=row.energy;}assert.ok(previous<s.data[0].energy*.1);
});
test('stiff damped case stays within RK4 stability range',()=>{
  const s=new M.Simulation({...M.defaults,m:.02,b:100,k:1000,ki:0,kd:0,duration:.2,ts:.1});s.run();assert.equal(s.failed,null);assert.ok(s.data.every(r=>Number.isFinite(r.x)));assert.ok(Math.abs(s.x)<1);
});
test('forward kinematics preserves link lengths and world conventions',()=>{
  const params={yaw:90,shoulder:0,elbow:0,l1:1,l2:2,base:.5},points=M.arm(params);close(points[3][0],0);close(points[3][1],3);close(points[3][2],.5);
  const bent=M.arm({...params,yaw:0,shoulder:90,elbow:-90});close(bent[3][0],2);close(bent[3][2],1.5);
  const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));close(distance(points[1],points[2]),1);close(distance(points[2],points[3]),2);
});
test('invalid physical parameters fail explicitly',()=>{
  assert.throws(()=>new M.Simulation({m:0}));assert.throws(()=>M.validate({ts:0}));assert.throws(()=>M.validate({ki:-1}));assert.throws(()=>M.validate({logMin:3,logMax:2}));assert.throws(()=>M.validate({g:NaN}));
});
test('browser assets are local plain scripts with no remote runtime dependencies',()=>{
  const dir=path.join(__dirname,'../assets/browser-lab'),html=fs.readFileSync(path.join(dir,'index.html'),'utf8'),js=fs.readFileSync(path.join(dir,'app.js'),'utf8');
  assert.ok(html.includes('src="math.js"'));assert.ok(html.includes('src="usd.js"'));assert.ok(html.includes('src="app.js"'));assert.ok(html.includes('href="style.css"'));
  assert.ok(!/(?:src|href)=["']https?:/.test(html));assert.ok(!/\bfetch\s*\(|\bimport\s*\(/.test(js));
});
test('all numeric browser controls accept arbitrary in-range values and valid defaults',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../assets/browser-lab/index.html'),'utf8');const controls=[...html.matchAll(/<input\b[^>]*type="number"[^>]*>/g)].map(match=>Object.fromEntries([...match[0].matchAll(/([\w-]+)="([^"]*)"/g)].map(m=>[m[1],m[2]])));
  assert.equal(controls.length,18);controls.forEach(q=>{assert.equal(q.step,'any');assert.ok(Number(q.value)>=Number(q.min),`${q.name} default below minimum`);assert.ok(Number(q.value)<=Number(q.max),`${q.name} default above maximum`);});
});
test('USDA pose declares units, axes, time rate, hierarchy, and visual-only scope',()=>{
  const pose=USD.exportPose({yaw:25,shoulder:30,elbow:-55,l1:1.2,l2:.9,base:.25});
  ['#usda 1.0','defaultPrim = "Robot"','metersPerUnit = 1','upAxis = "Z"','timeCodesPerSecond = 60','def Xform "YawJoint"','def Xform "ShoulderJoint"','def Xform "ElbowJoint"','def Xform "Tool"','double xformOp:rotateZ = 25','double xformOp:rotateY = -30','double xformOp:rotateY = 55'].forEach(text=>assert.ok(pose.includes(text),text));
  assert.ok(pose.includes('No mass, inertia, collision, articulation physics'));assert.ok(!pose.includes('.timeSamples'));assert.ok(!/Physics[A-Z]|physics:/.test(pose));
});
test('USDA animation time samples map seconds to stage codes and preserve angle signs',()=>{
  const p={yaw:0,shoulder:0,elbow:0,l1:1,l2:2,base:.5},samples=[{t:0,yaw:0,shoulder:0,elbow:0},{t:.5,yaw:90,shoulder:45,elbow:-45},{t:1,yaw:180,shoulder:90,elbow:-90}],anim=USD.exportAnimation(p,samples,{timeCodesPerSecond:60});
  assert.ok(anim.includes('startTimeCode = 0'));assert.ok(anim.includes('endTimeCode = 60'));assert.equal((anim.match(/\.timeSamples = \{/g)||[]).length,3);assert.ok(anim.includes('30: 90,'));assert.ok(anim.includes('30: -45,'));assert.ok(anim.includes('30: 45,'));assert.ok(anim.includes('def BasisCurves "ToolPath"'));assert.ok(anim.includes('curveVertexCounts = [3]'));
  const noPath=USD.exportAnimation(p,samples,{timeCodesPerSecond:24,includePath:false});assert.ok(noPath.includes('endTimeCode = 24'));assert.ok(!noPath.includes('def BasisCurves'));
  samples.forEach(q=>USD.toolPosition(p,q).forEach((v,i)=>close(v,M.arm({...p,...q})[3][i],1e-12)));
});
test('USDA exporter rejects invalid geometry, nonfinite values, and invalid sample times',()=>{
  const p={yaw:0,shoulder:0,elbow:0,l1:1,l2:2,base:.5},samples=[{t:0,yaw:0,shoulder:0,elbow:0},{t:1,yaw:90,shoulder:30,elbow:20}];
  for(const key of ['l1','l2','base'])assert.throws(()=>USD.exportPose({...p,[key]:0}));assert.throws(()=>USD.exportPose({...p,yaw:Infinity}));assert.throws(()=>USD.exportPose({...p,yaw:'0'}));
  assert.throws(()=>USD.exportAnimation(p,[]));assert.throws(()=>USD.exportAnimation(p,[samples[0]]));assert.throws(()=>USD.exportAnimation(p,[samples[0],samples[0]]));assert.throws(()=>USD.exportAnimation(p,[samples[1],samples[0]]));assert.throws(()=>USD.exportAnimation(p,[{...samples[0],t:-1},samples[1]]));assert.throws(()=>USD.exportAnimation(p,[samples[0],{...samples[1],elbow:NaN}]));assert.throws(()=>USD.exportAnimation(p,samples,{timeCodesPerSecond:0}));assert.throws(()=>USD.exportAnimation(p,samples,{timeCodesPerSecond:Infinity}));
});
process.stdout.write(`\n${passed} browser-lab numerical/source checks passed. These do not validate browser rendering or physical hardware.\n`);
