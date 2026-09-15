/* Dependency-free OpenUSD USDA writer for this lab's kinematic arm. MIT. */
/* Syntax: https://openusd.org/release/tut_xforms.html and UsdGeom schemas. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MechUSD=api;}(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const defaults={yaw:25,shoulder:30,elbow:-55,l1:1.2,l2:.9,base:.25};
  function finite(value,label){if(typeof value!=='number'||!Number.isFinite(value))throw Error(`${label} must be a finite number.`);return value;}
  function validateParameters(raw){const p={...raw};for(const key of ['yaw','shoulder','elbow','l1','l2','base'])finite(p[key],key);for(const key of ['l1','l2','base'])if(p[key]<=0)throw Error(`${key} must be positive.`);return p;}
  const number=value=>{finite(value,'USD numeric value');return Object.is(value,-0)?'0':String(value);};
  const tuple=values=>'('+values.map(number).join(', ')+')';
  function validateOptions(raw={}){const timeCodesPerSecond=raw.timeCodesPerSecond===undefined?60:finite(raw.timeCodesPerSecond,'timeCodesPerSecond');if(timeCodesPerSecond<=0)throw Error('timeCodesPerSecond must be positive.');return {timeCodesPerSecond,includePath:raw.includePath!==false};}
  function validateSamples(samples,options){if(!Array.isArray(samples)||samples.length<2)throw Error('Animation requires at least two recorded joint samples.');let previous=-Infinity;return samples.map((sample,index)=>{const out={};for(const key of ['t','yaw','shoulder','elbow'])out[key]=finite(sample[key],`sample ${index} ${key}`);if(out.t<0)throw Error('Sample time must be nonnegative.');out.timeCode=finite(out.t*options.timeCodesPerSecond,`sample ${index} time code`);if(out.timeCode<=previous)throw Error('Sample time codes must be strictly increasing and distinct.');previous=out.timeCode;return out;});}
  function toolPosition(p,q=p){const yaw=q.yaw*Math.PI/180,shoulder=q.shoulder*Math.PI/180,elbow=q.elbow*Math.PI/180,r=p.l1*Math.cos(shoulder)+p.l2*Math.cos(shoulder+elbow);return [r*Math.cos(yaw),r*Math.sin(yaw),p.base+p.l1*Math.sin(shoulder)+p.l2*Math.sin(shoulder+elbow)];}
  function rotation(name,value,key,sign,samples,indent){const pad=' '.repeat(indent),lines=[`${pad}double xformOp:${name} = ${number(value)}`];if(samples)lines.push(`${pad}double xformOp:${name}.timeSamples = {`,...samples.map(q=>`${pad}    ${number(q.timeCode)}: ${number(sign*q[key])},`),`${pad}}`);return lines.join('\n');}
  function cube(name,translation,dimensions,color,indent){const pad=' '.repeat(indent);return `${pad}def Cube "${name}"
${pad}{
${pad}    double size = 1
${pad}    color3f[] primvars:displayColor = [${tuple(color)}]
${pad}    double3 xformOp:translate = ${tuple(translation)}
${pad}    double3 xformOp:scale = ${tuple(dimensions)}
${pad}    uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
${pad}}`;}
  function sphere(name,radius,color,indent){const pad=' '.repeat(indent);return `${pad}def Sphere "${name}"
${pad}{
${pad}    double radius = ${number(radius)}
${pad}    color3f[] primvars:displayColor = [${tuple(color)}]
${pad}}`;}
  function pathGeometry(p,samples){return `    def BasisCurves "ToolPath"
    {
        custom string mechatronics:scope = "Static display of the complete recorded end-effector path; not a collision or motion constraint."
        uniform token type = "linear"
        uniform token wrap = "nonperiodic"
        int[] curveVertexCounts = [${samples.length}]
        point3f[] points = [${samples.map(q=>tuple(toolPosition(p,q))).join(', ')}]
        float[] widths = [0.012] (
            interpolation = "constant"
        )
        color3f[] primvars:displayColor = [(0.325, 0.85, 0.82)]
    }
`;}
  function scene(p,samples,options){const start=samples?samples[0].timeCode:0,end=samples?samples[samples.length-1].timeCode:0;return `#usda 1.0
(
    defaultPrim = "Robot"
    metersPerUnit = 1
    upAxis = "Z"
    timeCodesPerSecond = ${number(options.timeCodesPerSecond)}
    framesPerSecond = ${number(options.timeCodesPerSecond)}
    startTimeCode = ${number(start)}
    endTimeCode = ${number(end)}
    customLayerData = {
        string mechatronicsEvidence = "Illustrative kinematic visual scene. No mass, inertia, collision, articulation physics, controller execution, or hardware validation."
        string mechatronicsSchema = "mechatronics-browser-lab-usda/v1"
        string coordinateConvention = "Right-handed; Z up; metres; joint angles in degrees."
        string animationScope = "${samples?'Recorded sampled joint angles; USD viewers interpolate between samples. Static ToolPath, when present, shows the complete recorded path.':'Current static arm pose; no sampled animation.'}"
    }
)

def Xform "Robot"
{
    custom string mechatronics:model = "Base yaw plus shoulder and relative elbow pitch; link geometry only."
    custom double mechatronics:upperLinkMetres = ${number(p.l1)}
    custom double mechatronics:forearmMetres = ${number(p.l2)}
    custom double mechatronics:baseHeightMetres = ${number(p.base)}
${cube('Base',[0,0,p.base/2],[.3,.3,p.base],[.36,.44,.53],4)}
${samples&&options.includePath?pathGeometry(p,samples):''}
    def Xform "YawJoint"
    {
        double3 xformOp:translate = ${tuple([0,0,p.base])}
${rotation('rotateZ',p.yaw,'yaw',1,samples,8)}
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]

        def Xform "ShoulderJoint"
        {
${rotation('rotateY',-p.shoulder,'shoulder',-1,samples,12)}
            uniform token[] xformOpOrder = ["xformOp:rotateY"]
${sphere('ShoulderVisual',.105,[.65,.71,.77],12)}
${cube('UpperLink',[p.l1/2,0,0],[p.l1,.13,.13],[.325,.85,.82],12)}

            def Xform "ElbowJoint"
            {
                double3 xformOp:translate = ${tuple([p.l1,0,0])}
${rotation('rotateY',-p.elbow,'elbow',-1,samples,16)}
                uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateY"]
${sphere('ElbowVisual',.105,[.65,.71,.77],16)}
${cube('Forearm',[p.l2/2,0,0],[p.l2,.11,.11],[.67,.61,1],16)}

                def Xform "Tool"
                {
                    double3 xformOp:translate = ${tuple([p.l2,0,0])}
                    uniform token[] xformOpOrder = ["xformOp:translate"]
${sphere('ToolVisual',.075,[.97,.75,.4],20)}
                }
            }
        }
    }
}
`;}
  function exportPose(parameters=defaults,rawOptions={}){return scene(validateParameters(parameters),null,validateOptions(rawOptions));}
  function exportAnimation(parameters,samples,rawOptions={}){const p=validateParameters(parameters),options=validateOptions(rawOptions);return scene(p,validateSamples(samples,options),options);}
  return {exportPose,exportAnimation,validateParameters,toolPosition};
}));
