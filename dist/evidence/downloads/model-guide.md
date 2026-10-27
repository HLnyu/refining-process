# 动力学、配料与温度模型：公式与推导

所有实现均为研究内核，未获得本厂工业预测误差。标准库函数可执行并接受明确输入，缺少标定量时必须停算对应项。

## 必须分清的量

- k：m/s；A：m²；G=sum(k_j*A_j)：m³/s；gamma=G/V：1/s。不要把m³/s的kA写成1/s的kLa。
- Lw=ws/wm是质量分数分配比；h=Cs/Cm=Lw*rho_s/rho_m是质量浓度分配比。
- QN是给定N状态气量，Q_actual是浴温/绝压下气量；两者不是同一个自变量。
- RH循环量q为kg/s；t/min乘1000/60换算。钢包内流场局部循环通量不是RH上/下浸渍管之间的净交换量。
- 95%混匀时间是示踪浓度容差定义，不等于脱硫95%完成，也不等于加料耗时。

## 参数可识别性

若C(t)=Ceq+(C0-Ceq)exp(-gamma*t)，浓度序列只能识别gamma。对任何正数b，把k变为b*k、A变为A/b，都给相同gamma，不能唯一反推出两者。仅有一个终点且Ceq也未知时，连gamma都不能唯一确定。

分离k与A需要独立的面积测量/VOF、局部耗散与传质测量、不同激励下的多时间点，以及带物理边界的联合标定。RH的q与kv也存在类似补偿性，优先用示踪实验识别q，再估计反应参数。

## 串联方式

LF条件化计算：QN、绝压、浴深 → 气体膨胀功 → 输入局部耗散分配参数 → k_m → 双膜K → 输入VOF/测量/标定面积 → gamma → 有限渣量脱硫 → 下一阶段钢渣状态。

其中“局部耗散分配参数”和“面积”是待标定输入，不能声称此链已从气量独立预测所有隐变量。simulate_lf实现此分段串联并同步做热平衡；没有完全求解钢-渣-氧-夹杂多反应体系。

RH条件化计算：气量/压力/几何 → 经验证的气含率/回路阻力或示踪反算q → 双容器交换与反应 → 脱碳/脱氢时序；尾气碳收支提供独立核验。仅有气量时拒绝给可信q的无条件结果。

## 逐模型注册表

### M01 标况气量到炉内实际气量

- 状态：implemented_unvalidated；实现：`gas_actual`。
- 方程：`Q=QN*(T/TN)*(pN/p)`。
- 输入：QN_m3_s, T_K, p_abs_Pa, TN_K, pN_Pa。输出：m3/s。
- 来源：守恒/几何推导，非文献拟合参数。
- 推导：理想气体状态方程pQ=nRT。N状态必须由输入指定。
- 适用与限制：单相理想气体；未包括气泡滑移、CO生成及传热非平衡。

### M02 气体膨胀的理想机械功

- 状态：implemented_unvalidated；实现：`gas_power`。
- 方程：`P=n_dot*R*T*ln((p_surface+rho*g*H)/p_surface); eps_mean=P/M`。
- 输入：QN_m3_s, T_K, p_surface_Pa, rho, H, M, TN, pN。输出：W; W/kg。
- 来源：[S02](https://www.jstage.jst.go.jp/article/isijinternational/57/11/57_ISIJINT-2016-589/_html/-char/en)。
- 推导：n_dot=pN*QN/(R*TN)，沿静压积分可逆等温膨胀功。局部界面耗散不是全包平均功率。
- 适用与限制：表面绝压>0；忽略气体显热与各处能量耗散分配。

### M03 Higbie界面更新传质系数

- 状态：implemented_unvalidated；实现：`higbie`。
- 方程：`k=2*sqrt(D/(pi*t_contact))=2*sqrt(D*U/(pi*L))`。
- 输入：D_m2_s, contact_s。输出：m/s。
- 来源：[S02](https://www.jstage.jst.go.jp/article/isijinternational/57/11/57_ISIJINT-2016-589/_html/-char/en)。
- 推导：半无限扩散解J(t)=DeltaC*sqrt(D/(pi*t))，在接触周期积分平均得到。
- 适用与限制：需要界面接触时间或U/L；不是只由吹气量决定。

### M04 涡胞传质尺度

- 状态：implemented_unvalidated；实现：`eddy_transfer`。
- 方程：`k=C*sqrt(D)*(eps_local/nu)**0.25`。
- 输入：D_m2_s, eps_local_W_kg, nu_m2_s, C。输出：m/s。
- 来源：[S04](https://www.jstage.jst.go.jp/article/isijinternational/64/1/64_ISIJINT-2023-310/_html/-char/en)。
- 推导：Kolmogorov时间tau=(nu/eps)^0.5，扩散层厚度sqrt(D*tau)，k~D/delta。量纲核对后使用；C必须显式提供。
- 适用与限制：局部耗散，不允许把总吹气功无系数代入。原HTML公式排版不可靠，未执行其原样转录。

### M05 双膜有效传质系数

- 状态：implemented_unvalidated；实现：`two_film`。
- 方程：`1/Km=1/km+rho_m/(rho_s*ks*Lw)`。
- 输入：km, ks, Lw, rho_m, rho_s。输出：m/s。
- 来源：[S03](https://www.jstage.jst.go.jp/article/isijinternational/62/6/62_ISIJINT-2021-514/_html/-char/en), [S04](https://www.jstage.jst.go.jp/article/isijinternational/64/1/64_ISIJINT-2023-310/_html/-char/en)。
- 推导：两侧通量相等，界面分配关系ws_i=Lw*wm_i，使用钢侧质量分数驱动力。若浓度基准改为kg/m3，h=Lw*rho_s/rho_m。
- 适用与限制：分配比为质量分数之比；界面近平衡，忽略有限化学反应阻力。

### M06 渣钢有效界面及液滴面积

- 状态：implemented_unvalidated；实现：`interface_area / combine_conductance`。
- 方程：`A=eta*A_resolved; A_drop=6*V_drop/d32; G=sum(Kj*Aj); gamma=G/Vm`。
- 输入：A_resolved, effectiveness, V_drop, d32, zone_KA。输出：m2; m3/s; 1/s。
- 来源：[S02](https://www.jstage.jst.go.jp/article/isijinternational/57/11/57_ISIJINT-2016-589/_html/-char/en), [S04](https://www.jstage.jst.go.jp/article/isijinternational/64/1/64_ISIJINT-2023-310/_html/-char/en)。
- 推导：球形液滴体积和面积之比6/d32；多个界面并联求和。平界面减裸露钢眼，钢眼边缘界面另计。
- 适用与限制：A_drop为渣钢界面；气泡面积不得并入脱硫面积。resolved面积须来自VOF、成像或独立标定。

### M07 有限渣量双容器脱硫

- 状态：implemented_unvalidated；实现：`sulfur_two_phase / sulfur_time`。
- 方程：`wm_eq=(Mm*wm0+Ms*ws0)/(Mm+Ms*Lw); wm(t)=wm_eq+(wm0-wm_eq)*exp(-gamma*(1+Mm/(Ms*Lw))*t)`。
- 输入：Mm_kg, Ms_kg, wm0, ws0, Lw, gamma_s_inv, t_s。输出：mass_fraction。
- 来源：[S03](https://www.jstage.jst.go.jp/article/isijinternational/62/6/62_ISIJINT-2021-514/_html/-char/en)。
- 推导：钢侧dwm/dt=-gamma*(wm-ws/Lw)；渣侧Ms*dws/dt=-Mm*dwm/dt。相加得总硫守恒，消元得到解析式。
- 适用与限制：分段内钢重、渣量、Lw、gamma固定；再氧化、加渣、扒渣在事件边界更新。

### M08 从浓度序列识别集总速率

- 状态：implemented_unvalidated；实现：`fit_rate`。
- 方程：`log((C-Ceq)/(C0-Ceq))=-lambda*t`。
- 输入：time_s, concentration, Ceq。输出：1/s。
- 来源：[S03](https://www.jstage.jst.go.jp/article/isijinternational/62/6/62_ISIJINT-2021-514/_html/-char/en), [S13](https://www.jstage.jst.go.jp/article/isijinternational/66/10/66_ISIJINT-2025-420/_html/-char/ja)。
- 推导：解析解取对数后回归；有限渣脱硫gamma=lambda/(1+Mm/(Ms*Lw))。
- 适用与限制：至少3点、已知平衡边界、同一工况；仅识别lambda，不能独立识别k和A。

### M09 参考工况混匀时间尺度

- 状态：implemented_unvalidated；实现：`mixing_relative`。
- 方程：`tau=tau_ref*(Q/Qref)**(-1/3)`。
- 输入：tau_ref_s, Q, Q_ref, source_case。输出：s。
- 来源：[S01](https://www.jstage.jst.go.jp/article/isijinternational/57/2/57_ISIJINT-2015-701/_html/-char/en)。
- 推导：文献同几何搅拌尺度关系；采用比值避免有量纲系数跨单位迁移。
- 适用与限制：仅同钢包、砖布置、渣状态、加料量和混匀定义近似不变的局部变化；不能当跨厂通式。

### M10 RH气升循环的力学闭合

- 状态：implemented_unvalidated；实现：`rh_lift_circulation`。
- 方程：`q=Ad*rho*sqrt(2*g*H*(alpha_up-alpha_down)/Kloss)`。
- 输入：Ad_m2, rho, H_m, alpha_up, alpha_down, Kloss。输出：kg/s。
- 来源：[S14](https://www.sciencedirect.com/science/article/abs/pii/S0042207X18304238), [S15](https://doi.org/10.1002/srin.202500395)。
- 推导：以气含率导致的浮力压头平衡有效全回路阻力压降。Kloss含几何变化及速度换算。
- 适用与限制：研究闭合式，不是拟合好的文献循环量通式；气含率和Kloss须独立测定/CFD/示踪标定。

### M11 示踪剂反演RH循环量

- 状态：implemented_unvalidated；实现：`rh_tracer_circulation`。
- 方程：`q=-log((Cl-Ceq)/(Cl0-Ceq))/(t*(1/Ml+1/Mv))`。
- 输入：Cl, Cl0, Ceq, Ml, Mv, t。输出：kg/s。
- 来源：守恒/几何推导，非文献拟合参数。
- 推导：无反应双完全混合容器守恒。Ceq=(Ml*Cl0+Mv*Cv0)/(Ml+Mv)。
- 适用与限制：已知初始示踪分布，期间无加料/反应，实际多区域死区会造成偏差。

### M12 RH钢包—真空室双容器反应

- 状态：implemented_unvalidated；实现：`rh_two_tank`。
- 方程：`dCl/dt=q/Ml*(Cv-Cl); dCv/dt=q/Mv*(Cl-Cv)-kv*(Cv-Cstar)`。
- 输入：Ml, Mv, q, kv, Cstar, Cl0, Cv0, t。输出：ppm; removed_mass_kg。
- 来源：[S13](https://www.jstage.jst.go.jp/article/isijinternational/66/10/66_ISIJINT-2025-420/_html/-char/ja), [S14](https://www.sciencedirect.com/science/article/abs/pii/S0042207X18304238)。
- 推导：守恒对流交换＋真空室一阶表观反应。显式输出两个容器，不能把q与k混为一个参数。
- 适用与限制：q/kv/Cstar需独立依据；脱碳额外检查可用氧，未包含完整CO成核和供氧竞争。

### M13 RH尾气碳收支

- 状态：implemented_unvalidated；实现：`carbon_offgas`。
- 方程：`mC_removed=MC*sum(QNdry*dt/VmN*(yCO+yCO2))*correction`。
- 输入：QNdry, dt, yCO, yCO2, VmN, correction。输出：kg_C。
- 来源：[S13](https://www.jstage.jst.go.jp/article/isijinternational/66/10/66_ISIJINT-2025-420/_html/-char/ja)。
- 推导：CO和CO2每mol各含1mol碳；由干基尾气摩尔流量积分。
- 适用与限制：必须同一干基和N状态；需修正漏气、冷却吸收、测量滞后和非钢液碳源。不能将全部尾气都当CO。

### M14 真空脱氢平衡与动力学

- 状态：implemented_unvalidated；实现：`hydrogen`。
- 方程：`Heq=KH(T)*sqrt(pH2/p0); H=Heq+(H0-Heq)*exp(-gammaH*t)`。
- 输入：KH_ppm, pH2, p0, H0, gammaH, t。输出：ppm_H。
- 来源：[S07](https://www.mdpi.com/2075-4701/13/7/1229)。
- 推导：Sieverts平衡＋气液传质一阶近似；KH标准态与钢种活度一致。
- 适用与限制：KH、氢分压、gamma必须有来源；总真空压力不是氢分压。

### M15 Al脱氧与残余铝物料平衡

- 状态：implemented_unvalidated；实现：`aluminum_dose`。
- 方程：`mAl=[(54/48)*M*(O0-Of)*1e-6+M*(Alf-Al0)*1e-6+loss]/purity`。
- 输入：M, O0_ppm, Of_ppm, Al0_ppm, Alf_ppm, loss_kg, purity。输出：kg。
- 来源：[S09](https://doi.org/10.1002/srin.202300330)。
- 推导：2Al+3O=Al2O3的摩尔质量比；耗氧铝与钢中净保留铝分开。
- 适用与限制：不是总氧终点预测；不能再重复除以含相同损失的综合收得率。

### M16 合金单元素精确质量平衡

- 状态：implemented_unvalidated；实现：`alloy_single`。
- 方程：`m=M*(wt-w0)/(x*eta-wt)`。
- 输入：M, w0, wt, alloy_x, eta。输出：kg。
- 来源：守恒/几何推导，非文献拟合参数。
- 推导：假设所加合金总质量进入最终金属质量，目标方程M*w0+m*x*eta=(M+m)*wt；实际渣损须另建总质量。
- 适用与限制：单种合金单元素；多合金多元素联算应采用优化并检查所有杂质。

### M17 多合金约束配料

- 状态：specified_not_implemented；实现：`design_only`。
- 方程：`M*w0_i+sum(mj*xij*etaij)=(M+sum(mj))*wf_i`。
- 输入：M, w0_i, targets_i, xij, etaij, prices_j。输出：kg; cost。
- 来源：守恒/几何推导，非文献拟合参数。
- 推导：按目标上下限建立线性不等式并最小化成本；考虑总钢重变化。
- 适用与限制：材料收得率与金属总质量假设需现场校准；未安装LP依赖时不生成假解。

### M18 分段热平衡

- 状态：implemented_unvalidated；实现：`thermal_step`。
- 方程：`Tnext=T+(eta*P+Qrxn-Qloss)*dt/(M*cp)-Qaddition/(M*cp)`。
- 输入：T, M, cp, P, eta, Qrxn, Qloss, Qaddition, dt。输出：degC。
- 来源：[S18](https://www.mdpi.com/2075-4701/11/10/1554), [S19](https://www.jstage.jst.go.jp/article/isijinternational/62/3/62_ISIJINT-2021-251/_pdf)。
- 推导：第一定律，逐段累计；待浇和运输没有加热也有散热。
- 适用与限制：cp、效率、包衬蓄热、气体/渣层影响必须有来源；加料增重可用全焓模型扩展。

### M19 浇注向前逆算温度

- 状态：implemented_unvalidated；实现：`backward_temperature`。
- 方程：`Tup=TL+superheat+sum(losses)-sum(heating)`。
- 输入：TL, superheat, losses, heating。输出：degC。
- 来源：[S20](https://www.jstage.jst.go.jp/article/isijinternational/advpub/0/advpub_ISIJINT-2023-008/_pdf), [S21](https://pmc.ncbi.nlm.nih.gov/articles/PMC9000347/)。
- 推导：沿路线反向累计温差；液相线必须来自具体成分和热力学/实验。
- 适用与限制：首炉、稳态、尾浇和换包独立；不是统一1520度液相线。

### M20 颗粒Stokes上浮尺度

- 状态：implemented_unvalidated；实现：`stokes_rise`。
- 方程：`u=(rho_m-rho_p)*g*d**2/(18*mu); t=H/u`。
- 输入：rho_m, rho_p, d, mu, H。输出：m/s; s。
- 来源：守恒/几何推导，非文献拟合参数。
- 推导：低Re球形颗粒浮力和Stokes阻力平衡。
- 适用与限制：只适用于Re<0.1的静态尺度估计；实际夹杂去除还受湍流、聚集和渣吸收影响。

### M21 总氧与夹杂物人口平衡

- 状态：specified_not_implemented；实现：`design_only`。
- 方程：`TO=O_diss+sum(fO_j*mj)/M; dn_i/dt=aggregation+generation-removal`。
- 输入：dissolved_O, inclusion_bins, aggregation_kernel, capture, reoxidation。输出：ppm_O。
- 来源：[S09](https://doi.org/10.1002/srin.202300330), [S17](https://www.mdpi.com/2075-4701/11/5/763), [S30](https://www.jstage.jst.go.jp/article/isijinternational/63/2/63_ISIJINT-2022-274/_pdf)。
- 推导：溶解与夹杂中的氧质量守恒；人口平衡保留尺寸和成分。
- 适用与限制：缺少原始尺寸谱/聚集与吸收数据，不冒充已完成预测。

### M22 N脱除、吸氮与TiN固定耦合

- 状态：specified_not_implemented；实现：`design_only`。
- 方程：`dN/dt=J_desorb+J_absorb-J_precip; equilibrium activities required`。
- 输入：pN2, N, O, S, Ti, T, interface。输出：ppm_N。
- 来源：[S12](https://cje.ustb.edu.cn/cn/article/doi/10.13374/j.issn2095-9389.2020.10.10.002), [S24](https://www.chinamet.cn/gt/article/doi/10.13228/j.boyuan.issn0449-749x.20240305)。
- 推导：气液平衡与界面动力学，结合TiN沉淀平衡。
- 适用与限制：高氮并非都能RH去除，N2搅拌不等于Ar；缺少活度与动力学数据库。

### M23 渣眼、卷渣和界面面积代理模型

- 状态：specified_not_implemented；实现：`design_only`。
- 方程：`Aeye=f(Q,H,D,hslag,layout,rho,mu,sigma); Adrop=6*Vdrop/d32`。
- 输入：geometry, gas, slag_properties, CFD_or_images。输出：m2。
- 来源：[S01](https://www.jstage.jst.go.jp/article/isijinternational/57/2/57_ISIJINT-2015-701/_html/-char/en), [S02](https://www.jstage.jst.go.jp/article/isijinternational/57/11/57_ISIJINT-2016-589/_html/-char/en), [S04](https://www.jstage.jst.go.jp/article/isijinternational/64/1/64_ISIJINT-2023-310/_html/-char/en), [S29](https://www.jstage.jst.go.jp/article/isijinternational/66/9/66_ISIJINT-2026-028/_html/-char/en)。
- 推导：通过原型CFD和水模/视觉建立带工况域的代理模型。
- 适用与限制：尚无可通用的已训练代理系数；M06只计算给定面积的几何关系，不声称Q即可预测A。

### M24 工序路线与约束串联

- 状态：specified_not_implemented；实现：`design_only`。
- 方程：`x_next=F_process(x,events,calibration); feasible=all(order_constraints & equipment_constraints)`。
- 输入：state, events, route, targets, equipment。输出：state trajectory。
- 来源：[S11](https://www.jstage.jst.go.jp/article/isijinternational/60/6/60_ISIJINT-2019-423/_pdf/-char/en), [S12](https://cje.ustb.edu.cn/cn/article/doi/10.13374/j.issn2095-9389.2020.10.10.002), [S25](https://www.shougang.com.cn/en/p1/ShougangNews/20250110/122.html), [S26](https://www.sms-group.com/en-us/plants/secondary-metallurgy)。
- 推导：事件图：加料/加热/吹气可重叠；质量和焓在工序边界传递。
- 适用与限制：数据库提供路线图与输入模板，尚无多设备排队/全产品性能优化器。

### M25 2017单砖偏心钢包混匀关联式

- 状态：implemented_unvalidated；实现：`mixing_2017`。
- 方程：`tau*Q/R^3=222*(Q^2/(gR^5))^0.33*(L/R)^(-1)*(hslag/R)^0.3*(nu_s^2/(gR^3))^0.016*(DeltaRho/rho_l)^(-0.044)`。
- 输入：Q_actual_mean_height, L, R, hslag, nu_s, rho_l, rho_s, plug_r_over_R。输出：s。
- 来源：[S01](https://www.jstage.jst.go.jp/article/isijinternational/57/2/57_ISIJINT-2015-701/_html/-char/en)。
- 推导：原文Eq7无量纲形式；输入Q是按平均浴深压力和液温修正后的气体量，不是标况气量。
- 适用与限制：单砖0.5R、近似圆柱、上浮渣层；代码检查部分域，完整水模/原型相似仍须人工核对。

### M26 2017偏心单砖渣眼关联式

- 状态：implemented_unvalidated；实现：`slag_eye_2017`。
- 方程：`Aeye/(L*hslag)=2.67*(Up^2/(g*hslag))^1.28*(nu_s/(hslag*Up))^(-0.05)*(rho_l/DeltaRho)^0.55`。
- 输入：Uplume, L, hslag, nu_s, rho_l, rho_s, R, plug_r_over_R。输出：m2。
- 来源：[S01](https://www.jstage.jst.go.jp/article/isijinternational/57/2/57_ISIJINT-2015-701/_html/-char/en)。
- 推导：原文偏心单砖关联，系数2.67；中心喷吹版本系数不同，不混用。
- 适用与限制：需要独立羽流速度；输出超过横截面时拒算，不截断伪装正确。只预测渣眼，不是总有效反应面积。

## 有限渣量脱硫的完整推导

令钢质量Mm、渣质量Ms、硫质量分数wm、ws，总硫I=Mm*wm+Ms*ws不变。

界面驱动力为wm-ws/Lw。钢侧V=Mm/rho_m，gamma=K*A/V。

dwm/dt=-gamma*(wm-ws/Lw)，dws/dt=Mm/Ms*gamma*(wm-ws/Lw)。

由ws=(I-Mm*wm)/Ms消元，得到dwm/dt=-gamma*(1+Mm/(Ms*Lw))*(wm-wm_eq)。

wm_eq=I/(Mm+Ms*Lw)。所以终点与渣量和初渣硫有关，不是无限趋近于零；初渣富硫时允许返硫。取对数得到目标时间，目标≤wm_eq时有限时间不可达。

两膜推导：J=rho_m*km*(wm_bulk-wm_i)=rho_s*ks*(ws_i-ws_bulk)，ws_i=Lw*wm_i。消去界面浓度得1/K=1/km+rho_m/(rho_s*ks*Lw)。

## RH双容器边界

钢包Ml、真空室Mv分别完全混合，交换质量流量q，两侧交换项相加为零。只在真空室设kv*(Cv-Cstar)表观反应。当kv=0时全系统元素守恒；q=0时钢包浓度不变。RK4自动细分到最大无量纲步长≤0.02，并有氧预算检查。该结构是简化反应器模型，不是完整VOF/气泡人口平衡CFD。

## 不确定性与验证

rate_sensitivity返回的是参数敏感性包络，不能称95%统计区间。统计区间需要独立验证残差并检查实际覆盖率。单元测试验证守恒、极限、反算、单位/输入域；没有工业校准时不报告MAE/RMSE等模型精度。
