import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import path from 'node:path';

const pages=JSON.parse(readFileSync('wrangler.jsonc','utf8'));
const worker=JSON.parse(readFileSync('wrangler.worker.jsonc','utf8'));
assert.equal(pages.name,'steelmakingz');
assert.equal(pages.pages_build_output_dir,'./dist','Pages must publish dist, not the source repository root');
assert.equal(pages.assets,undefined,'Worker-only asset settings must not leak into Pages configuration');
assert.ok(existsSync(path.join(pages.pages_build_output_dir,'index.html')),'Published output needs a root index.html');
assert.ok(existsSync(path.join(pages.pages_build_output_dir,'bed.html')));
assert.equal(worker.assets.directory,'./dist');
assert.equal(worker.pages_build_output_dir,undefined);
console.log('PASS Pages publishes dist with an index; Worker configuration remains separate');
