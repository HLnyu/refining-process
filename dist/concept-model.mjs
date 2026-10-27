export const TASKS=[
 ['receive','接收与均化','TAP,AR,TD','来料波动、携渣与混合边界'],
 ['slag','挡渣与改渣','TAP,SKIM,LF','渣量、渣系与排渣去向'],
 ['decarb','脱碳','RH,RHOB,AODVOD','供氧、碳氧平衡及合金氧化'],
 ['dephos','脱磷','','氧势、碱度、温度与回磷；需专项补充证据'],
 ['desulfur','脱硫','LF,POWDER','氧活度、渣容量与界面传质'],
 ['deoxid','脱氧','LF,WIRE','脱氧产物、收得率与总氧区别'],
 ['degas','脱气','RH,VD,VAD','密封、压力、传质与连续进出钢'],
 ['alloy','合金化与喂丝','LF,CAS,WIRE','溶解、混匀、收得率与残余元素'],
 ['clean','夹杂调控与去除','SOFT,TD,WIRE','变性、上浮、捕集与再卷渣'],
 ['thermal','温度调节','LF,CASOB,VAD,TDHEAT','功率、热效率、损失与温度窗口'],
 ['buffer','缓冲与分流','TD,TRANSFER','液位、短路、流量与钢种切换'],
 ['cast','凝固与后处理接口','CC,INGOT,VIMESRVAR,ROLLHT','凝固及下游设备独立边界'],
 ['custom','自定义构想','','写下尚无成熟设备对应的新机制']
].map(([id,name,refs,question])=>({id,name,refs:refs?refs.split(','):[],question}));
export const AUX=['顶吹 Ar','顶吹 O₂','底吹 Ar','底吹 N₂','喷粉','喂丝','扒渣','抽真空','电磁搅拌','感应补热','等离子补热','电弧补热','化学补热','冷却','测温／取样','在线成分检测','保护气罩'];
export const LEVELS=['纯概念，待论证','跨设备迁移构想','有论文或模拟支持','已有工业参考'];
export const STATUSES=['待研究','保留','修改','暂缓','淘汰'];
export const uid=()=>globalThis.crypto.randomUUID();
export function makeZone(task='receive'){const t=TASKS.find(x=>x.id===task)||TASKS[0];return{id:uid(),task:t.id,name:t.name,length:1.5,lane:'main',anchor:null,reference:t.refs[0]||'',aux:[],level:LEVELS[0],status:STATUSES[0],effect:'',question:t.question,evidence:''};}
export function makePlan(starter=false){return{id:uid(),name:starter?'多功能床 · 初始草图':'未命名构想',feed:'钢水来源、流量与成分范围待填写',product:'目标钢种与终点要求待确定',idea:'探索连续主流＋局部功能区；允许支路与循环构想',zones:starter?['receive','desulfur','clean','thermal','buffer'].map(makeZone):[]};}
export function active(z){return !['暂缓','淘汰'].includes(z.status);}
export function summarize(plan){const zones=plan.zones.filter(active), main=zones.filter(x=>x.lane==='main'),other=zones.filter(x=>x.lane!=='main'),tasks=new Set(zones.map(x=>x.task));const issues=[];
 if(!zones.length)issues.push('尚未安排功能区：先从任务库添加一个构想。');
 if(tasks.has('decarb')&&tasks.has('deoxid'))issues.push('脱碳与最终脱氧并存：论证顺序、供氧边界及脱氧剂的重复氧化。');
 if(tasks.has('dephos')&&tasks.has('desulfur'))issues.push('脱磷与脱硫并存：需分段论证氧势、渣系隔离、排渣和回磷／回硫。');
 if(zones.some(x=>x.task==='degas'||x.aux.includes('抽真空')))issues.push('真空功能：连续进出钢的密封、压差液位、漏气与抽气能力尚待论证。');
 if(zones.some(x=>x.aux.includes('底吹 N₂')))issues.push('使用底吹 N₂：检查产品氮指标与增氮风险，不自动判定可用于低氮钢。');
 if(zones.some(x=>x.aux.includes('化学补热')))issues.push('化学补热：补齐反应物、独立氧预算、产物夹杂与净热量核算。');
 for(const z of other){if(!z.anchor||!main.some(x=>x.id===z.anchor))issues.push(`${z.name}：尚未连接一个有效主流区段。`);}
 if(other.length)issues.push('支路／循环为拓扑草图：需补充分流比例、驱动力、回流及混合守恒，当前不计算分支流量。');
 issues.push('所有方案均需补充截面、流量、温度与成分边界；占用长度本身不能给出处理时间或脱除率。');
 return{zones,main,other,tasks:[...tasks],mainLength:main.reduce((s,x)=>s+x.length,0),otherLength:other.reduce((s,x)=>s+x.length,0),issues};}
export function validatePlan(p){
 if(!p||typeof p!=='object'||typeof p.id!=='string'||typeof p.name!=='string'||!p.name.trim()||p.name.length>200||!Array.isArray(p.zones)||p.zones.length>200)throw Error('方案格式不正确，最多支持 200 个模块。');
 for(const k of ['feed','product','idea'])if(typeof p[k]!=='string'||p[k].length>10000)throw Error('设计意图格式不正确。');
 const ids=new Set();for(const z of p.zones){if(!z||typeof z.id!=='string'||ids.has(z.id))throw Error('模块编号重复或缺失。');ids.add(z.id);
 if(!TASKS.some(x=>x.id===z.task)||!['main','side','cycle'].includes(z.lane)||!LEVELS.includes(z.level)||!STATUSES.includes(z.status))throw Error('模块任务、路径或状态无效。');
 if(!Number.isFinite(z.length)||z.length<.5||z.length>3||!Number.isInteger(z.length*2))throw Error('模块长度必须为 0.5–3 m，步长 0.5 m。');
 if(!Array.isArray(z.aux)||z.aux.some(x=>!AUX.includes(x)))throw Error('辅助方式无效。');
 for(const k of ['name','reference','effect','question','evidence'])if(typeof z[k]!=='string'||z[k].length>10000)throw Error('模块文字格式不正确。');
 if(z.anchor!==null&&typeof z.anchor!=='string')throw Error('连接区段无效。');
 }return p;
}
