import {evaluate,SPECIES_UNITS} from './bed-model.mjs';
const known=x=>typeof x==='number'&&Number.isFinite(x);
const names={C:'碳',S:'硫',TO:'总氧',Odiss:'溶解氧',H:'氢',N:'氮',P:'磷',Cu:'铜',Sn:'锡'};
/** Goal-based review of one explicit design. This does not optimize uncalibrated equipment. */
export function summarizePlan(config,result=evaluate(config)){
 if(!result.valid)return {valid:false,statusLabel:'请先修正设计输入',issues:result.errors,objectives:[],flowScenarios:[],requiredInputs:[]};
 const stages=result.stages,objectives=Object.entries(config.targets||{}).map(([key,target])=>{
  const inlet=config.inlet[key],final=result.final[key],pass=known(final)?final<=target:null,indices=config.modules.flatMap((m,i)=>m.species===key?[i]:[]),scale=SPECIES_UNITS[key]==='ppm'?.001:10;
  return {key,label:names[key]||key,unit:SPECIES_UNITS[key],inlet,target,final,status:pass===null?'unknown':pass?'pass':'fail',gap:known(final)?Math.max(0,final-target):null,removalNeededKgT:Math.max(0,inlet-target)*scale,predictedRemovalKgT:known(final)?(inlet-final)*scale:null,stages:indices};
 });
 const required=objectives.filter(x=>x.inlet>x.target),covered=required.filter(x=>x.stages.length>0),missing=required.filter(x=>!x.stages.length).map(x=>x.key),issues=[],requiredInputs=[];
 for(const x of objectives){if(x.status==='fail')issues.push(`${x.label}终点仍高于指定上限`);if(x.status==='unknown')issues.push(`${x.label}终点缺少可用预测参数`);}
 for(const key of missing)requiredInputs.push(`需要承担${names[key]||key}控制任务的处理区段或调整来料／目标`);
 for(const [i,m]of config.modules.entries()){
  if(m.species&&(!known(m.kPerMin)||!known(m.equilibrium)))requiredInputs.push(`第${i+1}区 ${m.type} 的适用速率系数与极限浓度`);
  if(['VD','RH','RHOB','VAD','VOD'].includes(m.type)&&m.species&&m.sealedVacuum!==true)requiredInputs.push(`第${i+1}区的密封真空／循环能力；开放床无法直接获得原设备真空效果`);
  if(m.heatingEnabled!==false&&m.heatingMethod&&m.heatingMethod!=='none'&&(!known(m.heatEfficiency)||!known(m.heatKW)&&m.heatingMethod!=='powder'))requiredInputs.push(`第${i+1}区补热的输入功率／热效率边界`);
 }
 if(result.totals.lossKW===null)requiredInputs.push('适用工况的覆盖面、裸露面和耐材接触热流密度');
 if(!known(config.cpKJkgK))requiredInputs.push('钢液比热');
 if(!known(config.liquidusC))requiredInputs.push('当前来料液相线温度');
 const targetOutletC=known(config.targetOutletC)?config.targetOutletC:null,finalC=known(result.final.T)?result.final.T:null,gapK=targetOutletC!==null&&finalC!==null?Math.max(0,targetOutletC-finalC):null;
 if(gapK>0)issues.push('出口温度低于指定目标');
 if(result.phaseValid===false)issues.push('存在低于液相线的区段，液态反应模型失效');
 const chemicalPass=objectives.length>0&&objectives.every(x=>x.status==='pass'),thermalPass=finalC!==null&&result.phaseValid===true&&(targetOutletC===null||finalC>=targetOutletC);
 const statusLabel=chemicalPass&&thermalPass?'当前设定下计算目标满足，仍需工业验证':chemicalPass?'成分计算目标满足，热边界或温度目标待核':'当前方案存在目标差距或未知项';
 const flowScenarios=[.5,1,1.5].map(factor=>{
  const c={...config,flowTph:config.flowTph*factor},r=factor===1?result:evaluate(c);
  if(!r.valid)return {flowTph:c.flowTph,valid:false,errors:r.errors};
  return {flowTph:c.flowTph,valid:true,throughMin:r.geometry.residenceMin,passCount:r.checks.filter(x=>x.pass===true).length,failCount:r.checks.filter(x=>x.pass===false).length,unknownCount:r.checks.filter(x=>x.pass===null).length,finalT:r.final.T,phaseValid:r.phaseValid};
 });
 const overlays={heating:config.modules.filter(m=>m.heatingEnabled===true||m.heatingEnabled!==false&&m.heatingMethod&&m.heatingMethod!=='none').length,skimming:config.modules.filter(m=>m.skimmingEnabled===true).length,blowing:config.modules.filter(m=>m.blowingMode&&m.blowingMode!=='none'||m.blowingMode===undefined&&m.gas&&m.gas!=='none').length};
 return {valid:true,statusLabel,routeLabel:config.modules.map(m=>m.type).join(' → ')||'仅连续输送',flow:{flowTph:config.flowTph,velocityMps:result.geometry.velocityMps,volumeFlowM3h:result.geometry.flowM3h,throughMin:result.geometry.residenceMin,allocatedLengthM:config.modules.reduce((s,m)=>s+m.lengthM,0),bedLengthM:config.geometry.lengthM,basis:'u=ṁ/(ρA); τ=L/u; parallel operations add no serial time'},objectives,coverage:{required:required.length,covered:covered.length,missing},capability:{knownLimitTph:result.totals.throughputLimitTph,unknown:result.totals.unknownCapacity,confidence:'conditional',limitBasis:'local_segment_targets_not_global_optimum'},resources:{...result.totals},thermal:{targetOutletC,finalC,gapK,requiredAdditionalDeliveredKW:gapK!==null&&known(config.cpKJkgK)?gapK*config.flowTph*1000/3600*config.cpKJkgK:null},overlays,flowScenarios,issues,requiredInputs:[...new Set(requiredInputs)],assumptions:['流量情景保持现有气、粉、扒渣、功率设定不变，只运行现有条件模型。','局部能力上限不是全床最优产能；多个同元素区段的串联效果应核对最终目标表。','增加喷吹、扒渣或加热开关不自动产生未经标定的化学效率。']};
}
