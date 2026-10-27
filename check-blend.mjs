import assert from 'node:assert/strict';
import {defaults,evaluate,validate} from './dist/blend-model.mjs';
let n=0;const test=(name,fn)=>{fn();n++;console.log('PASS',name)};
test('mixture mass and sulfur',()=>{const c=defaults();c.route=[];const r=evaluate(c);assert.equal(r.mixed.mass_t,100);assert.ok(Math.abs(r.mixed.S-.0225)<1e-9)});
test('TO cannot be below dissolved oxygen',()=>{const c=defaults();c.feeds[0].TO=1;assert.ok(validate(c).length)});
test('sulfur conservation',()=>{const c=defaults();c.route=c.route.slice(0,1);const r=evaluate(c);const start=r.mixed.mass_t*1000*r.mixed.S/100+1500*.02/100;const end=r.final.mass_t*1000*r.final.S/100+r.stages[0].slagSkg;assert.ok(Math.abs(start-end)<1e-8)});
test('gas dose and nested duration',()=>{const r=evaluate(defaults());assert.equal(r.totals.time,55);assert.equal(r.totals.gasNm3,14.3)});
test('capacity violation',()=>{const c=defaults();c.feeds[0].mass_t=200;assert.equal(evaluate(c).capacity,false)});
test('zero oxygen bounds carbon',()=>{const c=defaults('stainless');c.feeds.forEach(f=>{f.Odiss=0;f.TO=0});c.route=[{...c.route[0],oxygenNm3:0}];const r=evaluate(c);assert.ok(Math.abs(r.final.C*r.final.mass_t-r.mixed.C*r.mixed.mass_t)<1e-9)});
test('unremoved residual blocks target',()=>{const c=defaults();c.feeds.forEach(f=>f.Cu=1);assert.equal(evaluate(c).feasible,false)});
test('no negative oxygen',()=>{const c=defaults();c.route[0].AlKg=1000;const r=evaluate(c);assert.ok(r.final.Odiss>=0);assert.ok(r.final.TO>=r.final.Odiss)});
console.log(`${n} tests passed`);

test('strict numeric missing params',()=>{const c=defaults();c.feeds[0].S=null;assert.ok(validate(c).length);c.feeds[0].S=.01;delete c.params.kS;assert.ok(validate(c).length)});
test('alloy carrier multielement mass balance',()=>{const c=defaults();c.feeds.forEach(f=>f.Odiss=0);c.route=[{...c.route[0],time:0,AlKg:0,additions:[{type:'SiMn',kg:100,recovery:.9}]}];const r=evaluate(c);assert.ok(Math.abs(r.final.mass_t-100.09)<1e-8);assert.ok(Math.abs(r.final.Si*r.final.mass_t*10-(r.mixed.Si*1000+90*.17))<1e-7)});
test('phase guard stops route',()=>{const c=defaults();c.params.coolingKMin=50;const r=evaluate(c);assert.equal(r.phaseValid,false);assert.equal(r.stages.length,1);assert.equal(r.feasible,false)});
test('oxygen ledger closes',()=>{const c=defaults('stainless');const r=evaluate(c);const a=r.stages[0].oxygenLedger;assert.ok(Math.abs(a.suppliedKg-a.notAbsorbedKg-a.reactedKg)<1e-9)});
test('editable equipment respected',()=>{const c=defaults();c.equipment.LF.maxBatchT=50;assert.equal(evaluate(c).capacity,false)});
console.log(`${n} total tests passed`);

