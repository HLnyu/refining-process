# 数据库结构、工序串联和覆盖边界

版本2026-10-26。数据库的“参数记录”不是独立炉次数；范围是一条记录，不把上下限拆成两个样本。研究输入、CFD输出、作者推荐、工业测量、企业目标与换算值分别保存。

## 核心连接

`sources → cases → observations → derivations` 保留每个数字的来源和工况。

`grade_families → routes → equipment` 给出产品族与设备路径。routes.steps_json中的设备ID对应equipment。

`models → source_ids_json / implementation` 将公式连接到原文和Python函数。

`heat_imports → calibrations → predictions` 是未来厂级数据与预测链；本版heat_imports和calibrations为空，不伪造训练数据。predictions表结构已准备，演示不自动作为工业预测入库。

同一工况关联case_id，而不是凭相同钢种把不同厂、不同炉、不同时间的数据合并。逐事件输入应携带plant_id、heat_id、equipment_id和时间戳。

## 时间和温度

加热、吹氩、加料可并行：阶段总时间是事件区间并集，不是全部持续时间之和。抽真空、深真空保压、破空、软吹和设备占用时间分开。每步都需要进站温度、随时间的热量和离站状态；上游目标按液相线、过热度及后续运输/等待逆算。

已有文献统计范围见S11的各case；不能将其最小值和最大值当作所有钢厂设计上下限。设备表里的温度/时间规则是模型入口；没有实测支持的工序没有强填分钟数。

## 数据字段说明

sources: source_id, title, DOI, URL, publication_year（卷期年）, publication_date（首次公开日期，缺失可空）, date_precision, 原始数据年代, 访问层级及核验日期。

cases: 同源同工况；study_kind指industrial_heat/industrial_aggregate/numerical_model/water_model等；context_json保存吨位、气体口径、砖布置、研究条件。案例ID不是工厂原始炉号。

observations: 参数名、点值或上下界、原始单位、R/D/A/F/U、数量角色、原表/页/节、核验状态、注释。quantity_role必须区分target、measured、difference、parameter_scan等。U及quarantined数据不用于参考计算。

derivations: 每个D值指向所有父观测及计算式，禁止跨case不解释地拼接。

所有未知数留空或待核，不以零替代。原文“-”未报告的合金量不插入零值。wt%除以100成为质量分数；ppm乘1e-6；吨乘1000成为kg；NL和Nm³以原文N状态为前提。L/min和dm³/min无N不得强改为标况。Pa_abs为绝压。

## 可直接使用的SQL

```sql
SELECT case_id,parameter,value,lower_value,upper_value,unit,locator,url
FROM evidence_chain WHERE grade='Q355B';

SELECT case_id,parameter,value,unit FROM evidence_chain
WHERE source_id='S05' AND study_kind='industrial_heat';

SELECT * FROM usable_reference_evidence WHERE process='RH';

SELECT * FROM models WHERE name LIKE '%传质%';
```

usable_reference_evidence仅排除了显式未核/历史复用项，不代表自动适配任何钢厂；仍必须核对工况、原始数据年代、标准状态、研究类型和模型适用域。

## 产品族覆盖

| ID | 产品族 | 代表牌号 | 本版覆盖 |
|---|---|---|---|
|STRUCT|普碳/低合金结构钢|Q235,Q355,S235,S355|Q355B和S355有定量案例；不同标准不等同|
|HOTSTRIP|热轧普碳板带|SPHC等|SPHC企业内控案例|
|REBAR|钢筋|HRB400,HRB500等|HRB400进站渣目标有论文摘要；异常节时/节电量隔离|
|WIRE|普通线材/焊接线材|低碳盘条、焊丝钢|待专项检索|
|PLATE|中厚板|工程机械、桥梁结构钢|待专项检索|
|PIPE|管线钢|X52,X65,X70,X80|路线库待定量补充，不挪用IF配方|
|MARINE|船板海工|船体/海工结构钢|待专项检索|
|VESSEL|锅炉压力容器钢|压力容器板|待专项检索|
|IF|超低碳深冲板|IF钢|西昌IF工业对比＋RH方法证据|
|AUTO|汽车板|低碳冲压、HSLA、AHSS|尚无全成分/轧制性能联合模型|
|TIN|镀锡基板|低碳板|待专项检索|
|ELEC|电工钢|无取向/取向|厂级公告仅产线背景，非精炼定量配方|
|WEATHER|耐候/集装箱钢|耐候板、集装箱板|待专项检索|
|RAIL|重轨|轨道钢|待专项检索|
|HIGHC|高碳硬线|预应力钢绞线盘条|待专项检索|

## 工序设备

|ID|设备|范围|温度处理|时间处理|依据|
|---|---|---|---|---|---|
|TAP|BOF/EAF出钢挡渣|core|实测出钢温度曲线；不设通用固定值|出钢钢重曲线积分；加入事件可重叠|[S06](https://doi.org/10.12677/meng.2022.91008), [S25](https://www.shougang.com.cn/en/p1/ShougangNews/20250110/122.html)|
|SKIM|扒渣/改渣|core|继承钢包热平衡|实际扒渣与作业耗时|[S03](https://www.jstage.jst.go.jp/article/isijinternational/62/6/62_ISIJINT-2021-514/_html/-char/en), [S17](https://www.mdpi.com/2075-4701/11/5/763)|
|AR|吹氩站|core|M18分段温降|M09混匀＋去夹杂独立约束|[S01](https://www.jstage.jst.go.jp/article/isijinternational/57/2/57_ISIJINT-2015-701/_html/-char/en), [S05](https://pmc.ncbi.nlm.nih.gov/articles/PMC11722051/)|
|LF|钢包炉|core|M18/M19；SPHC案例1595±5℃不通用|通电/混匀/软吹/取样/等待区分|[S10](https://www.mdpi.com/2227-9717/14/18/2994), [S11](https://www.jstage.jst.go.jp/article/isijinternational/60/6/60_ISIJINT-2019-423/_pdf/-char/en), [S19](https://www.jstage.jst.go.jp/article/isijinternational/62/3/62_ISIJINT-2021-251/_pdf)|
|CAS|密封吹氩成分调整|core_optional|热平衡；无氧化补热时只计热损|材料溶解/混匀及调度|[S18](https://www.mdpi.com/2075-4701/11/10/1554)|
|CASOB|密封吹氧补热|core_optional|反应热+包衬热损联算|吹氧/供铝/还原阶段分别计算|[S18](https://www.mdpi.com/2075-4701/11/10/1554)|
|RH|真空循环精炼|core_optional|M18/M19按路线逆算|抽空/脱碳/最终脱氧合金化/循环时间|[S12](https://cje.ustb.edu.cn/cn/article/doi/10.13374/j.issn2095-9389.2020.10.10.002), [S13](https://www.jstage.jst.go.jp/article/isijinternational/66/10/66_ISIJINT-2025-420/_html/-char/ja), [S14](https://www.sciencedirect.com/science/article/abs/pii/S0042207X18304238)|
|RHOB|RH-OB/RH-TOP|core_optional|吹氧反应热与材料热效应|供氧和真空曲线分段|[S12](https://cje.ustb.edu.cn/cn/article/doi/10.13374/j.issn2095-9389.2020.10.10.002), [S13](https://www.jstage.jst.go.jp/article/isijinternational/66/10/66_ISIJINT-2025-420/_html/-char/ja)|
|VD|真空罐脱气|core_optional|真空期间净热损|抽空/保压/破空/软吹分开|[S07](https://www.mdpi.com/2075-4701/13/7/1229)|
|VAD|真空加热精炼|extension|按配置电热平衡|真空与加热事件图|[S26](https://www.sms-group.com/en-us/plants/secondary-metallurgy)|
|WIRE|喂丝站|core_optional|喂入温降、释放及反应热|长度/速度＋后续混匀|[S30](https://www.jstage.jst.go.jp/article/isijinternational/63/2/63_ISIJINT-2022-274/_pdf)|
|POWDER|喷粉站/RH喷粉|extension|粉料热效应和载气损失|粉速积分，载气与提升气分开|[S08](https://doi.org/10.1007/s42243-023-00973-x), [S22](https://www.jstage.jst.go.jp/article/isijinternational/58/11/58_ISIJINT-2018-406/_html/-char/ja)|
|SOFT|软吹与静置|core|M18温降；包盖/渣层状态|相应设备模型和质量检测终止|[S01](https://www.jstage.jst.go.jp/article/isijinternational/57/2/57_ISIJINT-2015-701/_html/-char/en), [S16](https://journals.sagepub.com/doi/full/10.1080/03019233.2023.2218247)|
|TRANSFER|钢包运输/等候/保温|core|包衬热史、加盖与等待持续时间|调度事件日志|[S11](https://www.jstage.jst.go.jp/article/isijinternational/60/6/60_ISIJINT-2019-423/_pdf/-char/en), [S19](https://www.jstage.jst.go.jp/article/isijinternational/62/3/62_ISIJINT-2021-251/_pdf)|
|TD|中间包|core|液相线+过热度；首炉/稳态分开|RTD分布而非单一停留时间|[S20](https://www.jstage.jst.go.jp/article/isijinternational/advpub/0/advpub_ISIJINT-2023-008/_pdf), [S21](https://pmc.ncbi.nlm.nih.gov/articles/PMC9000347/)|
|TDHEAT|中间包感应/等离子加热|core_optional|功率与温度反馈热平衡|按浇注时间连续控制|[S21](https://pmc.ncbi.nlm.nih.gov/articles/PMC9000347/)|
|CC|连铸/EMS/软压下|core|液相线、固相线、二冷热传导|钢重/流量与拉速、断面、流数联算|[S20](https://www.jstage.jst.go.jp/article/isijinternational/advpub/0/advpub_ISIJINT-2023-008/_pdf)|
|INGOT|模铸/真空浇注|extension|液相线与补缩凝固计算|浇注曲线及凝固仿真|[S27](https://www.danieli.com/en/products/processes-technologies/product-lines/special-metallurgy_26_208.htm)|
|AODVOD|AOD/VOD|outside_core|按钢种分阶段热化学平衡|吹氧/还原/脱硫阶段|[S26](https://www.sms-group.com/en-us/plants/secondary-metallurgy)|
|VIMESRVAR|VIM/ESR/VAR|outside_core|独立合金体系和熔池模型|熔速/电极质量/凝固模型|[S27](https://www.danieli.com/en/products/processes-technologies/product-lines/special-metallurgy_26_208.htm)|
|ROLLHT|轧制/锻造/控冷/退火/淬回火/涂镀|downstream_interface|相变与传热模型；待专项建库|厚度/线速/保温及相变时间；尚未实现|守恒/几何推导，非文献拟合参数|

## 路线串联

- RT01 / STRUCT: TAP → LF → SOFT → TRANSFER → TD → CC。Q355Ti参考，Ti在低氧后加入；按订单决定是否Ca处理。状态：evidence_route。
- RT02 / STRUCT: TAP → LF → SOFT → TRANSFER → TD → CC。S355独立案例；不得与Q355配料拼为一炉。状态：evidence_route。
- RT03 / HOTSTRIP: TAP → LF → SOFT → TRANSFER → TD → CC。SPHC本厂目标案例，仅作参考。状态：evidence_route。
- RT04 / IF: TAP → LF → RHOB → SOFT → TRANSFER → TD → CC。LF可补热；RH强制供氧脱碳，最终脱氧顺序必须保留。状态：evidence_route。
- RT05 / IF: TAP → RH → SOFT → TRANSFER → TD → CC。热量及初始C/O满足时的候选；尚未绑定完整炉次。状态：evidence_route。
- RT06 / PIPE: TAP → LF → RH → WIRE → SOFT → TRANSFER → TD → CC。工程候选而非统一规定；H/S/夹杂目标决定真空与Ca处理。状态：engineering_candidate_not_verified。
- RT07 / PLATE: TAP → LF → VD → SOFT → TRANSFER → TD → CC。工程候选；VD能力不可从105t模型直接移植。状态：evidence_route。
- RT08 / REBAR: TAP → AR → TRANSFER → TD → CC。低成本候选，仅在成分温度洁净度均可满足时。状态：engineering_candidate_not_verified。
- RT09 / REBAR: TAP → LF → SOFT → TRANSFER → TD → CC。需升温/微合金/成分调整的候选。状态：engineering_candidate_not_verified。
- RT10 / REBAR: TAP → LF → SOFT → TRANSFER → TD → CC。HRB400进站渣优化案例，不能把进站氧化物目标当终渣脱硫目标。状态：partial_evidence_route。

## 后续规模化采集

1. 每个产品族先确定钢厂、设备和订单版本；采起点—操作时序—中间点—终点—铸坯实绩，不能只收最终合格炉次。
2. 原文图形数字化记录工具、坐标校准、读图误差，禁止标作原表实测。数值模拟案例记录原型/水模、几何相似比与流量换算。
3. 文献DOI去重不等于原始数据去重；文献引用同一历史数据集应保存dataset_group，避免训练验证重复。
4. 以钢厂/设备/钢种/吨位/流态建域，再做分层回归与带量纲检查的关联式；不把不同单位经验系数混合。
5. 若更改模型结构、数据或参数，保存模型版本、校准炉次及独立验证时间窗。不能用随机切分同炉时间点宣称独立验证。

## 尚未实现的全平台功能

本版不是自动工厂排程、全元素热力学引擎或最终产品性能认证。多合金优化、完整Al-O-渣-夹杂人口平衡、N去除/吸收、界面面积代理训练、多设备排队和下游性能模型已登记需求，但没有冒充实现。温度规则和设备目录也不是已经数字化的运行规程。
