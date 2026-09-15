/* Original educational numerical core. SI units, negative unity feedback. MIT. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.MechMath = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const defaults = Object.freeze({m:1,b:1.2,k:4,kp:18,ki:8,kd:4,tf:0.04,g:1,ts:0.01,limit:30,target:1,disturbance:0,duration:20,logMin:-2,logMax:3,locusMax:8});
  const units = Object.freeze({t:'s',x:'m',v:'m/s',a:'m/s²',u:'N',error:'m',integral:'N',derivative:'m/s',energy:'J',target:'m',omega:'rad/s',magnitude:'dB',phase:'deg',poleReal:'1/s',poleImag:'1/s'});
  const cx = (re=0,im=0) => ({re,im});
  const add = (a,b) => cx(a.re+b.re,a.im+b.im);
  const sub = (a,b) => cx(a.re-b.re,a.im-b.im);
  const mul = (a,b) => cx(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re);
  const div = (a,b) => { const d=b.re*b.re+b.im*b.im; return cx((a.re*b.re+a.im*b.im)/d,(a.im*b.re-a.re*b.im)/d); };
  const abs = a => Math.hypot(a.re,a.im);
  const scale = (a,s) => cx(a.re*s,a.im*s);
  const evaluate = (coeff,z) => coeff.reduce((v,c)=>add(mul(v,z),cx(c)),cx());
  const clamp = (x,lo,hi) => Math.max(lo,Math.min(hi,x));
  function trim(a) { a=a.slice(); while(a.length>1 && a[0]===0) a.shift(); return a; }
  function polynomialRoots(input) {
    const p=trim(input); const n=p.length-1;
    if(!n) return [];
    if(p[p.length-1]===0) return [cx(0),...polynomialRoots(p.slice(0,-1))];
    if(n===1) return [cx(-p[1]/p[0])];
    if(n===2) {
      const [a,b,c]=p, d=b*b-4*a*c;
      if(d<0) return [cx(-b/(2*a),Math.sqrt(-d)/(2*Math.abs(a))),cx(-b/(2*a),-Math.sqrt(-d)/(2*Math.abs(a)))];
      const q=-0.5*(b+(b>=0?1:-1)*Math.sqrt(d));
      return q===0 ? [cx(0),cx(0)] : [cx(q/a),cx(c/q)];
    }
    // Scale the root variable before Aberth iteration to limit coefficient spread.
    const monic=p.map(v=>v/p[0]);
    const radius=Math.max(1,...monic.slice(1).map((v,i)=>Math.pow(Math.abs(v),1/(i+1))));
    const q=monic.map((v,i)=>v/Math.pow(radius,i));
    const dq=q.slice(0,-1).map((v,i)=>v*(n-i));
    let roots=Array.from({length:n},(_,i)=>cx(1.2*Math.cos(2*Math.PI*(i+0.27)/n),1.2*Math.sin(2*Math.PI*(i+0.27)/n)));
    for(let iter=0;iter<700;iter++) {
      let maxStep=0;
      roots=roots.map((z,i)=> {
        const f=evaluate(q,z), df=evaluate(dq,z);
        if(abs(f)<1e-15) return z;
        if(abs(df)<1e-20) return add(z,cx(1e-8,1e-8));
        const newton=div(f,df);
        let sum=cx();
        roots.forEach((other,j)=> { if(i!==j) { const delta=sub(z,other); if(abs(delta)>1e-20) sum=add(sum,div(cx(1),delta)); } });
        const den=sub(cx(1),mul(newton,sum));
        const step=abs(den)>1e-20?div(newton,den):newton;
        maxStep=Math.max(maxStep,abs(step));
        return sub(z,step);
      });
      if(maxStep<1e-12) break;
    }
    return roots.map(z=>cx(z.re*radius,Math.abs(z.im*radius)<1e-8?0:z.im*radius)).sort((a,b)=>a.re-b.re || a.im-b.im);
  }
  function validate(raw) {
    const p={...defaults,...raw};
    for(const key of Object.keys(defaults)) if(!Number.isFinite(p[key])) throw Error(`${key} must be finite.`);
    for(const key of ['m','b','k','tf','ts','limit','duration','locusMax']) if(p[key]<=0) throw Error(`${key} must be positive.`);
    for(const key of ['kp','ki','kd','g']) if(p[key]<0) throw Error(`${key} must be nonnegative.`);
    if(p.ts<0.001 || p.ts>0.2) throw Error('Sample period must be 0.001–0.2 s.');
    if(p.duration>120) throw Error('Run duration is limited to 120 s.');
    if(p.logMin>=p.logMax || p.logMin < -5 || p.logMax > 6) throw Error('Frequency exponents must increase within −5 to 6.');
    if(p.m<0.02 || p.b>100 || p.k>1000 || p.kp>10000 || p.ki>10000 || p.kd>1000 || p.tf<0.001 || p.g>1000 || p.locusMax>1000) throw Error('Parameters exceed the educational model bounds.');
    return p;
  }
  function controller(p) {
    // Only include states for terms that actually exist. A disabled D term has no filter pole.
    if(p.kd>0 && p.ki>0) return {num:trim([p.kp*p.tf+p.kd,p.kp+p.ki*p.tf,p.ki]),den:[p.tf,1,0]};
    if(p.kd>0) return {num:trim([p.kp*p.tf+p.kd,p.kp]),den:[p.tf,1]};
    if(p.ki>0) return {num:trim([p.kp,p.ki]),den:[1,0]};
    return {num:[p.kp],den:[1]};
  }
  function convolution(a,b) { const c=Array(a.length+b.length-1).fill(0); a.forEach((x,i)=>b.forEach((y,j)=>c[i+j]+=x*y)); return c; }
  function characteristic(p,g=p.g) {
    const c=controller(p), den=convolution([p.m,p.b,p.k],c.den), out=den.slice(), offset=den.length-c.num.length;
    c.num.forEach((v,i)=>out[i+offset]+=g*v);
    return trim(out);
  }
  const poles = (p,g=p.g) => polynomialRoots(characteristic(p,g));
  function poleStatus(roots) { const right=Math.max(...roots.map(r=>r.re)); return right>1e-7?'unstable':right < -1e-7?'stable':'boundary / numerically near boundary'; }
  function loop(p,w,g=p.g) {
    const s=cx(0,w), c=controller(p);
    return scale(div(evaluate(c.num,s),mul(evaluate(c.den,s),evaluate([p.m,p.b,p.k],s))),g);
  }
  function frequency(p,n=600) {
    let previous=0;
    return Array.from({length:n},(_,i)=> {
      const w=Math.pow(10,p.logMin+(p.logMax-p.logMin)*i/(n-1)), z=loop(p,w), magnitude=abs(z);
      let phase=Math.atan2(z.im,z.re)*180/Math.PI;
      if(i) { while(phase-previous>180) phase-=360; while(phase-previous < -180) phase+=360; }
      previous=phase;
      return {omega:w,re:z.re,im:z.im,magnitude: magnitude?20*Math.log10(magnitude):null,phase:magnitude?phase:null};
    });
  }
  function margins(data) {
    const gainCrossings=[],phaseCrossings=[];
    for(let i=1;i<data.length;i++) {
      const a=data[i-1], b=data[i];
      if(a.magnitude===null || b.magnitude===null) continue;
      const interpolate=(t,key)=>a[key]+t*(b[key]-a[key]);
      const omega=t=>Math.exp(Math.log(a.omega)+t*Math.log(b.omega/a.omega));
      if(a.magnitude!==b.magnitude && ((a.magnitude>=0 && b.magnitude<0)||(a.magnitude<=0 && b.magnitude>0)||(i===data.length-1 && b.magnitude===0))) {
        const t=-a.magnitude/(b.magnitude-a.magnitude), phase=interpolate(t,'phase');
        gainCrossings.push({omega:omega(t),phase,phaseMargin:180+phase});
      }
      for(let level=-900;level<=900;level+=360) if(a.phase!==b.phase && ((a.phase>=level && b.phase<level)||(a.phase<=level && b.phase>level)||(i===data.length-1 && b.phase===level))) {
        const t=(level-a.phase)/(b.phase-a.phase);
        phaseCrossings.push({omega:omega(t),phase:level,gainMarginDb:-interpolate(t,'magnitude')});
      }
    }
    return {gainCrossings,phaseCrossings,note:'Interpolated finite-range crossings; all detected crossings are listed. Missing crossings do not prove infinite margin. Margins alone do not prove stability.'};
  }
  function rootLocus(p,n=181) {
    const max=Math.max(p.locusMax,p.g), open=poles(p,0), rows=[];
    for(let i=0;i<n;i++) {
      // Quadratic gain spacing gives useful resolution near the origin.
      const g=max*Math.pow(i/(n-1),2), rr=poles(p,g);
      rows.push({g,poles:rr});
    }
    return {rows,open,zeros:polynomialRoots(controller(p).num),current:poles(p),max};
  }
  class Simulation {
    constructor(raw) { this.p=validate(raw); this.t=0; this.steps=0; this.x=0; this.v=0; this.integral=0; this.derivative=0; this.prevX=0; this.u=0; this.data=[]; this.failed=null; this.sample(); this.record(); }
    sample() {
      const p=this.p, error=p.target-this.x;
      if(p.kd>0) { const a=Math.exp(-p.ts/p.tf); this.derivative=a*this.derivative+(1-a)*(this.x-this.prevX)/p.ts; }
      else this.derivative=0;
      this.prevX=this.x;
      const raw=p.g*(p.kp*error+this.integral-p.kd*this.derivative);
      this.u=clamp(raw,-p.limit,p.limit);
      // Conditional integration: freeze while the error would push further into saturation.
      const pushing=(raw>=p.limit && error>0)||(raw<=-p.limit && error<0);
      if(p.ki>0 && p.g>0 && !pushing) this.integral+=p.ki*error*p.ts;
    }
    record() { const p=this.p; this.data.push({t:this.t,x:this.x,v:this.v,a:(this.u+p.disturbance-p.b*this.v-p.k*this.x)/p.m,u:this.u,error:p.target-this.x,integral:this.integral,derivative:this.derivative,energy:0.5*p.m*this.v*this.v+0.5*p.k*this.x*this.x,target:p.target}); }
    step() {
      if(this.failed || this.t>=this.p.duration-1e-10) return false;
      const p=this.p, count=Math.max(4,Math.ceil(p.ts/Math.min(0.0025,0.1/Math.max(Math.sqrt(p.k/p.m),p.b/p.m)))), h=p.ts/count;
      const f=(x,v)=>[v,(this.u+p.disturbance-p.b*v-p.k*x)/p.m];
      for(let j=0;j<count;j++) {
        const a=f(this.x,this.v), b=f(this.x+h*a[0]/2,this.v+h*a[1]/2),c=f(this.x+h*b[0]/2,this.v+h*b[1]/2),d=f(this.x+h*c[0],this.v+h*c[1]);
        this.x+=h*(a[0]+2*b[0]+2*c[0]+d[0])/6; this.v+=h*(a[1]+2*b[1]+2*c[1]+d[1])/6;
      }
      this.steps++; this.t=this.steps*p.ts;
      if(!Number.isFinite(this.x) || !Number.isFinite(this.v) || Math.abs(this.x)>1e5 || Math.abs(this.v)>1e6) { this.failed='Model exceeded the numerical display envelope; run stopped.'; return false; }
      this.sample(); this.record(); return true;
    }
    run() { while(this.step()) {} return this.data; }
  }
  function arm({yaw=25,shoulder=30,elbow=-55,l1=1.2,l2=0.9,base=0.25}) {
    const y=yaw*Math.PI/180,s=shoulder*Math.PI/180,e=elbow*Math.PI/180;
    const point=(r,z)=>[r*Math.cos(y),r*Math.sin(y),z];
    return [[0,0,0],[0,0,base],point(l1*Math.cos(s),base+l1*Math.sin(s)),point(l1*Math.cos(s)+l2*Math.cos(s+e),base+l1*Math.sin(s)+l2*Math.sin(s+e))];
  }
  return {defaults,units,cx,add,sub,mul,div,abs,evaluate,polynomialRoots,validate,controller,characteristic,poles,poleStatus,loop,frequency,margins,rootLocus,Simulation,arm,clamp};
}));
