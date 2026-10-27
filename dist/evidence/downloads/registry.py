"""Formula, equipment, grade-family and coverage registries. No invented calibration."""
import json

def j(x):return json.dumps(x,ensure_ascii=False)
MODELS=[]
def model(i,name,eq,inputs,units,src,derivation,domain,impl,status='implemented_unvalidated'):
    MODELS.append(dict(model_id=i,name=name,equation=eq,inputs_json=j(inputs),output_units=units,
        source_ids_json=j(src),derivation=derivation,domain=domain,status=status,implementation=impl))
model('M01','标况气量到炉内实际气量','Q=QN*(T/TN)*(pN/p)', ['QN_m3_s','T_K','p_abs_Pa','TN_K','pN_Pa'],'m3/s',[], '理想气体状态方程pQ=nRT。N状态必须由输入指定。','单相理想气体；未包括气泡滑移、CO生成及传热非平衡。','gas_actual')
model('M02','气体膨胀的理想机械功','P=n_dot*R*T*ln((p_surface+rho*g*H)/p_surface); eps_mean=P/M',['QN_m3_s','T_K','p_surface_Pa','rho','H','M','TN','pN'],'W; W/kg',['S02'],'n_dot=pN*QN/(R*TN)，沿静压积分可逆等温膨胀功。局部界面耗散不是全包平均功率。','表面绝压>0；忽略气体显热与各处能量耗散分配。','gas_power')
model('M03','Higbie界面更新传质系数','k=2*sqrt(D/(pi*t_contact))=2*sqrt(D*U/(pi*L))',['D_m2_s','contact_s'],'m/s',['S02'],'半无限扩散解J(t)=DeltaC*sqrt(D/(pi*t))，在接触周期积分平均得到。','需要界面接触时间或U/L；不是只由吹气量决定。','higbie')
model('M04','涡胞传质尺度','k=C*sqrt(D)*(eps_local/nu)**0.25',['D_m2_s','eps_local_W_kg','nu_m2_s','C'],'m/s',['S04'],'Kolmogorov时间tau=(nu/eps)^0.5，扩散层厚度sqrt(D*tau)，k~D/delta。量纲核对后使用；C必须显式提供。','局部耗散，不允许把总吹气功无系数代入。原HTML公式排版不可靠，未执行其原样转录。','eddy_transfer')
model('M05','双膜有效传质系数','1/Km=1/km+rho_m/(rho_s*ks*Lw)',['km','ks','Lw','rho_m','rho_s'],'m/s',['S03','S04'],'两侧通量相等，界面分配关系ws_i=Lw*wm_i，使用钢侧质量分数驱动力。若浓度基准改为kg/m3，h=Lw*rho_s/rho_m。','分配比为质量分数之比；界面近平衡，忽略有限化学反应阻力。','two_film')
model('M06','渣钢有效界面及液滴面积','A=eta*A_resolved; A_drop=6*V_drop/d32; G=sum(Kj*Aj); gamma=G/Vm',['A_resolved','effectiveness','V_drop','d32','zone_KA'],'m2; m3/s; 1/s',['S02','S04'],'球形液滴体积和面积之比6/d32；多个界面并联求和。平界面减裸露钢眼，钢眼边缘界面另计。','A_drop为渣钢界面；气泡面积不得并入脱硫面积。resolved面积须来自VOF、成像或独立标定。','interface_area / combine_conductance')
model('M07','有限渣量双容器脱硫','wm_eq=(Mm*wm0+Ms*ws0)/(Mm+Ms*Lw); wm(t)=wm_eq+(wm0-wm_eq)*exp(-gamma*(1+Mm/(Ms*Lw))*t)',['Mm_kg','Ms_kg','wm0','ws0','Lw','gamma_s_inv','t_s'],'mass_fraction',['S03'],'钢侧dwm/dt=-gamma*(wm-ws/Lw)；渣侧Ms*dws/dt=-Mm*dwm/dt。相加得总硫守恒，消元得到解析式。','分段内钢重、渣量、Lw、gamma固定；再氧化、加渣、扒渣在事件边界更新。','sulfur_two_phase / sulfur_time')
model('M08','从浓度序列识别集总速率','log((C-Ceq)/(C0-Ceq))=-lambda*t',['time_s','concentration','Ceq'],'1/s',['S03','S13'],'解析解取对数后回归；有限渣脱硫gamma=lambda/(1+Mm/(Ms*Lw))。','至少3点、已知平衡边界、同一工况；仅识别lambda，不能独立识别k和A。','fit_rate')
model('M09','参考工况混匀时间尺度','tau=tau_ref*(Q/Qref)**(-1/3)',['tau_ref_s','Q','Q_ref','source_case'],'s',['S01'],'文献同几何搅拌尺度关系；采用比值避免有量纲系数跨单位迁移。','仅同钢包、砖布置、渣状态、加料量和混匀定义近似不变的局部变化；不能当跨厂通式。','mixing_relative')
model('M10','RH气升循环的力学闭合','q=Ad*rho*sqrt(2*g*H*(alpha_up-alpha_down)/Kloss)',['Ad_m2','rho','H_m','alpha_up','alpha_down','Kloss'],'kg/s',['S14','S15'],'以气含率导致的浮力压头平衡有效全回路阻力压降。Kloss含几何变化及速度换算。','研究闭合式，不是拟合好的文献循环量通式；气含率和Kloss须独立测定/CFD/示踪标定。','rh_lift_circulation')
model('M11','示踪剂反演RH循环量','q=-log((Cl-Ceq)/(Cl0-Ceq))/(t*(1/Ml+1/Mv))',['Cl','Cl0','Ceq','Ml','Mv','t'],'kg/s',[],'无反应双完全混合容器守恒。Ceq=(Ml*Cl0+Mv*Cv0)/(Ml+Mv)。','已知初始示踪分布，期间无加料/反应，实际多区域死区会造成偏差。','rh_tracer_circulation')
model('M12','RH钢包—真空室双容器反应','dCl/dt=q/Ml*(Cv-Cl); dCv/dt=q/Mv*(Cl-Cv)-kv*(Cv-Cstar)',['Ml','Mv','q','kv','Cstar','Cl0','Cv0','t'],'ppm; removed_mass_kg',['S13','S14'],'守恒对流交换＋真空室一阶表观反应。显式输出两个容器，不能把q与k混为一个参数。','q/kv/Cstar需独立依据；脱碳额外检查可用氧，未包含完整CO成核和供氧竞争。','rh_two_tank')
model('M13','RH尾气碳收支','mC_removed=MC*sum(QNdry*dt/VmN*(yCO+yCO2))*correction',['QNdry','dt','yCO','yCO2','VmN','correction'],'kg_C',['S13'],'CO和CO2每mol各含1mol碳；由干基尾气摩尔流量积分。','必须同一干基和N状态；需修正漏气、冷却吸收、测量滞后和非钢液碳源。不能将全部尾气都当CO。','carbon_offgas')
model('M14','真空脱氢平衡与动力学','Heq=KH(T)*sqrt(pH2/p0); H=Heq+(H0-Heq)*exp(-gammaH*t)',['KH_ppm','pH2','p0','H0','gammaH','t'],'ppm_H',['S07'],'Sieverts平衡＋气液传质一阶近似；KH标准态与钢种活度一致。','KH、氢分压、gamma必须有来源；总真空压力不是氢分压。','hydrogen')
model('M15','Al脱氧与残余铝物料平衡','mAl=[(54/48)*M*(O0-Of)*1e-6+M*(Alf-Al0)*1e-6+loss]/purity',['M','O0_ppm','Of_ppm','Al0_ppm','Alf_ppm','loss_kg','purity'],'kg',['S09'],'2Al+3O=Al2O3的摩尔质量比；耗氧铝与钢中净保留铝分开。','不是总氧终点预测；不能再重复除以含相同损失的综合收得率。','aluminum_dose')
model('M16','合金单元素精确质量平衡','m=M*(wt-w0)/(x*eta-wt)',['M','w0','wt','alloy_x','eta'],'kg',[],'假设所加合金总质量进入最终金属质量，目标方程M*w0+m*x*eta=(M+m)*wt；实际渣损须另建总质量。','单种合金单元素；多合金多元素联算应采用优化并检查所有杂质。','alloy_single')
model('M17','多合金约束配料','M*w0_i+sum(mj*xij*etaij)=(M+sum(mj))*wf_i',['M','w0_i','targets_i','xij','etaij','prices_j'],'kg; cost',[],'按目标上下限建立线性不等式并最小化成本；考虑总钢重变化。','材料收得率与金属总质量假设需现场校准；未安装LP依赖时不生成假解。','design_only',status='specified_not_implemented')
model('M18','分段热平衡','Tnext=T+(eta*P+Qrxn-Qloss)*dt/(M*cp)-Qaddition/(M*cp)',['T','M','cp','P','eta','Qrxn','Qloss','Qaddition','dt'],'degC',['S18','S19'],'第一定律，逐段累计；待浇和运输没有加热也有散热。','cp、效率、包衬蓄热、气体/渣层影响必须有来源；加料增重可用全焓模型扩展。','thermal_step')
model('M19','浇注向前逆算温度','Tup=TL+superheat+sum(losses)-sum(heating)',['TL','superheat','losses','heating'],'degC',['S20','S21'],'沿路线反向累计温差；液相线必须来自具体成分和热力学/实验。','首炉、稳态、尾浇和换包独立；不是统一1520度液相线。','backward_temperature')
model('M20','颗粒Stokes上浮尺度','u=(rho_m-rho_p)*g*d**2/(18*mu); t=H/u',['rho_m','rho_p','d','mu','H'],'m/s; s',[],'低Re球形颗粒浮力和Stokes阻力平衡。','只适用于Re<0.1的静态尺度估计；实际夹杂去除还受湍流、聚集和渣吸收影响。','stokes_rise')
model('M21','总氧与夹杂物人口平衡','TO=O_diss+sum(fO_j*mj)/M; dn_i/dt=aggregation+generation-removal',['dissolved_O','inclusion_bins','aggregation_kernel','capture','reoxidation'],'ppm_O',['S09','S17','S30'],'溶解与夹杂中的氧质量守恒；人口平衡保留尺寸和成分。','缺少原始尺寸谱/聚集与吸收数据，不冒充已完成预测。','design_only',status='specified_not_implemented')
model('M22','N脱除、吸氮与TiN固定耦合','dN/dt=J_desorb+J_absorb-J_precip; equilibrium activities required',['pN2','N','O','S','Ti','T','interface'],'ppm_N',['S12','S24'],'气液平衡与界面动力学，结合TiN沉淀平衡。','高氮并非都能RH去除，N2搅拌不等于Ar；缺少活度与动力学数据库。','design_only',status='specified_not_implemented')
model('M23','渣眼、卷渣和界面面积代理模型','Aeye=f(Q,H,D,hslag,layout,rho,mu,sigma); Adrop=6*Vdrop/d32',['geometry','gas','slag_properties','CFD_or_images'],'m2',['S01','S02','S04','S29'],'通过原型CFD和水模/视觉建立带工况域的代理模型。','尚无可通用的已训练代理系数；M06只计算给定面积的几何关系，不声称Q即可预测A。','design_only',status='specified_not_implemented')
model('M24','工序路线与约束串联','x_next=F_process(x,events,calibration); feasible=all(order_constraints & equipment_constraints)',['state','events','route','targets','equipment'],'state trajectory',['S11','S12','S25','S26'],'事件图：加料/加热/吹气可重叠；质量和焓在工序边界传递。','数据库提供路线图与输入模板，尚无多设备排队/全产品性能优化器。','design_only',status='specified_not_implemented')
model('M25','2017单砖偏心钢包混匀关联式','tau*Q/R^3=222*(Q^2/(gR^5))^0.33*(L/R)^(-1)*(hslag/R)^0.3*(nu_s^2/(gR^3))^0.016*(DeltaRho/rho_l)^(-0.044)',['Q_actual_mean_height','L','R','hslag','nu_s','rho_l','rho_s','plug_r_over_R'],'s',['S01'],'原文Eq7无量纲形式；输入Q是按平均浴深压力和液温修正后的气体量，不是标况气量。','单砖0.5R、近似圆柱、上浮渣层；代码检查部分域，完整水模/原型相似仍须人工核对。','mixing_2017')
model('M26','2017偏心单砖渣眼关联式','Aeye/(L*hslag)=2.67*(Up^2/(g*hslag))^1.28*(nu_s/(hslag*Up))^(-0.05)*(rho_l/DeltaRho)^0.55',['Uplume','L','hslag','nu_s','rho_l','rho_s','R','plug_r_over_R'],'m2',['S01'],'原文偏心单砖关联，系数2.67；中心喷吹版本系数不同，不混用。','需要独立羽流速度；输出超过横截面时拒算，不截断伪装正确。只预测渣眼，不是总有效反应面积。','slag_eye_2017')

REACTIONS=[]
for i,name,eq,process,src,note in [
('R01','铝脱氧','2[Al]+3[O] -> Al2O3','LF,RH,CAS',['S09'],'产物先为夹杂，生成不等于去除。'),
('R02','硅脱氧','[Si]+2[O] -> SiO2','tapping,LF',['S09'],'结合硅锰复合脱氧和产物活度。'),
('R03','锰脱氧','[Mn]+[O] -> MnO','tapping,LF',['S09'],'有效合金和氧化损失分开。'),
('R04','渣钢脱硫','[S]+(CaO) <-> (CaS)+[O]','LF',['S03'],'需要低氧及合适渣量/活度/液相。'),
('R05','铝耦合脱硫','3(CaO)+3[S]+2[Al] -> 3(CaS)+(Al2O3)','LF',['S03'],'理论耗铝与硫变化联算，避免重复计入脱氧损失。'),
('R06','还原氧化渣','2[Al]+3(FeO) -> (Al2O3)+3Fe','LF,RH',['S17'],'FeO和MnO都可造成铝损。'),
('R07','真空脱碳','[C]+[O] -> CO(g)','RH,VD',['S12','S13'],'每kg C形成CO至少消耗16/12 kg O。'),
('R08','脱氢','2[H] <-> H2(g)','RH,VD',['S07'],'氢分压与总压力分开。'),
('R09','脱氮','2[N] <-> N2(g)','RH,VD',['S24'],'氧硫及界面反应速率会限制脱氮。'),
('R10','钙与氧硫','[Ca]+[O] -> CaO; [Ca]+[S] -> CaS','wire',['S30'],'需要热力学改性窗口和有效Ca收得率。'),
('R11','钛固定氮','[Ti]+[N] <-> TiN','LF,RH,solidification',['S06'],'有效固溶量和析出量不能混淆。'),
('R12','铝氧化升温','4Al+3O2 -> 2Al2O3','CAS-OB,RH-OB',['S18'],'氧化铝输入与反应放热一起计入。')]:REACTIONS.append(dict(reaction_id=i,name=name,equation=eq,processes=process,source_ids_json=j(src),note=note))

EQUIPMENT=[]
for eid,name,scope,functions,temp,time,src in [
('TAP','BOF/EAF出钢挡渣','core','建立钢/渣/温度初始条件','实测出钢温度曲线；不设通用固定值','出钢钢重曲线积分；加入事件可重叠',['S06','S25']),
('SKIM','扒渣/改渣','core','减少携渣氧化物和调整渣量','继承钢包热平衡','实际扒渣与作业耗时',['S03','S17']),
('AR','吹氩站','core','混匀、成分微调、去夹杂','M18分段温降','M09混匀＋去夹杂独立约束',['S01','S05']),
('LF','钢包炉','core','加热、造渣、脱氧、脱硫、合金化','M18/M19；SPHC案例1595±5℃不通用','通电/混匀/软吹/取样/等待区分',['S10','S11','S19']),
('CAS','密封吹氩成分调整','core_optional','合金微调与保护','热平衡；无氧化补热时只计热损','材料溶解/混匀及调度',['S18']),
('CASOB','密封吹氧补热','core_optional','铝氧化化学升温','反应热+包衬热损联算','吹氧/供铝/还原阶段分别计算',['S18']),
('RH','真空循环精炼','core_optional','脱碳、脱气、成分微调','M18/M19按路线逆算','抽空/脱碳/最终脱氧合金化/循环时间',['S12','S13','S14']),
('RHOB','RH-OB/RH-TOP','core_optional','强制脱碳与化学补热','吹氧反应热与材料热效应','供氧和真空曲线分段',['S12','S13']),
('VD','真空罐脱气','core_optional','重点脱氢及气体控制','真空期间净热损','抽空/保压/破空/软吹分开',['S07']),
('VAD','真空加热精炼','extension','特定配置真空与加热','按配置电热平衡','真空与加热事件图',['S26']),
('WIRE','喂丝站','core_optional','Ca/Al/C/微合金控制','喂入温降、释放及反应热','长度/速度＋后续混匀',['S30']),
('POWDER','喷粉站/RH喷粉','extension','强化界面反应','粉料热效应和载气损失','粉速积分，载气与提升气分开',['S08','S22']),
('SOFT','软吹与静置','core','最终均匀与夹杂去除','M18温降；包盖/渣层状态','相应设备模型和质量检测终止',['S01','S16']),
('TRANSFER','钢包运输/等候/保温','core','工序连接','包衬热史、加盖与等待持续时间','调度事件日志',['S11','S19']),
('TD','中间包','core','缓冲、分流、去夹杂','液相线+过热度；首炉/稳态分开','RTD分布而非单一停留时间',['S20','S21']),
('TDHEAT','中间包感应/等离子加热','core_optional','稳定过热度','功率与温度反馈热平衡','按浇注时间连续控制',['S21']),
('CC','连铸/EMS/软压下','core','凝固质量和断面','液相线、固相线、二冷热传导','钢重/流量与拉速、断面、流数联算',['S20']),
('INGOT','模铸/真空浇注','extension','大型锭坯','液相线与补缩凝固计算','浇注曲线及凝固仿真',['S27']),
('AODVOD','AOD/VOD','outside_core','不锈钢脱碳保铬','按钢种分阶段热化学平衡','吹氧/还原/脱硫阶段',['S26']),
('VIMESRVAR','VIM/ESR/VAR','outside_core','特种熔炼与重熔','独立合金体系和熔池模型','熔速/电极质量/凝固模型',['S27']),
('ROLLHT','轧制/锻造/控冷/退火/淬回火/涂镀','downstream_interface','最终组织与性能','相变与传热模型；待专项建库','厚度/线速/保温及相变时间；尚未实现',[])]:EQUIPMENT.append(dict(equipment_id=eid,name=name,scope=scope,functions=functions,temperature_rule=temp,time_rule=time,source_ids_json=j(src),status='catalog_only'))

GRADES=[]
for gid,name,examples,drivers,coverage in [
('STRUCT','普碳/低合金结构钢','Q235,Q355,S235,S355','C/Mn/Si/P/S，Ti/N/夹杂、焊接与铸坯','Q355B和S355有定量案例；不同标准不等同'),
('HOTSTRIP','热轧普碳板带','SPHC等','低Si、C/Mn、Als、温度与表面质量','SPHC企业内控案例'),
('REBAR','钢筋','HRB400,HRB500等','C/Mn/Si/V/Nb/N、碳当量、控轧控冷','HRB400进站渣目标有论文摘要；异常节时/节电量隔离'),
('WIRE','普通线材/焊接线材','低碳盘条、焊丝钢','成分均匀性、夹杂、残余元素','待专项检索'),
('PLATE','中厚板','工程机械、桥梁结构钢','低S/P、H、夹杂与厚度性能','待专项检索'),
('PIPE','管线钢','X52,X65,X70,X80','S/H/N、夹杂、Ca处理、焊接与偏析','路线库待定量补充，不挪用IF配方'),
('MARINE','船板海工','船体/海工结构钢','低温韧性、H、夹杂与焊接','待专项检索'),
('VESSEL','锅炉压力容器钢','压力容器板','H、S/P、厚度与热处理','待专项检索'),
('IF','超低碳深冲板','IF钢','C/N、Ti/Nb稳定化、T.O和表面','西昌IF工业对比＋RH方法证据'),
('AUTO','汽车板','低碳冲压、HSLA、AHSS','C/Mn/Si/Al、N、表面、退火组织','尚无全成分/轧制性能联合模型'),
('TIN','镀锡基板','低碳板','C/N、夹杂、表面','待专项检索'),
('ELEC','电工钢','无取向/取向','C/N/S、Si/Al、抑制剂与退火','厂级公告仅产线背景，非精炼定量配方'),
('WEATHER','耐候/集装箱钢','耐候板、集装箱板','Cu/Cr/Ni/P与残余控制','待专项检索'),
('RAIL','重轨','轨道钢','C/Mn、H、夹杂和中心偏析','待专项检索'),
('HIGHC','高碳硬线','预应力钢绞线盘条','高C、低夹杂、偏析、脱碳','待专项检索')]:GRADES.append(dict(grade_id=gid,name=name,examples=examples,quality_drivers=drivers,coverage_status=coverage,note='仅产品族索引，不代表有效版本标准或产品认证。'))

ROUTES=[]
for rid,gid,steps,rule,src in [
('RT01','STRUCT',['TAP','LF','SOFT','TRANSFER','TD','CC'],'Q355Ti参考，Ti在低氧后加入；按订单决定是否Ca处理',['S06']),
('RT02','STRUCT',['TAP','LF','SOFT','TRANSFER','TD','CC'],'S355独立案例；不得与Q355配料拼为一炉',['S05']),
('RT03','HOTSTRIP',['TAP','LF','SOFT','TRANSFER','TD','CC'],'SPHC本厂目标案例，仅作参考',['S10']),
('RT04','IF',['TAP','LF','RHOB','SOFT','TRANSFER','TD','CC'],'LF可补热；RH强制供氧脱碳，最终脱氧顺序必须保留',['S12']),
('RT05','IF',['TAP','RH','SOFT','TRANSFER','TD','CC'],'热量及初始C/O满足时的候选；尚未绑定完整炉次',['S13','S26']),
('RT06','PIPE',['TAP','LF','RH','WIRE','SOFT','TRANSFER','TD','CC'],'工程候选而非统一规定；H/S/夹杂目标决定真空与Ca处理',[]),
('RT07','PLATE',['TAP','LF','VD','SOFT','TRANSFER','TD','CC'],'工程候选；VD能力不可从105t模型直接移植',['S07']),
('RT08','REBAR',['TAP','AR','TRANSFER','TD','CC'],'低成本候选，仅在成分温度洁净度均可满足时',[]),
('RT09','REBAR',['TAP','LF','SOFT','TRANSFER','TD','CC'],'需升温/微合金/成分调整的候选',[])]:ROUTES.append(dict(route_id=rid,grade_id=gid,steps_json=j(steps),selection_rule=rule,source_ids_json=j(src),status='evidence_route' if src else 'engineering_candidate_not_verified'))
ROUTES.append(dict(route_id='RT10',grade_id='REBAR',steps_json=j(['TAP','LF','SOFT','TRANSFER','TD','CC']),selection_rule='HRB400进站渣优化案例，不能把进站氧化物目标当终渣脱硫目标',source_ids_json=j(['S33']),status='partial_evidence_route'))

GAPS=[]
for i,topic,missing,impact,action in [
('G01','本厂炉次','逐炉起点/时序/中间取样/终点及设备号','不能宣称工业预测精度','按templates事件格式导入；按炉次、时间和钢厂隔离验证'),
('G02','传质与面积可识别性','独立界面面积或局部耗散/传质测量','单一终点只能约束kA/V，k和A不唯一','结合多流量时序、成像、VOF及示踪'),
('G03','RH循环闭合','气含率、回路阻力或示踪浓度序列','不能只凭气量算可信循环量','建立具体装置气含率/阻力标定或示踪反算'),
('G04','气体体积口径','S05/S08/S16等标准状态定义','Nm3转换和跨文献回归不成立','核对仪表/方法，未解决前保留unspecified'),
('G05','热力学库','各钢渣体系活度、温度依赖、液相线、硫分配','没有统一可信平衡终点','接入有许可的热力学引擎或逐式核验的实验关系'),
('G06','夹杂人口平衡','尺寸谱、聚并与吸收效率、再氧化率','无法保证总氧和水口堵塞预测','工业SEM谱＋T.O测量＋分组动力学'),
('G07','产品族覆盖','钢筋/管线/船板/压力容器/电工/高碳等完整配方','不能称全面普钢数据库已完成','逐族补原始论文与钢厂工况，不用专利替代实测'),
('G08','时间窗与元数据','S14/S15/S20首发日期；部分准确题名/作者','十年统计边界仍有待核条目','用Crossref/期刊原始元数据复核，待核项不作年份趋势'),
('G09','数据来源新旧','S09含2005工业输入；S13介绍含旧经验范围','出版年不等于新工业数据','保存原始数据年份并排除新炉次统计'),
('G10','公式转录','S03部分有量纲经验系数；S04原网页公式排版','错误单位会产生数量级偏差','先原PDF图式/原始引用核验，暂不执行有歧义经验式'),
('G11','真实公开样本范围','S05只选取8炉，并非整张46炉表全量','不可声称已拥有46炉原始数据','在许可和提取预算内逐步扩充并记录版本'),
('G12','上下游质量','废钢Cu/Sn等、铸坯/轧制/热处理实绩','不能预测最终所有性能','接入原料和下游数据；残余元素约束先行'),
('G13','不确定性','独立验证残差及域外样本','敏感性范围不能叫95%置信/预测区间','分钢种和设备留出验证，校准覆盖率'),
('G14','工程优化','多合金LP、全流程状态事件求解、多设备排程','当前是数据库与子模型，不是完整自动决策平台','先固定厂型和钢种闭环，再扩展设备与产品'),
('G15','检索完整性','尚未完成十年逐库穷尽筛查、逐年纳排清单','本版是有边界的种子集，不是系统综述','扩展Crossref/中文原站，按DOI和原始数据集去重')]:GAPS.append(dict(gap_id=i,topic=topic,severity='high',missing_data=missing,impact=impact,next_action=action))
