// SI heat balance; kW and kJ are used consistently. No CFD or equipment calibration.
export const SIGMA=5.670374419e-8;
export const POWDERS={al:{name:'铝粉 → Al₂O₃',heat:31.05,o2:.623,product:1.889,label:'Al₂O₃'},si:{name:'硅粉 → SiO₂',heat:32.43,o2:.798,product:2.139,label:'SiO₂'},carbon:{name:'碳粉 → CO',heat:9.20,o2:.933,product:2.332,label:'CO'}};
export const defaults=()=>({mode:'continuous',L:6,W:1,depth:.35,rho:7000,cp:.75,Tin:1600,liquidus:1500,Ta:25,Trad:200,flow:20,minutes:20,target:0,bare:.02,slagDepth:.06,slagK:1.2,slagEps:.85,steelEps:.8,hTop:10,hSteel:1000,workD:.2,workK:2.5,insD:.1,insK:.4,outerH:10,outerEps:.8,extraKW:5,startupKWh:0,selected:'induction',heatLength:6,indKWm:80,indEta:.75,indAux:5,plasmaN:2,plasmaKW:250,plasmaEta:.55,plasmaAux:8,powder:'al',powderDose:3,powderEta:.35,conversion:.9,oxygen:3,o2Util:.8,powderAux:3,extraMJ:0,price:.7});
const finite=x=>Number.isFinite(x);
export function validate(s){const e=[];for(const [k,v] of Object.entries(defaults()))if(typeof v==='number'&&!finite(s[k]))e.push(`${k} 需为有限数值`);if(e.length)return e;
 const bounds={L:[.2,100],W:[.1,10],depth:[.05,3],rho:[5000,8500],cp:[.4,1.5],Tin:[1400,1750],Ta:[-20,200],Trad:[-20,1750],flow:[.1,1000],minutes:[.1,180],target:[-100,100],bare:[0,1],slagDepth:[.001,.5],slagK:[.1,10],slagEps:[.01,1],steelEps:[.01,1],hTop:[0,100],hSteel:[10,10000],workD:[.01,1],workK:[.1,100],insD:[0,1],insK:[.02,20],outerH:[0,100],outerEps:[.01,1],extraKW:[0,5000],startupKWh:[0,5000],heatLength:[0,100],indKWm:[0,2000],indEta:[.01,1],indAux:[0,500],plasmaN:[0,20],plasmaKW:[0,5000],plasmaEta:[.01,1],plasmaAux:[0,500],powderDose:[0,50],powderEta:[0,1],conversion:[0,1],oxygen:[0,100],o2Util:[0,1],powderAux:[0,500],extraMJ:[0,50],price:[0,10]};
 for(const[k,[lo,hi]]of Object.entries(bounds))if(s[k]<lo||s[k]>hi)e.push(`${k} 应在 ${lo}–${hi} 范围内`);
 if(s.liquidus<1300||s.liquidus>1600)e.push('液相线温度应在1300–1600°C范围内');
 if(s.Tin<s.liquidus||s.Tin+s.target<s.liquidus||s.Tin+s.target>1800)e.push('初始及目标温度须在所设液相线至1800°C之间');
 if(s.o2Util<=0)e.push('氧利用率必须大于0');
 if(s.mode==='continuous'&&geometry(s).residence>180)e.push('平均停留时间超过180 min，请提高处理量或减小槽内存量（超出本页核算范围）');
 if(!Number.isInteger(s.plasmaN))e.push('等离子装置数量需为整数');
 if(s.Trad>s.Tin)e.push('辐射环境温度不能高于入口钢温（本页限定冷却边界）');
 if(!['continuous','batch'].includes(s.mode)||!['none','induction','plasma','powder'].includes(s.selected)||!POWDERS[s.powder])e.push('模式或加热装置无效');
 return e;}
export function geometry(s){const top=s.L*s.W,wall=2*(s.L+s.W)*s.depth,volume=top*s.depth,mass=volume*s.rho;return{top,wall,bottom:top,contact:wall+top,volume,mass,tonnes:mass/1000,residence:mass/(s.flow*1000/60)};}
function outward(T,Ta,Tr,h,eps){return h*(T-Ta)+eps*SIGMA*((T+273.15)**4-(Tr+273.15)**4);}
// Root enforces conduction = convection + radiation at the exposed solid surface.
export function surfaceBalance(T,R,Ta,Tr,h,eps){let lo=Math.min(T,Ta,Tr),hi=Math.max(T,Ta,Tr);for(let i=0;i<48;i++){const mid=(lo+hi)/2;if((T-mid)/R-outward(mid,Ta,Tr,h,eps)>0)lo=mid;else hi=mid;}const Ts=(lo+hi)/2;return{Ts,q:(T-Ts)/R,residual:(T-Ts)/R-outward(Ts,Ta,Tr,h,eps)};}
export function losses(s,T=s.Tin,g=geometry(s)){const R=1/s.hSteel+s.workD/s.workK+s.insD/s.insK;
 const wall=surfaceBalance(T,R,s.Ta,s.Ta,s.outerH,s.outerEps),slag=surfaceBalance(T,1/s.hSteel+s.slagDepth/s.slagK,s.Ta,s.Trad,s.hTop,s.slagEps);
 const bareFlux=outward(T,s.Ta,s.Trad,s.hTop,s.steelEps)/1000;
 const parts={wall:wall.q*g.wall/1000,bottom:wall.q*g.bottom/1000,slag:slag.q*g.top*(1-s.bare)/1000,bare:bareFlux*g.top*s.bare,extra:s.extraKW};
 return{...parts,total:Object.values(parts).reduce((a,b)=>a+b,0),bareFlux,slagFlux:slag.q/1000,wallFlux:wall.q/1000,slagTs:slag.Ts,shellTs:wall.Ts,workHotT:T-wall.q/s.hSteel,workColdT:T-wall.q*(1/s.hSteel+s.workD/s.workK),residual:Math.max(Math.abs(wall.residual),Math.abs(slag.residual))};}
export function powderSpecific(s){const p=POWDERS[s.powder],requested=s.powderDose,conversion=requested>0?Math.min(s.conversion,s.oxygen*s.o2Util/(requested*p.o2)):0;const reactionMJ=requested*conversion*p.heat,netMJ=Math.max(0,reactionMJ*s.powderEta-requested*s.extraMJ);return{conversion,reactionMJ,netMJ,netKWh:netMJ/3.6,o2Need:requested*s.conversion*p.o2/s.o2Util,o2Reacted:requested*conversion*p.o2,reacted:requested*conversion,unreacted:requested*(1-conversion),product:requested*conversion*p.product,productLabel:p.label,netPerKg:requested>0?netMJ/requested:Math.max(0,p.heat*s.conversion*s.powderEta-s.extraMJ)};}
function source(s,g,type){const durationH=s.mode==='batch'?s.minutes/60:g.residence/60,tonnes=s.mode==='batch'?g.tonnes:s.flow*durationH,pow=powderSpecific(s);let main=0,aux=0,deposited=0;
 if(type==='induction'){main=s.indKWm*Math.min(s.L,s.heatLength);aux=main>0?s.indAux:0;deposited=main*s.indEta;}
 if(type==='plasma'){main=s.plasmaN*s.plasmaKW;aux=main>0?s.plasmaAux:0;deposited=main*s.plasmaEta;}
 if(type==='powder'){deposited=pow.netKWh*tonnes/durationH;aux=s.powderDose>0?s.powderAux:0;}
 return{main,aux,deposited,input:main+aux,durationH,tonnes,electricKWh:(main+aux)*durationH,kWhT:(main+aux)*durationH/tonnes,powder:type==='powder'?s.powderDose*tonnes:0,oxygen:type==='powder'?s.oxygen*tonnes:0};}
export function run(s,type=s.selected){const errors=validate(s);if(errors.length)return{errors};const g=geometry(s),src=source(s,g,type),initial=losses(s,s.Tin,g),N=240,dt=src.durationH*3600/N,capacity=g.mass*s.cp,preheatPower=s.startupKWh/src.durationH;
 let T=s.Tin,lossKJ=0,curve=[{x:0,T}],parts={wall:0,bottom:0,slag:0,bare:0,extra:0},limited=false;
 for(let i=0;i<N;i++){const q1=losses(s,T,g),d1=(src.deposited-q1.total-preheatPower)/capacity;const mid=T+d1*dt/2,q2=losses(s,mid,g),next=T+(src.deposited-q2.total-preheatPower)*dt/capacity;
  if(next<s.liquidus||next>1800){limited=true;break;}T=next;lossKJ+=q2.total*dt;for(const k in parts)parts[k]+=q2[k]*dt/3600;if((i+1)%8===0)curve.push({x:(i+1)/N*(s.mode==='batch'?s.minutes:s.L),T});}
 const delta=T-s.Tin,stored=g.mass*s.cp*delta/3600,lossKWh=lossKJ/3600,residual=src.deposited*src.durationH-lossKWh-s.startupKWh-stored;
 return{errors:[],type,g,src,initial,T,delta,stored,lossKWh,parts,curve,limited,residual,thermalEfficiency:type==='induction'?s.indEta:type==='plasma'?s.plasmaEta:type==='powder'?s.powderEta*powderSpecific(s).conversion:0};}
// Monotone bisection sizes effective bath heat for a specified outlet/batch target.
export function required(s){const base=run(s,'none');if(base.errors.length)return null;const g=base.g,durationH=base.src.durationH,targetT=s.Tin+s.target;
 const energy=g.mass*s.cp*s.target/3600;
 // Iterated distributed heat source; same heat-loss physics and integration as run().
 function final(power){let T=s.Tin,dt=durationH*3600/240;for(let i=0;i<240;i++){const d=(power-losses(s,T,g).total-s.startupKWh/durationH)/(g.mass*s.cp);T+=(power-losses(s,T+d*dt/2,g).total-s.startupKWh/durationH)*dt/(g.mass*s.cp);}return T;}
 let lo=0,hi=100;if(final(lo)>=targetT)return{bathKW:0,energy,achievableWithoutHeat:true};while(final(hi)<targetT&&hi<1e7)hi*=2;for(let i=0;i<34;i++){const mid=(lo+hi)/2;if(final(mid)<targetT)lo=mid;else hi=mid;}const bathKW=(lo+hi)/2,tonnes=base.src.tonnes,p=POWDERS[s.powder],netPerKg=Math.max(0,p.heat*s.conversion*s.powderEta-s.extraMJ),powderKg=netPerKg>0?bathKW*durationH*3.6/netPerKg:null,powderPerT=powderKg===null?null:powderKg/tonnes;
 return{bathKW,energy,achievableWithoutHeat:false,indKW:bathKW/s.indEta,indKWm:Math.min(s.L,s.heatLength)>0?bathKW/s.indEta/Math.min(s.L,s.heatLength):null,plasmaKW:bathKW/s.plasmaEta,powderPerT,oxygenPerT:powderPerT===null?null:powderPerT*s.conversion*p.o2/s.o2Util};}
export function assess(s){const errors=validate(s);if(errors.length)return{errors};const rows=['none','induction','plasma','powder'].map(t=>run(s,t)),selected=rows.find(r=>r.type===s.selected),baseline=rows[0],req=required(s),powder=powderSpecific(s),warnings=[];
 if(rows.some(x=>x.limited))warnings.push('部分曲线达到所设液相线或超出1800°C，已截断并停止末温核算；本页不计算凝固潜热与过热区。液相线默认1500°C为教学值，应按具体钢种修改。');
 if(s.heatLength>s.L)warnings.push('铺设长度超过槽长，已按槽长限制有效铺设段。');
 if(s.startupKWh>0)warnings.push('已加入独立耐材蓄热负荷；这是用户给定热量，并未求解耐材瞬态温度场。');
 if(s.mode==='continuous')warnings.push('连续模式采用一维均匀分布热源的活塞流近似；未求局部热点、短路流或电磁耦合。');
 if(s.powderDose>0&&powder.conversion+1e-8<s.conversion)warnings.push('当前供氧不足，喷粉反应完成率已被氧量上限约束。');
 if(s.powder==='carbon')warnings.push('碳粉只按生成CO计热，未把后燃CO₂热量直接记入钢液。');
 return{errors:[],rows,selected,baseline,req,powder,warnings};}
