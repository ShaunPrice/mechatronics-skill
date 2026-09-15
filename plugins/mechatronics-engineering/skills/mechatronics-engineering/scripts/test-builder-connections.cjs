#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
// These are the same gesture reducer and edge mutation used by the DOM editor.
// Pointer capture, hit-testing and visual feedback still require browser checks.
const {PortDragGesture,connectionCandidate}=require('../assets/browser-lab/builder.js');
const B=require('../assets/browser-lab/block-engine.js');
let passed=0;
function test(name,fn){fn();passed++;process.stdout.write('PASS '+name+'\n');}
const pointer=(x,y,id=1)=>({pointerId:id,clientX:x,clientY:y});
const source={node:'constant',port:'out'},target={node:'gain',port:'in',direction:'in'};
const create=()=>{const g=new PortDragGesture();assert.equal(g.start(pointer(10,10),source),true);return g;};
function graph(){const nodes=['constant','gain','scope'].map(type=>B.createNode(type,type,50,50));nodes[0].params.value=3;nodes[1].params.gain=2;return {schema:B.SCHEMA,settings:{dt:.01,duration:.1},nodes,edges:[]};}
function drop(g,to,x=100,y=40){g.move(pointer(x,y),to);return g.finish(pointer(x,y),to);}
function checkedConnection(diagram,result){assert.equal(result.kind,'drop');assert.ok(result.target);const candidate=connectionCandidate(diagram,result.from,result.target);return B.validateDiagram(candidate.diagram,{allowIncomplete:true}).diagram;}

test('stationary press and small movement preserve the native click route',()=>{
  const g=create();assert.equal(g.move(pointer(12,12),target).dragging,false);const result=g.finish(pointer(12,12),target);assert.equal(result.kind,'click');assert.equal(result.target,null);assert.equal(g.current,null);
});
test('drag beyond threshold records the input released on',()=>{
  const g=create();const result=drop(g,target);assert.deepEqual(result,{kind:'drop',from:source,target:{node:'gain',port:'in'},pointerId:1});assert.equal(g.current,null);
});
test('pointer-up can establish a drag even without an intermediate move event',()=>{
  const result=create().finish(pointer(70,20),target);assert.equal(result.kind,'drop');assert.deepEqual(result.target,{node:'gain',port:'in'});
});
test('returning near the source after a drag does not turn it into a click',()=>{
  const g=create();g.move(pointer(60,10),target);assert.equal(g.finish(pointer(11,10),null).kind,'drop');
});
test('empty-space and output-port drops do not yield a connection target',()=>{
  for(const destination of [null,{node:'other',port:'out',direction:'out'}]){const result=drop(create(),destination);assert.equal(result.kind,'drop');assert.equal(result.target,null);}
});
test('the release target supersedes an earlier hovered input',()=>{
  const g=create();g.move(pointer(70,10),target);const result=g.finish(pointer(130,10),{node:'scope',port:'in',direction:'in'});assert.deepEqual(result.target,{node:'scope',port:'in'});
});
test('secondary pointers cannot move, end or cancel the active connection',()=>{
  const g=create();assert.equal(g.start(pointer(90,90,2),{node:'other',port:'out'}),false);assert.equal(g.move(pointer(80,50,2),target),null);assert.equal(g.finish(pointer(80,50,2),target),null);assert.equal(g.cancel(2),null);assert.equal(g.current.pointerId,1);assert.equal(drop(g,target).kind,'drop');
});
test('cancellation clears the gesture and permits a clean new drag',()=>{
  const g=create();g.move(pointer(60,10),target);assert.equal(g.cancel().dragging,true);assert.equal(g.current,null);assert.equal(g.finish(pointer(60,10),target),null);assert.equal(g.cancel(),null);assert.equal(g.start(pointer(10,10),source),true);assert.deepEqual(drop(g,target).target,{node:'gain',port:'in'});
});
test('two real drag results build Constant 3 → Gain 2 → Scope and simulate 6',()=>{
  const original=graph(),snapshot=JSON.stringify(original);let diagram=checkedConnection(original,drop(create(),target));const g=new PortDragGesture();g.start(pointer(10,10),{node:'gain',port:'out'});diagram=checkedConnection(diagram,drop(g,{node:'scope',port:'in',direction:'in'}));const run=new B.Simulator(diagram);run.run();assert.ok(run.history.every(row=>row.scopes.scope===6));assert.equal(JSON.stringify(original),snapshot);assert.deepEqual(diagram.edges.map(e=>e.id),['w1','w2']);
});
test('occupied-input drop is rejected without modifying the accepted graph',()=>{
  const diagram=checkedConnection(graph(),drop(create(),target)),snapshot=JSON.stringify(diagram),candidate=connectionCandidate(diagram,source,{node:'gain',port:'in'});assert.throws(()=>B.validateDiagram(candidate.diagram,{allowIncomplete:true}),/more than one wire/);assert.equal(JSON.stringify(diagram),snapshot);
});
test('connection mutation still rejects algebraic loops through the graph validator',()=>{
  const diagram=graph(),candidate=connectionCandidate(diagram,{node:'gain',port:'out'},{node:'gain',port:'in'});assert.throws(()=>B.validateDiagram(candidate.diagram,{allowIncomplete:true}),/Algebraic loop/);assert.equal(diagram.edges.length,0);
});
test('edge IDs remain unique after deletion and malformed destinations are rejected',()=>{
  const diagram=checkedConnection(graph(),drop(create(),target));diagram.edges[0].id='w2';const candidate=connectionCandidate(diagram,{node:'gain',port:'out'},{node:'scope',port:'in'});assert.equal(candidate.edge.id,'w1');assert.doesNotThrow(()=>B.validateDiagram(candidate.diagram));const bad=connectionCandidate(diagram,source,{node:'missing',port:'in'});assert.throws(()=>B.validateDiagram(bad.diagram,{allowIncomplete:true}),/missing/);
});
process.stdout.write(`\n${passed} builder-connection tests passed. DOM capture, touch and visual feedback require separate browser checks.\n`);
