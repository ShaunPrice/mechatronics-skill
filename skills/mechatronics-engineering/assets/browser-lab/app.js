/* Offline presentation layer. The numerical simulation does not use frame delta as its integration step. */
(function () {
  'use strict';
  const M=window.MechMath,$=id=>document.getElementById(id),colors={cyan:'#53d9d1',amber:'#f7be66',violet:'#ab9bff',muted:'#8297ae',red:'#f18290',green:'#9ad89a'};
  let p={...M.defaults},sim=new M.Simulation(p),running=false,activeTab='dynamics',lastFrame=null,accumulator=0,lastDraw=0,analysis={};
  const chartState=new WeakMap(),tooltip=$('tooltip');
  const fmt=(v,d=3)=> !Number.isFinite(v)?'—':(Math.abs(v)>=1e4||(Math.abs(v)>0&&Math.abs(v)<.001))?v.toExponential(2):v.toFixed(d);
  const compact=v=>Math.abs(v)>=1000||Math.abs(v)>0&&Math.abs(v)<.01?v.toExponential(1):Number(v.toPrecision(3)).toString();
  function prepare(canvas) {
    const r=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
    if(!r.width||!r.height) return null;
    const w=Math.round(r.width*dpr),h=Math.round(r.height*dpr);
    if(canvas.width!==w||canvas.height!==h) {canvas.width=w;canvas.height=h;}
    const c=canvas.getContext('2d');c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,r.width,r.height);
    return {c,w:r.width,h:r.height};
  }
  const range=(values,pad=.12)=> { const finite=values.filter(Number.isFinite); if(!finite.length)return [-1,1];let lo=Math.min(...finite),hi=Math.max(...finite);if(hi-lo<1e-8){lo-=1;hi+=1;}const d=(hi-lo)*pad;return [lo-d,hi+d]; };
  function plot(id,series,opts={}) {
    const canvas=$(id),view=prepare(canvas);if(!view)return;
    const {c,w,h}=view,rect={x:59,y:15,w:w-76,h:h-52};if(rect.w<30)return;
    const points=series.flatMap(s=>s.data).filter(q=>Number.isFinite(q.x)&&Number.isFinite(q.y));
    let xr=opts.xRange||range(points.map(q=>q.x)),yr=opts.yRange||range(points.map(q=>q.y));
    if(opts.equal) {const middle=(yr[0]+yr[1])/2,half=(xr[1]-xr[0])*rect.h/rect.w/2;yr=[middle-half,middle+half];}
    const px=x=>rect.x+(x-xr[0])/(xr[1]-xr[0])*rect.w,py=y=>rect.y+rect.h-(y-yr[0])/(yr[1]-yr[0])*rect.h;
    c.font='10px system-ui';c.lineWidth=1;
    for(let i=0;i<=4;i++) {const x=xr[0]+(xr[1]-xr[0])*i/4,y=yr[0]+(yr[1]-yr[0])*i/4;
      c.strokeStyle='#273345';c.beginPath();c.moveTo(px(x),rect.y);c.lineTo(px(x),rect.y+rect.h);c.stroke();c.beginPath();c.moveTo(rect.x,py(y));c.lineTo(rect.x+rect.w,py(y));c.stroke();
      c.fillStyle='#8da1b9';c.textAlign='center';c.fillText(opts.xFormat?opts.xFormat(x):compact(x),px(x),rect.y+rect.h+16);c.textAlign='right';c.fillText(compact(y),rect.x-8,py(y)+3);
    }
    c.save();c.beginPath();c.rect(rect.x,rect.y,rect.w,rect.h);c.clip();
    (opts.hLines||[]).forEach(y=>{c.strokeStyle='#9a927655';c.setLineDash([4,5]);c.beginPath();c.moveTo(rect.x,py(y));c.lineTo(rect.x+rect.w,py(y));c.stroke();c.setLineDash([]);});
    (opts.vLines||[]).forEach(x=>{c.strokeStyle='#9a927655';c.setLineDash([4,5]);c.beginPath();c.moveTo(px(x),rect.y);c.lineTo(px(x),rect.y+rect.h);c.stroke();c.setLineDash([]);});
    const hover=[];
    series.forEach(s=> {
      c.strokeStyle=s.color;c.fillStyle=s.color;c.lineWidth=s.width||1.7;c.setLineDash(s.dashed?[5,4]:[]);
      if(!s.marker) {c.beginPath();let started=false;s.data.forEach(q=>{if(!Number.isFinite(q.y)||!Number.isFinite(q.x)){started=false;return;}if(!started)c.moveTo(px(q.x),py(q.y));else c.lineTo(px(q.x),py(q.y));started=true;});c.stroke();}
      s.data.forEach((q,i)=> {if(!Number.isFinite(q.x)||!Number.isFinite(q.y))return;const x=px(q.x),y=py(q.y),size=s.size||4;
        if(s.marker) {c.beginPath();if(s.marker==='x'){c.moveTo(x-size,y-size);c.lineTo(x+size,y+size);c.moveTo(x-size,y+size);c.lineTo(x+size,y-size);}else if(s.marker==='+'){c.moveTo(x-size,y);c.lineTo(x+size,y);c.moveTo(x,y-size);c.lineTo(x,y+size);}else {c.arc(x,y,size,0,Math.PI*2);}if(s.marker==='dot')c.fill();else c.stroke();}
        if(x>=rect.x&&x<=rect.x+rect.w&&y>=rect.y&&y<=rect.y+rect.h)hover.push({x,y,label:s.label,text:q.tip||`${s.label}\n${opts.xLabel||'x'}: ${fmt(q.x)}\n${opts.yLabel||'y'}: ${fmt(q.y)}`});
        if(s.arrows&&i>0&&i%65===0){const prev=s.data[i-1],dx=x-px(prev.x),dy=y-py(prev.y),a=Math.atan2(dy,dx);c.save();c.translate(x,y);c.rotate(a);c.beginPath();c.moveTo(-7,-3);c.lineTo(0,0);c.lineTo(-7,3);c.stroke();c.restore();}
      });c.setLineDash([]);
    });c.restore();
    c.fillStyle='#a9b8cb';c.textAlign='center';c.font='10px system-ui';c.fillText(opts.xLabel||'',rect.x+rect.w/2,h-3);c.save();c.translate(12,rect.y+rect.h/2);c.rotate(-Math.PI/2);c.fillText(opts.yLabel||'',0,0);c.restore();
    chartState.set(canvas,hover);
    if(!canvas.dataset.hoverReady) {canvas.dataset.hoverReady='true';canvas.addEventListener('pointermove',event=> {const rr=canvas.getBoundingClientRect(),x=event.clientX-rr.left,y=event.clientY-rr.top,hh=chartState.get(canvas)||[];let best=null,dist=625;hh.forEach(q=>{const d=(q.x-x)**2+(q.y-y)**2;if(d<dist){dist=d;best=q;}});if(!best){tooltip.hidden=true;return;}tooltip.textContent=best.text;tooltip.hidden=false;const tw=tooltip.offsetWidth,th=tooltip.offsetHeight;tooltip.style.left=Math.min(window.innerWidth-tw-8,event.clientX+14)+'px';tooltip.style.top=Math.max(8,Math.min(window.innerHeight-th-8,event.clientY+14))+'px';});canvas.addEventListener('pointerleave',()=>tooltip.hidden=true);}
  }
  function download(name,content,type) {const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  const evidence={classification:'illustrative model simulation; no hardware validation',continuousAnalysis:'Ideal continuous-time negative unity-feedback L(s)=C(s)G(s); excludes sampling, saturation, delay and disturbances. Derivative-on-measurement changes setpoint numerator but not feedback denominator.',sampledSimulation:'Fixed controller sample clock; derivative on measurement with exponential filtering; conditional integral anti-windup; saturated force held between updates; RK4 plant integration.',nyquist:'Finite positive/negative frequency trace only, not a completed contour or encirclement proof. Clockwise-positive complete-contour convention: Z=P+N.',margins:'Finite-grid interpolated crossing estimates; missing or multiple crossings must not be reduced to a fabricated single verdict.'};
  function refreshAnalysis() {
    const freq=M.frequency(p),locus=M.rootLocus(p),margins=M.margins(freq),status=M.poleStatus(locus.current);
    analysis={frequency:freq,rootLocus:locus,margins,continuousPoles:locus.current,continuousPoleStatus:status,characteristicPolynomialDescending:M.characteristic(p)};
    $('pole-status').textContent=status.toUpperCase();$('pole-status').className='chip '+(status==='stable'?'stable':status==='unstable'?'unstable':'');
    $('pole-summary').textContent=`Current g = ${fmt(p.g,2)} · pole real parts in s⁻¹\n`+locus.current.map(r=>`${fmt(r.re)} ${r.im<0?'−':'+'} j${fmt(Math.abs(r.im))}`).join('  |  ');
    const lines=[];
    if(margins.gainCrossings.length) margins.gainCrossings.forEach((r,i)=>lines.push(`Gain crossing ${i+1}: ω = ${fmt(r.omega)} rad/s; PM = ${fmt(r.phaseMargin,1)}°`));else lines.push('0 dB crossing: not found in displayed range.');
    if(margins.phaseCrossings.length)margins.phaseCrossings.forEach((r,i)=>lines.push(`Phase crossing ${i+1}: ω = ${fmt(r.omega)} rad/s; GM = ${fmt(r.gainMarginDb,1)} dB`));else lines.push('−180° (mod 360°) crossing: not found in displayed range.');
    $('margin-summary').textContent=lines.join('\n');$('margin-summary').style.whiteSpace='pre-line';
    $('nyquist-warning').textContent=p.ki>0?'Ki > 0 introduces an imaginary-axis pole at s = 0. The plotted frequency range omits the origin indentation, the high-frequency closure, and limiting tails. No completed-contour stability proof is shown.':'The trace samples a finite frequency interval. Closure and limiting tails are not constructed; no completed-contour stability proof is shown.';
    drawAnalysis();
  }
  function drawAnalysis() {
    if(activeTab!=='dynamics')return;const {frequency:f,rootLocus:l}=analysis;if(!f)return;
    const rootTip=(r,g)=>`Gain g: ${fmt(g,3)}\nPole: ${fmt(r.re)} ${r.im<0?'−':'+'} j${fmt(Math.abs(r.im))} s⁻¹`;
    plot('root-chart',[{label:'Locus sample',color:colors.cyan,marker:'dot',size:1.5,data:l.rows.flatMap(row=>row.poles.map(r=>({x:r.re,y:r.im,tip:rootTip(r,row.g)})))},{label:'Open-loop pole',color:colors.muted,marker:'+',size:6,data:l.open.map(r=>({x:r.re,y:r.im,tip:'Open-loop pole at g = 0\n'+rootTip(r,0)}))},{label:'Controller zero',color:colors.violet,marker:'circle',size:5,data:l.zeros.map(r=>({x:r.re,y:r.im,tip:`Controller zero\n${fmt(r.re)} ${r.im<0?'−':'+'} j${fmt(Math.abs(r.im))} s⁻¹`}))},{label:'Current pole',color:colors.amber,marker:'x',size:6,width:2.4,data:l.current.map(r=>({x:r.re,y:r.im,tip:rootTip(r,p.g)}))}],{xLabel:'Real part σ / s⁻¹',yLabel:'Imaginary part ω / s⁻¹',hLines:[0],vLines:[0],xRange:range([...l.rows.flatMap(r=>r.poles.map(z=>z.re)),...l.zeros.map(z=>z.re),0])});
    const freqSeries=key=>f.map(q=>({x:Math.log10(q.omega),y:q[key],tip:`ω: ${fmt(q.omega)} rad/s\n|L|: ${fmt(q.magnitude,2)} dB\nPhase: ${fmt(q.phase,2)}°\nL: ${fmt(q.re)} ${q.im<0?'−':'+'} j${fmt(Math.abs(q.im))}`}));
    plot('bode-mag',[{label:'Loop magnitude',color:colors.cyan,data:freqSeries('magnitude')}],{xLabel:'Frequency ω / rad·s⁻¹ (log scale)',yLabel:'Magnitude / dB',xRange:[p.logMin,p.logMax],xFormat:v=>compact(10**v),hLines:[0]});
    plot('bode-phase',[{label:'Unwrapped loop phase',color:colors.violet,data:freqSeries('phase')}],{xLabel:'Frequency ω / rad·s⁻¹ (log scale)',yLabel:'Phase / °',xRange:[p.logMin,p.logMax],xFormat:v=>compact(10**v),hLines:[-180]});
    const pos=f.map(q=>({x:q.re,y:q.im,tip:`+ω: ${fmt(q.omega)} rad/s\nRe(L): ${fmt(q.re)}\nIm(L): ${fmt(q.im)}`})),neg=f.map(q=>({x:q.re,y:-q.im,tip:`−ω: ${fmt(-q.omega)} rad/s\nRe(L): ${fmt(q.re)}\nIm(L): ${fmt(-q.im)}`}));
    const focus=$('nyquist-focus').checked,xrange=focus?[-3,1.5]:range([...pos.map(q=>q.x),-1,0]),yrange=focus?[-2,2]:range([...pos.map(q=>q.y),...neg.map(q=>q.y),0]);
    // Equal horizontal and vertical scale; expand either dimension to fit the full finite trace.
    const canvas=$('nyquist-chart'),r=canvas.getBoundingClientRect(),aspect=Math.max(.3,(r.width-76)/(r.height-52));let xr=xrange.slice(),yr=yrange.slice();
    if(!focus && (yr[1]-yr[0])>(xr[1]-xr[0])/aspect){const mid=(xr[0]+xr[1])/2,half=(yr[1]-yr[0])*aspect/2;xr=[mid-half,mid+half];}
    plot('nyquist-chart',[{label:'Positive frequency',color:colors.cyan,data:pos,arrows:true},{label:'Negative frequency',color:colors.violet,data:neg,arrows:true},{label:'Critical point',color:colors.amber,marker:'x',size:7,width:2,data:[{x:-1,y:0,tip:'Critical point: −1 + j0\nDimensionless loop response'}]}],{xLabel:'Real L(jω) / dimensionless',yLabel:'Imaginary L(jω) / dimensionless',xRange:xr,yRange:yr,equal:true,hLines:[0],vLines:[0]});
  }
  function drawMechanism() {
    const view=prepare($('mechanism'));if(!view)return;const {c,w,h}=view;
    const span=Math.max(1.5,Math.abs(p.target)*1.2,Math.abs(sim.x)*1.2),origin=w*.53,scale=(w*.29)/span,position=origin+sim.x*scale,target=origin+p.target*scale,wall=22,cy=h*.43,block=54;
    c.fillStyle='#101925';c.fillRect(0,0,w,h);c.strokeStyle='#253548';c.lineWidth=1;
    for(let x=20;x<w;x+=30){c.beginPath();c.moveTo(x,20);c.lineTo(x,h-25);c.stroke();}for(let y=20;y<h-20;y+=30){c.beginPath();c.moveTo(20,y);c.lineTo(w-10,y);c.stroke();}
    c.strokeStyle='#6c8098';c.lineWidth=3;c.beginPath();c.moveTo(wall,cy-53);c.lineTo(wall,cy+56);c.moveTo(15,cy+65);c.lineTo(w-12,cy+65);c.stroke();
    c.setLineDash([4,5]);c.strokeStyle=colors.amber;c.lineWidth=1;c.beginPath();c.moveTo(target,cy-58);c.lineTo(target,cy+66);c.stroke();c.setLineDash([]);
    c.fillStyle=colors.amber;c.textAlign='center';c.font='10px system-ui';c.fillText(`target ${fmt(p.target,2)} m`,M.clamp(target,65,w-65),cy-68);
    const end=position-block/2,start=wall+12,length=end-start,sy=cy-15;
    c.strokeStyle=colors.cyan;c.lineWidth=2;c.beginPath();c.moveTo(wall,sy);c.lineTo(start,sy);for(let i=0;i<=18;i++){const x=start+length*i/18,y=sy+(i===0||i===18?0:(i%2?9:-9));c.lineTo(x,y);}c.lineTo(end,sy);c.stroke();
    const dy=cy+19,mid=(wall+end)/2;c.strokeStyle=colors.violet;c.beginPath();c.moveTo(wall,dy);c.lineTo(mid-16,dy);c.moveTo(mid+17,dy);c.lineTo(end,dy);c.moveTo(mid+17,dy-9);c.lineTo(mid-16,dy-9);c.lineTo(mid-16,dy+9);c.lineTo(mid+17,dy+9);c.moveTo(mid+4,dy-7);c.lineTo(mid+4,dy+7);c.stroke();
    c.fillStyle='#224b58';c.strokeStyle=colors.cyan;c.lineWidth=1.5;c.fillRect(position-block/2,cy-39,block,79);c.strokeRect(position-block/2,cy-39,block,79);c.fillStyle='#def8f7';c.font='bold 13px system-ui';c.textAlign='center';c.fillText(`${compact(p.m)} kg`,position,cy+3);
    c.fillStyle='#0c121b';[position-15,position+15].forEach(x=>{c.beginPath();c.arc(x,cy+53,10,0,Math.PI*2);c.fill();c.stroke();});
    const forceLength=Math.min(55,Math.abs(sim.u)/p.limit*55),direction=Math.sign(sim.u);c.strokeStyle=colors.amber;c.fillStyle=colors.amber;c.lineWidth=2;
    if(forceLength>1){const ax=position+direction*(block/2+7),bx=ax+direction*forceLength;c.beginPath();c.moveTo(ax,cy);c.lineTo(bx,cy);c.lineTo(bx-direction*7,cy-4);c.moveTo(bx,cy);c.lineTo(bx-direction*7,cy+4);c.stroke();}
    c.font='10px system-ui';c.textAlign='left';c.fillStyle=colors.cyan;c.fillText(`k = ${compact(p.k)} N/m`,30,h-29);c.fillStyle=colors.violet;c.fillText(`b = ${compact(p.b)} N·s/m`,30,h-13);c.textAlign='right';c.fillStyle='#95a8bd';c.fillText('Schematic: travel rescales with motion',w-10,h-13);
  }
  function drawTime() {
    if(activeTab!=='dynamics')return;const last=sim.data[sim.data.length-1],stride=Math.max(1,Math.floor(sim.data.length/1400)),rows=sim.data.filter((_,i)=>i%stride===0||i===sim.data.length-1),xrange=[0,Math.max(5,sim.t)];
    $('time').innerHTML=fmt(sim.t,2)+' <small>s</small>';$('position').innerHTML=fmt(sim.x)+' <small>m</small>';$('force').innerHTML=fmt(sim.u,2)+' <small>N</small>';$('energy').innerHTML=fmt(last.energy)+' <small>J</small>';
    plot('time-chart',[{label:'Position',color:colors.cyan,data:rows.map(r=>({x:r.t,y:r.x,tip:`t: ${fmt(r.t)} s\nx: ${fmt(r.x)} m\nv: ${fmt(r.v)} m/s\nerror: ${fmt(r.error)} m`}))},{label:'Target',color:colors.amber,dashed:true,data:[{x:0,y:p.target},{x:xrange[1],y:p.target}]}],{xLabel:'Simulated time / s',yLabel:'Position / m',xRange:xrange});
    plot('force-chart',[{label:'Actuator force',color:colors.violet,data:rows.map(r=>({x:r.t,y:r.u,tip:`t: ${fmt(r.t)} s\nu: ${fmt(r.u)} N\nlimit: ±${fmt(p.limit)} N`}))}],{xLabel:'Simulated time / s',yLabel:'Force / N',xRange:xrange,yRange:[-p.limit*1.12,p.limit*1.12],hLines:[-p.limit,p.limit,0]});drawMechanism();
  }
  function setRunning(value) {running=value;$('play').textContent=value?'Ⅱ Pause':'▶ Run experiment';$('run-status').textContent=value?'Running on fixed sample clock':sim.failed||sim.t>=p.duration?'Run complete':sim.t?'Paused':'Ready';accumulator=0;}
  function resetSimulation() {setRunning(false);sim=new M.Simulation(p);$('run-status').textContent='Ready';drawTime();}
  function readParams(){const next={};new FormData($('parameters')).forEach((v,k)=>next[k]=Number(v));return M.validate(next);}
  $('parameters').addEventListener('submit',e=>e.preventDefault());
  $('parameters').addEventListener('input',()=> {
    try {if(!$('parameters').checkValidity())throw Error('Enter a valid number within each displayed parameter range.');p=readParams();$('error').hidden=true;$('gain-value').value=fmt(p.g,2);resetSimulation();refreshAnalysis();}
    catch(e){setRunning(false);$('error').textContent=e.message+' The plots retain the last valid model.';$('error').hidden=false;}
  });
  $('defaults').addEventListener('click',()=>{p={...M.defaults};Object.entries(p).forEach(([k,v])=>$('parameters').elements.namedItem(k).value=v);$('gain-value').value=fmt(p.g,2);$('error').hidden=true;resetSimulation();refreshAnalysis();});
  $('play').addEventListener('click',()=>{if(!$('error').hidden)return;if(sim.t>=p.duration||sim.failed)resetSimulation();setRunning(!running);});$('reset').addEventListener('click',resetSimulation);
  $('nyquist-focus').addEventListener('change',drawAnalysis);
  $('export-csv').addEventListener('click',()=> {const keys=Object.keys(M.units).filter(k=>k in sim.data[0]);const metadata=['# Mechatronics browser lab run; schema mechatronics-browser-lab/v1','# Evidence: illustrative numerical simulation; no hardware validation','# Parameters SI: '+JSON.stringify(p),'# Controller: sampled PID; derivative on measurement; conditional anti-windup; saturated ZOH force; RK4 plant','# Clock: t = integer sample index * Ts; exports include complete data, not chart decimation',keys.map(k=>`${k} [${M.units[k]}]`).join(',')];download('mechatronics-run.csv',metadata.concat(sim.data.map(row=>keys.map(k=>row[k]).join(','))).join('\n'),'text/csv');});
  $('export-json').addEventListener('click',()=>download('mechatronics-model-and-data.json',JSON.stringify({schema:'mechatronics-browser-lab/v1',createdAt:new Date().toISOString(),parameters:p,parameterUnits:{m:'kg',b:'N s/m',k:'N/m',kp:'N/m',ki:'N/(m s)',kd:'N s/m',tf:'s',g:'dimensionless',ts:'s',limit:'N',target:'m',disturbance:'N',duration:'s',logMin:'log10(rad/s)',logMax:'log10(rad/s)',locusMax:'dimensionless'},units:M.units,evidence,runState:{complete:sim.t>=p.duration,failed:sim.failed},...analysis,time:sim.data},null,2),'application/json'));

  // A genuine perspective projection of 3D joint/link geometry, rendered by a depth-sorted Canvas painter.
  let armBase={yaw:25,shoulder:30,elbow:-55,l1:1.2,l2:.9,base:.25},armQ={...armBase},armRunning=false,armSteps=0,armAccumulator=0,armData=[],camera={az:.85,elev:.48,radius:6.5},drag=null;
  const vector={add:(a,b)=>a.map((v,i)=>v+b[i]),sub:(a,b)=>a.map((v,i)=>v-b[i]),scale:(a,s)=>a.map(v=>v*s),dot:(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross:(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],normal:a=>{const n=Math.hypot(...a);return a.map(v=>v/n);}};
  function armRecord(){const end=M.arm(armQ)[3];armData.push({t:armSteps/60,x:end[0],y:end[1],z:end[2],yaw:armQ.yaw,shoulder:armQ.shoulder,elbow:armQ.elbow});$('export-usd-animation').disabled=armData.length<2;}
  function resetArm(){armRunning=false;armSteps=0;armAccumulator=0;armQ={...armBase};armData=[];armRecord();$('arm-motion').textContent='▶ Demonstrate joint motion';drawArm();}
  function armStep(){armSteps++;const t=armSteps/60;armQ={...armBase,yaw:M.clamp(armBase.yaw+35*Math.sin(t*.6),-180,180),shoulder:M.clamp(armBase.shoulder+18*Math.sin(t*.9),-90,120),elbow:M.clamp(armBase.elbow+25*Math.sin(t*.75),-150,150)};armRecord();if(armSteps>=1800){armRunning=false;$('arm-motion').textContent='↺ Replay joint motion';}}
  function drawArm() {
    if(activeTab!=='arm')return;const view=prepare($('arm-canvas'));if(!view)return;const {c,w,h}=view,points=M.arm(armQ),end=points[3];
    const total=armBase.l1+armBase.l2,look=[0,0,Math.max(.4,total*.25)],dir=[Math.cos(camera.elev)*Math.cos(camera.az),Math.cos(camera.elev)*Math.sin(camera.az),Math.sin(camera.elev)],right=[-Math.sin(camera.az),Math.cos(camera.az),0],up=vector.cross(dir,right),focal=Math.min(w,h)*1.3;
    const project=point=>{const q=vector.sub(point,look),depth=camera.radius-vector.dot(q,dir);return {x:w/2+focal*vector.dot(q,right)/Math.max(.2,depth),y:h*.52-focal*vector.dot(q,up)/Math.max(.2,depth),depth};};
    const line=(a,b,color,width=1)=>{const aa=project(a),bb=project(b);if(aa.depth<.2||bb.depth<.2)return;c.strokeStyle=color;c.lineWidth=width;c.beginPath();c.moveTo(aa.x,aa.y);c.lineTo(bb.x,bb.y);c.stroke();};
    const bg=c.createLinearGradient(0,0,0,h);bg.addColorStop(0,'#101e2d');bg.addColorStop(1,'#0c121d');c.fillStyle=bg;c.fillRect(0,0,w,h);
    const grid=Math.ceil(total+1);for(let i=-grid;i<=grid;i++){line([i,-grid,0],[i,grid,0],'#263647');line([-grid,i,0],[grid,i,0],'#263647');}
    [[[1.2,0,0],colors.red,'X'],[[0,1.2,0],colors.green,'Y'],[[0,0,1.2],colors.cyan,'Z']].forEach(([q,color,label])=>{line([0,0,0],q,color,2);const pp=project(q);c.fillStyle=color;c.font='bold 12px system-ui';c.fillText(label,pp.x+5,pp.y-5);});
    if(armData.length>1){c.strokeStyle='#53d9d166';c.lineWidth=1.5;c.beginPath();armData.filter((_,i)=>i%3===0).forEach((q,i)=>{const pp=project([q.x,q.y,q.z]);if(!i)c.moveTo(pp.x,pp.y);else c.lineTo(pp.x,pp.y);});c.stroke();}
    const faces=[];
    function prism(a,b,width,color) {const axis=vector.normal(vector.sub(b,a)),u=vector.scale(vector.normal(vector.cross(axis,Math.abs(axis[2])>.9?[0,1,0]:[0,0,1])),width),v=vector.scale(vector.cross(axis,vector.normal(u)),width),corners=[];[a,b].forEach(base=>{[[1,1],[-1,1],[-1,-1],[1,-1]].forEach(([su,sv])=>corners.push(vector.add(base,vector.add(vector.scale(u,su),vector.scale(v,sv)))));});[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]].forEach((indices,i)=>{const projected=indices.map(j=>project(corners[j]));faces.push({kind:'face',points:projected,depth:projected.reduce((s,q)=>s+q.depth,0)/4,color:color[i%color.length]});});}
    prism(points[0],points[1],.15,['#54687d','#3d5269','#718599']);prism(points[1],points[2],.065,['#39938f','#63d6cb','#2f7776']);prism(points[2],points[3],.055,['#7366ab','#afa0ec','#594d91']);
    points.slice(1).forEach((q,i)=>{const pp=project(q);faces.push({kind:'joint',...pp,radius:focal*(i===2?.075:.105)/pp.depth});});
    faces.sort((a,b)=>b.depth-a.depth).forEach(face=>{if(face.depth<.2)return;if(face.kind==='face'){c.beginPath();face.points.forEach((q,i)=>i?c.lineTo(q.x,q.y):c.moveTo(q.x,q.y));c.closePath();c.fillStyle=face.color;c.fill();c.strokeStyle='#b3d7e433';c.lineWidth=1;c.stroke();}else{const gradient=c.createRadialGradient(face.x-face.radius*.3,face.y-face.radius*.3,1,face.x,face.y,face.radius);gradient.addColorStop(0,'#e6edf4');gradient.addColorStop(.45,'#8c9bae');gradient.addColorStop(1,'#334758');c.fillStyle=gradient;c.beginPath();c.arc(face.x,face.y,Math.max(1,face.radius),0,Math.PI*2);c.fill();}});
    const tool=project(end);c.fillStyle=colors.amber;c.font='11px system-ui';c.fillText('TOOL',tool.x+13,tool.y-9);c.fillStyle='#9dafc4';c.font='10px system-ui';c.fillText('Right-handed world · Z up · distances in metres',15,h-18);
    ['x','y','z'].forEach((key,i)=>$('tool-'+key).innerHTML=fmt(end[i])+' <small>m</small>');$('arm-time').innerHTML=fmt(armSteps/60,2)+' <small>s</small>';
    plot('arm-chart',['x','y','z'].map((key,i)=>({label:'Tool '+key.toUpperCase(),color:[colors.red,colors.green,colors.cyan][i],data:armData.filter((_,j)=>j%2===0||j===armData.length-1).map(q=>({x:q.t,y:q[key],tip:`t: ${fmt(q.t)} s\nTool ${key.toUpperCase()}: ${fmt(q[key])} m`}))})),{xLabel:'Illustrative joint-motion time / s',yLabel:'Tool position / m',xRange:[0,Math.max(5,armSteps/60)]});
  }
  $('arm-parameters').addEventListener('submit',e=>e.preventDefault());$('arm-parameters').addEventListener('input',()=>{if(!$('arm-parameters').checkValidity())return;new FormData($('arm-parameters')).forEach((v,k)=>armBase[k]=Number(v));['yaw','shoulder','elbow'].forEach(k=>document.querySelector(`[data-value="${k}"]`).value=fmt(armBase[k],0)+'°');resetArm();});
  $('arm-motion').addEventListener('click',()=>{if(armSteps>=1800)resetArm();armRunning=!armRunning;armAccumulator=0;$('arm-motion').textContent=armRunning?'Ⅱ Pause joint motion':'▶ Demonstrate joint motion';});
  $('arm-camera').addEventListener('click',()=>{camera={az:.85,elev:.48,radius:Math.max(6.5,(armBase.l1+armBase.l2)*2.5)};drawArm();});
  const zoom=amount=>{camera.radius=M.clamp(camera.radius*amount,2,22);drawArm();};$('zoom-in').addEventListener('click',()=>zoom(.85));$('zoom-out').addEventListener('click',()=>zoom(1.18));
  $('arm-canvas').addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY};e.currentTarget.setPointerCapture(e.pointerId);});$('arm-canvas').addEventListener('pointermove',e=>{if(!drag)return;camera.az-=(e.clientX-drag.x)*.008;camera.elev=M.clamp(camera.elev+(e.clientY-drag.y)*.008,.05,1.45);drag={x:e.clientX,y:e.clientY};drawArm();});['pointerup','pointercancel'].forEach(name=>$('arm-canvas').addEventListener(name,()=>drag=null));
  $('arm-canvas').addEventListener('wheel',e=>{e.preventDefault();zoom(Math.exp(e.deltaY*.001));},{passive:false});$('arm-canvas').addEventListener('keydown',e=>{const keys={ArrowLeft:()=>camera.az-=.12,ArrowRight:()=>camera.az+=.12,ArrowUp:()=>camera.elev=M.clamp(camera.elev+.1,.05,1.45),ArrowDown:()=>camera.elev=M.clamp(camera.elev-.1,.05,1.45),'+':()=>zoom(.85),'=':()=>zoom(.85),'-':()=>zoom(1.18)};if(keys[e.key]){e.preventDefault();keys[e.key]();drawArm();}});
  $('export-arm').addEventListener('click',()=>download('mechatronics-arm-kinematics.json',JSON.stringify({schema:'mechatronics-arm-kinematics/v1',evidence:'Illustrative forward kinematics only. No rigid-body dynamics, torque, collision, control-loop stability or hardware validation.',coordinateConvention:'Right-handed world; Z up; yaw about Z; shoulder and relative elbow pitch in radial-Z plane.',jointMotion:'30 s bounded sinusoidal joint demonstration about entered angles; fixed 1/60 s illustrative clock; angle clamping may make this unsuitable as a physical trajectory.',baseParameters:armBase,currentParameters:armQ,currentJointPoints:M.arm(armQ),units:{t:'s',x:'m',y:'m',z:'m',yaw:'deg',shoulder:'deg',elbow:'deg',l1:'m',l2:'m',base:'m'},path:armData},null,2),'application/json'));
  $('export-usd-pose').addEventListener('click',()=>download('mechatronics-arm-pose.usda',window.MechUSD.exportPose(armQ),'text/plain'));
  $('export-usd-animation').addEventListener('click',()=>download('mechatronics-arm-animation.usda',window.MechUSD.exportAnimation(armBase,armData,{timeCodesPerSecond:60,includePath:true}),'text/plain'));
  document.querySelectorAll('.tab').forEach(button=>button.addEventListener('click',()=>{activeTab=button.dataset.tab;document.querySelectorAll('.tab').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-selected',String(b===button));});document.querySelectorAll('.tab-panel').forEach(panel=>panel.classList.toggle('active',panel.id===activeTab));setRunning(false);armRunning=false;armAccumulator=0;$('arm-motion').textContent='▶ Demonstrate joint motion';tooltip.hidden=true;drawTime();drawAnalysis();drawArm();}));
  document.addEventListener('visibilitychange',()=>{if(document.hidden){setRunning(false);armRunning=false;$('arm-motion').textContent='▶ Demonstrate joint motion';$('run-status').textContent='Paused: browser tab hidden';}lastFrame=null;accumulator=0;armAccumulator=0;});
  window.addEventListener('resize',()=>{drawTime();drawAnalysis();drawArm();});
  function frame(now){const elapsed=lastFrame===null?0:Math.min(.1,(now-lastFrame)/1000);lastFrame=now;
    if(running){accumulator+=elapsed*Number($('speed').value);let count=0;while(accumulator>=p.ts&&count<600){if(!sim.step()){setRunning(false);$('run-status').textContent=sim.failed||'Run complete';break;}accumulator-=p.ts;count++;}}
    if(armRunning){armAccumulator+=elapsed;while(armAccumulator>=1/60&&armRunning){armStep();armAccumulator-=1/60;}}
    if(now-lastDraw>45){if(running)drawTime();if(armRunning)drawArm();lastDraw=now;}
    // Draw the last completed step too, after its running flag has cleared.
    if(!running&&sim.t>=p.duration&&$('time').textContent.trim().split(' ')[0]!==fmt(sim.t,2))drawTime();
    if(armSteps===1800 && parseFloat($('arm-time').textContent)!==30)drawArm();requestAnimationFrame(frame);
  }
  resetArm();refreshAnalysis();drawTime();requestAnimationFrame(frame);
}());
