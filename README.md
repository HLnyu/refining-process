# 连续精炼床研究工作台

唯一维护目录：**D:\Steelmaking\refining-process-lab\refining-process**。以后的代码都在此修改，直接通过GitHub Desktop管理本目录，并由Cloudflare发布；不再默认生成ZIP。`release/` 中的旧文件仅作历史交付记录。

当前版本是可追溯的条件评价原型，支持连续槽几何/流量、主体区段、并行喷吹/扒渣/补热、目标差距和方案比较。尚无本连续床工业标定，不能认证产品质量或保证设备产能。

## 本机使用

需要 Node.js；没有前端构建依赖，不必 npm install。

```text
npm start
npm test
npm run build
```

预览默认 http://127.0.0.1:8765 。首页进入 `bed.html`。

## GitHub Desktop 与 Cloudflare

在GitHub Desktop中添加本目录这个现有本地仓库，发布到你选择的GitHub仓库。后续在本目录修改、检查、提交和推送，无需压缩、解压或复制另一套源码。

源码目录已有 `package.json`、`wrangler.jsonc`、GitHub Actions检查和 `dist/` 静态网站。已保留本目录原有的Git仓库与 `.gitattributes`，未导入父目录的 `.git`、Sites托管身份或历史交付包。不要提交凭据、用户上传或求解器结果。研究参考数据不含出版社PDF；保留原来源和许可边界。

Cloudflare Pages项目 `steelmakingz` 连接仓库：框架None，构建 `npm run build`，发布目录 `dist`，仓库根目录留空。默认 `wrangler.jsonc` 已指定 `pages_build_output_dir: "./dist"`。Workers备用配置为 `wrangler.worker.jsonc`。详见 [DEPLOYMENT.md](DEPLOYMENT.md)。Cloudflare账户中的部署由GitHub推送触发。

## 代码入口

| 路径 | 用途 |
|---|---|
| dist/bed.html、bed-app.mjs、bed.css | 设计、评价、依据三个工作视图 |
| dist/bed-model.mjs | 几何、显热、一阶反应包络与并行操作核算 |
| dist/bed-planning.mjs | 目标任务、差距、缺参及流量情景 |
| dist/bed-catalog.mjs、bed-evidence.json | 原数据包目录和参考索引 |
| dist/evidence/ | 完整证据库、原单位、来源及下载数据 |
| dist/system-audit.json、platform.html | 完整性分层、扩展路线 |
| check-*.mjs | 计算边界和回归检查 |
| dist/laboratory.html、heating.html | 保留的旧精炼工具与详细热损工具 |

## 评价边界与后续开发

- [完整性审查](REVIEW_COMPLETENESS.md)：已修复的状态传播/达标误判，以及仍缺的热力学、质量平衡、RTD、夹杂与工业验证。
- [证据边界](BED_EVIDENCE.md)：参考数据不等于连续床参数标定。
- [集成架构](ARCHITECTURE.md)：GPT、参数化CAD、Fluent及场数据如何进入统一工作台。
- [后端接口草案](API_CONTRACT.md)：当前未实现，不是可用API。
- [历史说明](docs/HISTORY.md)：保留原有功能、模型和既往变更记录。

当前没有真实GPT调用、图纸自动转CAD或Fluent计算；这些能力需服务端与独立执行节点。以后接入时保存方案/模型/证据/运行版本，不用AI文字替代确定性计算或求解器验证。

