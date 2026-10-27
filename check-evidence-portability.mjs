import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verifyEvidenceHash} from './evidence-integrity.mjs';

const metadata=JSON.parse(readFileSync('dist/bed-evidence.json','utf8'));
const lf=readFileSync('dist/evidence/downloads/core-data.json','utf8').replace(/\r\n/g,'\n');
const windows=Buffer.from(lf.replace(/\n/g,'\r\n'));
const linux=Buffer.from(lf);
assert.equal(verifyEvidenceHash(linux,metadata).lfHash,verifyEvidenceHash(windows,metadata).lfHash);
assert.equal(verifyEvidenceHash(windows,metadata).originalBytesMatch,true);
assert.equal(verifyEvidenceHash(linux,metadata).originalBytesMatch,false);

const data=JSON.parse(lf);data.sources[0].title+=' [changed]';
assert.throws(()=>verifyEvidenceHash(Buffer.from(JSON.stringify(data,null,2)),metadata),/Evidence content changed/);
assert.throws(()=>verifyEvidenceHash(Buffer.from(lf+' '),metadata),/Evidence content changed/);
console.log('PASS evidence accepts original CRLF and Git LF, rejects modified data and non-newline byte changes');
