import {evaluate,defaults} from './blend-model.mjs';
// A finite process scenario comparison; neither an industrial optimum nor calibration.
export function suggestPlans(config){
 const initial=evaluate({...structuredClone(config),route:[]});if(!initial.valid)return [];
 const m=initial.mixed,base=defaults(config.family),routes=config.family==='stainless'?[['AOD','LF','VOD','SOFT'],['AOD','LF','SOFT']]:[['LF','VD','SOFT'],['LF','RH','SOFT'],['LF','SOFT']];
 const scenarios=[];for(const route of routes)for(const scale of [.75,1,1.5,2]){const c=structuredClone(config);c.route=route.map(type=>{const original=config.route.find(s=>s.type===type)||base.route.find(s=>s.type===type)||{type,time:20,gasNLmin:260,powderKgMin:0,AlKg:0,oxygenNm3:0,heatKW:0};return{...structuredClone(original),time:Math.min(120,Math.ceil(original.time*scale))};});
  const lf=c.route.find(s=>s.type==='LF');if(lf)lf.AlKg=Math.max(lf.AlKg,m.mass_t*1000*Math.max(0,m.Odiss-(c.targets.Odiss?.[1]??10))/1e6*54/48);
  const blow=c.route.find(s=>['AOD','VOD'].includes(s.type));if(blow){const needKg=Math.max(0,m.C-(c.targets.C?.[1]??m.C))/100*m.mass_t*1000;const oxygenNeed=Math.max(0,needKg*16/12-m.Odiss/1e6*m.mass_t*1000)/1.429/Math.max(.05,1-c.params.crOxygenFraction);blow.oxygenNm3=Math.max(blow.oxygenNm3,oxygenNeed);}
  const r=evaluate(c);if(!r.valid)continue;const deficit=r.checks.reduce((sum,x)=>sum+(x.pass?0:Math.max(x.min-x.value,x.value-x.max,0)/Math.max(.001,x.max)),0);
  scenarios.push({config:c,result:r,score:deficit+(r.capacity?0:100)+(r.phaseValid?0:100),label:route.join(' → ')+` · 时间系数${scale}`});}
 scenarios.sort((a,b)=>(a.result.feasible?0:1)-(b.result.feasible?0:1)||a.score-b.score||a.result.totals.time-b.result.totals.time);
 return scenarios.slice(0,6);
}
