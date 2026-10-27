import {EQUIPMENT_IDS} from './dist/bed-catalog.mjs';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verifyEvidenceHash} from './evidence-integrity.mjs';
const raw=readFileSync('dist/evidence/downloads/core-data.json'),core=JSON.parse(raw),bed=JSON.parse(readFileSync('dist/bed-evidence.json','utf8'));
verifyEvidenceHash(raw,bed);
for(const row of bed.observations){const original=core.observations.find(x=>x.observation_id===row.observation_id);assert.deepEqual(row,original);}
for(const group of bed.groups){assert.equal(group.auto_apply,false);for(const id of group.observation_ids)assert.ok(bed.observations.some(x=>x.observation_id===id));}
console.log(`${bed.observations.length} reference records unchanged; source hash and case groups verified`);

assert.deepEqual(EQUIPMENT_IDS,core.equipment.map(x=>x.equipment_id));
