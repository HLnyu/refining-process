# 普钢精炼核心数据支持包 v0.1

更新：2026-10-26。窗口2016-10-26—2026-10-26，定向检索，不是十年穷尽统计。

核心参考207条，完整底稿221条；历史复用11条、待核隔离3条。
36条来源包括期刊、钢厂公告及2条无日期设备商资料，不等于36个可训练工业数据集。8个同源可对齐工业炉次，原始heat_imports与本厂calibrations均为0。

## 怎么使用

- core.sqlite：只含核心参考观测的SQLite；source/case目录保留以便关联。空工况不表示有定量证据。
- core-observations.csv / core-data.json：核心参考数据，带原单位、SI换算、原文定位、URL与适用工况。
- all-observations.csv：221条完整底稿；historical.csv与quarantined.csv明确列出排除项。
- sources.csv、models.csv、cases.csv、equipment.csv、routes.csv、reactions.csv：目录和关系。
- model-guide.md：公式、推导、单位、适用域和模型状态；quality-audit.md：数据风险与缺口。
- models.py：可执行研究计算内核；完整源码和43项测试的运行环境见另附完整数据库包。

R原文值不自动等于工业实测；D换算；A作者假设/数值输入或CFD结果；F拟合或推荐；U待核。
核心参考仍包括物理模型和数值模型，不能当所有记录都是工业测量。未知气体标准状态保持unspecified，不按惯例改成Nm³。
21个模型条目有可执行计算函数，5个为待实现设计；均未在目标钢厂完成工业精度标定。公式测试通过不等于工艺保证。

## 数据谱系

原始数据库SHA256：4351d35e0eb169181cdea6eff48b8232a7e4934a2eca09248e020398547f473b
来源—工况—观测—换算—模型—路线关系见SQLite和JSON。不同文献不能拼成同一炉次。水油体系分配比不能冒充钢渣硫分配比。
