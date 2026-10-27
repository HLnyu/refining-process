import assert from 'node:assert/strict';
import {defaults} from './dist/blend-model.mjs';
import {suggestPlans} from './dist/blend-plan.mjs';
for(const family of ['structural','bearing','stainless']){const c=defaults(family),snapshot=JSON.stringify(c),plans=suggestPlans(c);assert.ok(plans.length>0&&plans.length<=6);assert.equal(JSON.stringify(c),snapshot);for(const p of plans){assert.ok(p.result.valid);assert.ok(Number.isFinite(p.score));assert.ok(Number.isFinite(p.result.totals.time));}c.feeds.forEach(f=>f.Cu=2);assert.ok(suggestPlans(c).every(p=>!p.result.feasible));}
console.log('3 product families: candidate integrity, immutable inputs, residual-element infeasibility passed');
