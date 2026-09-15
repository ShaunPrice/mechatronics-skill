#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const B=require('../assets/browser-lab/block-engine.js');let passed=0;
function test(name,fn){fn();passed++;process.stdout.write('PASS '+name+'\n');}
function close(value,expected,tolerance=1e-8){assert.ok(Math.abs(value-expected)<=tolerance,`${value} differs from ${expected} beyond ${tolerance}`);}
const node=(type,id,params={},label)=>({...B.createNode(type,id,50,50),params:{...B.library[type].defaults,...params},...(label?{label}:{})});
const edge=(id,from,to,port='in')=>({id,from:{node:from,port:'out'},to:{node:to,port}});
const graph=(nodes,edges,settings={dt:.01,duration:2})=>({schema:B.SCHEMA,settings,nodes,edges});
const fixture=()=>graph([node('constant','input',{value:1}),node('firstOrder','plant',{gain:1,tau:.5}),node('scope','scope')],[edge('a','input','plant'),edge('b','plant','scope')]);
test('known static graph evaluates gain, sum, saturation and scope in dependency order',()=>{
  const d=graph([node('scope','scope'),node('saturation','sat',{min:-5,max:5}),node('sum','sum'),node('gain','gain',{gain:3}),node('constant','a',{value:2}),node('constant','b',{value:1})],[edge('a_gain','a','gain'),edge('gain_sum','gain','sum','a'),edge('b_sum','b','sum','b'),edge('sum_sat','sum','sat'),edge('sat_scope','sat','scope')]);
  const s=new B.Simulator(d);close(s.evaluate().scopes.scope,5);s.step();close(s.history[1].scopes.scope,5);
});
test('first-order RK4 result matches analytic held-input response',()=>{
  const d=fixture();d.settings={dt:.05,duration:2};const s=new B.Simulator(d);s.run();close(s.time,2);close(s.history.at(-1).scopes.scope,1-Math.exp(-4),1e-7);
});
test('first-order sample-step refinement demonstrates fourth-order convergence',()=>{
  const expected=1-Math.exp(-2),errors=[.1,.05,.025].map(dt=>{const d=fixture();d.settings={dt,duration:1};const s=new B.Simulator(d);s.run();return Math.abs(s.history.at(-1).scopes.scope-expected);});
  assert.ok(errors[0]>errors[1]&&errors[1]>errors[2]);assert.ok(errors[0]/errors[1]>14&&errors[1]/errors[2]>14);
});
test('default PID feedback tracks reference with bounded actuator force',()=>{
  const s=new B.Simulator(B.createDefaultDiagram());s.run();assert.equal(s.error,null);close(s.history.at(-1).scopes.position,1,.0001);assert.ok(s.history.every(row=>Math.abs(row.outputs.controller)<=30));assert.ok(s.history.some(row=>row.outputs.reference===0));assert.ok(s.history.some(row=>row.outputs.reference===1));
});
test('PID derivative starts on measurement without setpoint kick and avoids windup',()=>{
  const d=B.createDefaultDiagram();d.settings.duration=10;d.nodes.find(n=>n.id==='controller').params.limit=2;d.nodes.find(n=>n.id==='reference').params.at=0;
  const s=new B.Simulator(d);close(s.history[0].outputs.controller,2);s.run();assert.ok(s.history.every(row=>Math.abs(row.outputs.controller)<=2));assert.ok(Math.abs(s.states.controller.integral)<1);close(s.history.at(-1).outputs.plant,.5,.005);
  const kick=B.createDefaultDiagram();kick.nodes.find(n=>n.id==='reference').params.at=0;kick.nodes.find(n=>n.id==='controller').params.limit=1000;const sk=new B.Simulator(kick);close(sk.history[0].outputs.controller,18);
});
test('multiple independent plants retain separate states and outputs',()=>{
  const d=graph([node('constant','a',{value:1}),node('constant','b',{value:2}),node('firstOrder','pa',{gain:1,tau:.5}),node('firstOrder','pb',{gain:3,tau:1}),node('scope','sa'),node('scope','sb')],[edge('a_pa','a','pa'),edge('b_pb','b','pb'),edge('pa_sa','pa','sa'),edge('pb_sb','pb','sb')],{dt:.02,duration:2});const s=new B.Simulator(d);s.run();close(s.history.at(-1).scopes.sa,1-Math.exp(-4),1e-8);close(s.history.at(-1).scopes.sb,6*(1-Math.exp(-2)),1e-8);
});
test('unit delay and integrator outputs update synchronously, independent of node ordering',()=>{
  const nodes=[node('constant','one',{value:1}),node('integrator','first'),node('integrator','second'),node('delay','delay'),node('scope','scope')],edges=[edge('a','one','first'),edge('b','first','second'),edge('c','second','delay'),edge('d','delay','scope')],d=graph(nodes,edges,{dt:.1,duration:.3});const s=new B.Simulator(d);s.step();close(s.history.at(-1).outputs.first,.1);close(s.history.at(-1).outputs.second,0);s.step();close(s.history.at(-1).outputs.second,.01);close(s.history.at(-1).outputs.delay,0);s.step();close(s.history.at(-1).outputs.delay,.01);
  const reverse=new B.Simulator({...d,nodes:nodes.slice().reverse()});reverse.run();for(let i=0;i<s.history.length;i++)for(const id of ['first','second','delay'])close(reverse.history[i].outputs[id],s.history[i].outputs[id]);
});
test('feedback through explicit delay is accepted but direct-feedthrough loops are rejected',()=>{
  const cycle=graph([node('gain','a'),node('gain','b')],[edge('a_b','a','b'),edge('b_a','b','a')]);assert.throws(()=>B.validateDiagram(cycle),/Algebraic loop/);
  const self=graph([node('gain','gain')],[edge('self','gain','gain')]);assert.throws(()=>B.validateDiagram(self),/Algebraic loop/);
  const delayed=graph([node('constant','one'),node('sum','sum',{signA:1,signB:1}),node('delay','memory'),node('scope','scope')],[edge('one_sum','one','sum','a'),edge('memory_sum','memory','sum','b'),edge('sum_memory','sum','memory'),edge('sum_scope','sum','scope')],{dt:.1,duration:.3});const s=new B.Simulator(delayed);s.run();assert.deepEqual(s.history.map(r=>r.scopes.scope),[1,2,3,4]);
});
test('reset exactly reproduces the initial states and deterministic run',()=>{
  const s=new B.Simulator(B.createDefaultDiagram());s.run();const saved=JSON.stringify(s.history);s.reset();close(s.time,0);assert.equal(s.history.length,1);s.run();assert.equal(JSON.stringify(s.history),saved);const other=new B.Simulator(B.createDefaultDiagram());other.run();assert.deepEqual(other.history,s.history);
});
test('sample rounding is explicit and logged at the declared effective duration',()=>{
  const d=fixture();d.settings={dt:.06,duration:.1};const checked=B.validateDiagram(d);close(checked.effectiveDuration,.12);assert.ok(checked.warnings.some(w=>w.includes('rounds up')));const s=new B.Simulator(d);s.run();close(s.time,.12);assert.deepEqual(s.history.map(r=>r.t),[0,.06,.12]);
  for(const settings of [{dt:.006,duration:.18+1e-12},{dt:.007,duration:.21},{dt:.003,duration:.1}]){const candidate={...fixture(),settings},result=B.validateDiagram(candidate),run=new B.Simulator(candidate);run.run();assert.equal(run.index,result.stepCount);assert.equal(run.history.length,result.stepCount+1);close(run.time,result.effectiveDuration,1e-14);}
});
test('thermal preset matches its lumped first-order analytic temperature',()=>{
  const s=new B.Simulator(B.createThermalDiagram());s.run();close(s.time,30);close(s.history.at(-1).scopes.temperatureScope,25+50*.2*(1-Math.exp(-30/100)),1e-10);close(s.history.at(-1).scopes.temperatureScope,27.59181779318282,1e-10);
});
test('fluid tank preset matches its linear outflow analytic level',()=>{
  const s=new B.Simulator(B.createTankDiagram());s.run();close(s.time,30);close(s.history.at(-1).scopes.level,1-Math.exp(-30/50),1e-10);close(s.history.at(-1).scopes.level,.4511883639059736,1e-10);
});
test('sine and step sources obey their sample-time definitions',()=>{
  const d=graph([node('sine','sine',{amplitude:2,frequency:1,offset:3,phase:90}),node('step','step',{initial:-1,final:4,at:.2}),node('scope','scope')],[edge('sine_scope','sine','scope')],{dt:.1,duration:.3});const s=new B.Simulator(d);close(s.history[0].outputs.sine,5);s.run();close(s.history[1].outputs.sine,3+2*Math.cos(.2*Math.PI));assert.deepEqual(s.history.map(r=>r.outputs.step),[-1,-1,4,4]);
});
test('invalid imports reject unknown schemas, dangling wires, duplicate inputs and nonfinite parameters',()=>{
  const d=fixture();assert.throws(()=>B.validateDiagram({...d,schema:'xcos'}),/schema/);assert.throws(()=>B.validateDiagram({...d,extra:'code'}),/Unknown/);
  const invalid=copy=>JSON.parse(JSON.stringify(copy));let bad=invalid(d);bad.edges[0].from.node='missing';assert.throws(()=>B.validateDiagram(bad),/missing/);
  bad=invalid(d);bad.edges.push({...bad.edges[0],id:'duplicate'});assert.throws(()=>B.validateDiagram(bad),/more than one wire/);
  bad=invalid(d);bad.nodes[0].params.value=NaN;assert.throws(()=>B.validateDiagram(bad),/finite/);
  bad=invalid(d);bad.nodes[0].params.value=Infinity;assert.throws(()=>B.validateDiagram(bad),/finite/);
  bad=invalid(d);bad.nodes[1].params.tau=0;assert.throws(()=>B.validateDiagram(bad),/between/);
  bad=invalid(d);bad.edges[0].to.port='invented';assert.throws(()=>B.validateDiagram(bad),/invalid/);
  bad=invalid(d);bad.nodes[0].type='script';assert.throws(()=>B.validateDiagram(bad),/Unsupported/);
  bad=invalid(d);bad.nodes[0].params.expression='alert(1)';assert.throws(()=>B.validateDiagram(bad),/Unknown/);
  for(const reserved of ['constructor','toString','hasOwnProperty']){bad=invalid(d);bad.nodes[0].id=reserved;assert.throws(()=>B.validateDiagram(bad),/reserved identifier/);}
});
test('graph validation rejects missing inputs for execution but supports incomplete edits',()=>{
  const d=graph([node('gain','gain')],[]);assert.throws(()=>new B.Simulator(d),/Connect required/);const incomplete=B.validateDiagram(d,{allowIncomplete:true});assert.equal(incomplete.missingInputs.length,1);
  assert.throws(()=>B.validateDiagram(graph([],[])),/at least one/);assert.doesNotThrow(()=>B.validateDiagram(graph([],[]),{allowIncomplete:true}));
});
test('model and integration workloads are bounded before execution',()=>{
  const d=fixture();assert.throws(()=>B.validateDiagram({...d,settings:{dt:.0001,duration:2}}));assert.throws(()=>B.validateDiagram({...d,settings:{dt:.01,duration:61}}));assert.throws(()=>B.validateDiagram({...d,nodes:Array.from({length:51},(_,i)=>node('constant','n'+i))}),/50 blocks/);
  const nodes=[node('constant','force')],edges=[];for(let i=0;i<11;i++){nodes.push(node('massSpring','mass'+i,{m:.02,b:100,k:1000}));edges.push(edge('e'+i,'force','mass'+i));}assert.throws(()=>B.validateDiagram(graph(nodes,edges,{dt:.1,duration:60})),/integration workload/);
});
test('numeric envelope stops a divergent sampled model with a readable error',()=>{
  const d=graph([node('constant','one'),node('sum','sum',{signA:1,signB:1}),node('gain','gain',{gain:1e5}),node('delay','delay')],[edge('a','one','sum','a'),edge('b','delay','sum','b'),edge('c','sum','gain'),edge('d','gain','delay')],{dt:.1,duration:1});const s=new B.Simulator(d);assert.throws(()=>s.run(),/envelope exceeded/);assert.ok(s.error);close(s.time,s.history.at(-1).t);
});
test('browser builder has local assets, safe label rendering, and explicit import limits',()=>{
  const dir=path.join(__dirname,'../assets/browser-lab'),html=fs.readFileSync(path.join(dir,'builder.html'),'utf8'),js=fs.readFileSync(path.join(dir,'builder.js'),'utf8');assert.ok(html.includes('src="block-engine.js"'));assert.ok(html.includes('src="builder.js"'));assert.ok(html.includes('href="builder.css"'));assert.ok(!/(?:href|src)=["']https?:/.test(html));assert.ok(!/\.innerHTML\s*=|\beval\s*\(|new\s+Function\s*\(|\bfetch\s*\(/.test(js));assert.ok(js.includes('file.size>300000'));assert.ok(js.includes('visibilitychange'));assert.ok(js.includes('performance.now()-started>10'));
});
process.stdout.write(`\n${passed} block-engine tests passed. Browser interaction and hardware validation are separate checks.\n`);
