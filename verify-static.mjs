import {readFileSync,existsSync} from 'node:fs';
const pagesConfig=JSON.parse(readFileSync('wrangler.jsonc','utf8'));
if(pagesConfig.pages_build_output_dir!=='./dist'||pagesConfig.assets)throw Error('Default Wrangler config must target Pages output ./dist');
for(const file of ['bed-planning.mjs','bed-catalog.mjs','platform.html','platform.css','system-audit.json'])if(!existsSync('dist/'+file))throw Error('Missing '+file);
for(const file of ['index.html','bed.html','bed-app.mjs','bed-model.mjs','bed-evidence.json','laboratory.html','heating.html','evidence/index.html','evidence/downloads/core-data.json'])if(!existsSync('dist/'+file))throw Error('Missing '+file);
const d=JSON.parse(readFileSync('dist/evidence/downloads/core-data.json','utf8'));
if(!d.sources?.length)throw Error('Evidence sources missing');
console.log('Static deployment assets and evidence present; no build dependency required.');
