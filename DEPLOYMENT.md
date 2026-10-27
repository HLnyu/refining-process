# GitHub 与 Cloudflare 部署

唯一源码目录为 `D:\Steelmaking\refining-process-lab\refining-process`。以后在这里修改并运行检查，使用GitHub Desktop管理本地仓库，Cloudflare连接GitHub部署。不再默认生成ZIP或维护解压副本。

这是无服务端、无 CDN 依赖的静态网站。`dist/` 为完整发布目录，方案和成分记录只保存在当前浏览器本地。没有自动上传炉次数据的服务。

## 上传 GitHub

在GitHub Desktop添加现有本地仓库 `D:\Steelmaking\refining-process-lab\refining-process`，再发布到你选择的GitHub仓库。已保留目标目录原有Git仓库；远程地址由你在GitHub Desktop配置。父目录的Git历史和Sites托管身份没有导入；Cloudflare使用本目录的 `dist/` 与对应配置，不需要压缩包。

运行检查：安装 Node.js 后执行 `npm test`；静态文件检查 `npm run build`；本机预览 `npm start`，默认 http://127.0.0.1:8765 。不需要 npm install。

## Cloudflare Pages（连接 GitHub）

创建 Pages 项目，连接该仓库。框架选 None；构建命令 `npm run build`；输出目录 `dist`；根目录为仓库根目录。入口 index.html 自动进入 bed.html。后续推送由你配置的 Pages 集成部署。

也可以直接上传 `dist` 文件夹到 Cloudflare Pages Direct Upload。

## Cloudflare Workers Static Assets

已附 wrangler.jsonc，assets.directory 指向 dist。安装官方 Wrangler 或使用 `npx wrangler deploy`，按 Cloudflare 的登录流程完成你的账户授权。发布名称可自行修改；无 Worker 服务端脚本或数据库绑定。

官方说明（2026-10-27核对）：
- https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- https://developers.cloudflare.com/workers/static-assets/binding/

## 模型与资料的边界

真实文献数据保存在 evidence/downloads/，沿用原数据包的来源、核验状态和使用边界。论文数字与公式的引用不表示可以重分发出版社全文；本包不含出版社论文PDF。代码没有替第三方资料授予额外许可。

几何设计、入口成分和用户填写的参数不自动成为文献实测。连续槽的流态、界面面积、传质系数和加热效率尚无适用域验证；无法绑定的数值保持待输入。请阅读 BED_EVIDENCE.md 和 MODEL_VALIDATION.md。

