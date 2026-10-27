# 后续服务接口草案（当前未实现）

当前网页不发起下列请求；不要把草案当作可用服务。实际接入时以版本化JSON Schema和服务测试补齐字段、权限与错误码。

## 统一输入

以现有方案JSON中的 `config` 为设计输入，保存 `schemaVersion`、`scenarioId`、`modelVersion`、`sourceCommit`、`evidenceIds` 和单位声明。每项外部图纸/CAD/网格/实验文件以受控 `assetId` 引用，禁止让模型提供任意本机文件路径或shell命令。

## 请求与返回

| 草案端点 | 输入 | 返回 |
|---|---|---|
| POST /api/evaluations | config、模型版本、证据 | 单位/条件错误、计算结果、缺参项、约束及适用域 |
| POST /api/proposals | 当前方案、用户目标、允许工具 | 参数变更提案、引用、假设、需核实项；不直接覆盖原方案 |
| POST /api/jobs/cad | 方案版本、几何模板、已复核尺寸 | jobId、queued状态；完成后几何检查报告、STEP/预览assetId |
| POST /api/jobs/fluent-prepare | 几何/网格引用、物性、边界、版本 | jobId；完成后准备清单与脚本，不宣称求解完成 |
| POST /api/jobs/fluent-run | 已审核准备包、许可证节点配置、资源上限 | jobId；状态和日志由后续查询返回 |
| GET /api/jobs/:id | 所属用户的jobId | queued/running/succeeded/failed/cancelled、进度、日志、产物、运行版本 |

失败和参数不足为显式状态。没有真实求解器任务及质量检查记录时，不提供“已完成CFD”的标记或伪造场图。

## 权责

网页负责提案查看与版本确认；确定性模型负责计算；服务端负责凭据及权限；计算节点负责真正运行；GPT负责理解、调用受控工具和解释。模型输出即使满足JSON结构，也不保证工程正确。
