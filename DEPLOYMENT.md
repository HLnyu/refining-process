# GitHub 与 Cloudflare 部署

唯一源码目录为 `D:\Steelmaking\refining-process-lab\refining-process`。以后在这里修改并运行检查，使用GitHub Desktop管理本地仓库，Cloudflare连接GitHub部署。不再默认生成ZIP或维护解压副本。

这是无服务端、无 CDN 依赖的静态网站。`dist/` 为完整发布目录，方案和成分记录只保存在当前浏览器本地。没有自动上传炉次数据的服务。

## 上传 GitHub

在GitHub Desktop添加现有本地仓库 `D:\Steelmaking\refining-process-lab\refining-process`，再发布到你选择的GitHub仓库。已保留目标目录原有Git仓库；远程地址由你在GitHub Desktop配置。父目录的Git历史和Sites托管身份没有导入；Cloudflare使用本目录的 `dist/` 与对应配置，不需要压缩包。

运行检查：安装 Node.js 后执行 `npm test`；静态文件检查 `npm run build`；本机预览 `npm start`，默认 http://127.0.0.1:8765 。不需要 npm install。

## Cloudflare Pages（连接 GitHub）

当前Pages项目为 `steelmakingz`，地址为 `https://steelmakingz.pages.dev/`。默认 `wrangler.jsonc` 使用Pages配置，并以 `pages_build_output_dir: "./dist"` 明确发布目录，不能发布仓库根目录。

连接该仓库，框架选 None；构建命令 `npm run build`；输出目录 `dist`；根目录保持仓库根目录（留空或 `/`，不要填 `dist`）。入口 `dist/index.html` 自动进入 `bed.html`。通过GitHub Desktop提交并Push后，核对Pages生产部署采用最新提交。GitHub Actions检查通过不等于Pages已经部署了同一提交。

若日志出现“配置无效、缺少pages_build_output_dir、Skipping file”，说明Pages没有采用正确配置。若部署成功但首页404，应核对输出目录确实为dist，以及该提交中存在dist/index.html。采用有效Wrangler配置后，输出目录以该配置为准。

也可以直接上传 `dist` 文件夹到 Cloudflare Pages Direct Upload。

## Cloudflare Workers Static Assets

Workers的配置已单独保存在 `wrangler.worker.jsonc`，assets.directory指向dist。只有选择Workers部署时才使用 `npx wrangler deploy --config wrangler.worker.jsonc`。不要把该文件当成Pages的默认配置；当前steelmakingz使用的是Pages。

官方说明（2026-10-27核对）：
- https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- https://developers.cloudflare.com/workers/static-assets/binding/

## 模型与资料的边界

真实文献数据保存在 evidence/downloads/，沿用原数据包的来源、核验状态和使用边界。论文数字与公式的引用不表示可以重分发出版社全文；本包不含出版社论文PDF。代码没有替第三方资料授予额外许可。

几何设计、入口成分和用户填写的参数不自动成为文献实测。连续槽的流态、界面面积、传质系数和加热效率尚无适用域验证；无法绑定的数值保持待输入。请阅读 BED_EVIDENCE.md 和 MODEL_VALIDATION.md。

