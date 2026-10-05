import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {waves,segments,timeValue,csv} from '../lib.js';
import {SERIES} from '../series.js';
const d=JSON.parse(fs.readFileSync(new URL('../data/research.json',import.meta.url),'utf8'));
test('All public figures retain valid survey and source references',()=>{
 const p=new Set(d.polls.map(r=>r.id)),s=new Set(d.sources.map(r=>r.id));
 for(const r of [...d.dynamics,...d.crosses,...d.questions]){assert(p.has(r.poll));assert(s.has(r.source));}
 for(const r of [...d.dynamics,...d.crosses])assert(Number.isFinite(r.pct)&&r.pct>=0&&r.pct<=1);
 assert.equal(SERIES.length,12);
 for(const series of SERIES){const rs=d.dynamics.filter(r=>r.series===series.id);assert(waves(rs).length>=2);const keys=rs.map(r=>r.poll+'|'+r.sort+'|'+r.answer);assert.equal(new Set(keys).size,keys.length);}
});
test('Two January Donbas measurements remain distinct',()=>{
 const ws=waves(d.dynamics.filter(r=>r.series==='KIIS_DONBAS_GUARANTEES_2026'));
 assert.equal(ws.length,6);assert.equal(ws.filter(w=>w.sort.startsWith('2026-01')).length,2);assert(ws[0].time<ws[1].time);
});
test('An absent option remains absent rather than becoming zero',()=>{
 const ws=waves(d.dynamics.filter(r=>r.series==='RAZUMKOV_MINIMUM_PEACE'));
 const seg=segments(ws,'Виведення ЗСУ з Донбасу');assert.equal(seg.length,1);assert.equal(seg[0].length,1);assert.equal(seg[0][0].pct,.037);
 const synthetic=waves([{poll:'a',sort:'2024-01',answer:'x',pct:.2},{poll:'b',sort:'2024-02',answer:'y',pct:.4},{poll:'c',sort:'2024-03',answer:'x',pct:.3}]);assert.equal(segments(synthetic,'x').length,2);
});
test('IRI connects all published waves without dropping values',()=>{
 const ws=waves(d.dynamics.filter(r=>r.series==='IRI_PEACE_REFERENDUM'));
 const seg=segments(ws,'Однозначно підтримую');assert.deepEqual(seg.map(s=>s.length),[3]);assert.equal(seg[0].at(-1).pct,.27);
});
test('NDI keeps published aggregates instead of sums of rounded bins',()=>{
 const rs=d.dynamics.filter(r=>r.series.startsWith('NDI_PEACE_PRICE_')&&r.sort==='2026-03');assert.equal(rs.length,2);assert(rs.every(r=>r.pct===.7));
});
test('CSV preserves decimals, quotes and multiline notes; times use UTC',()=>{
 assert(csv([{answer:'a,"b"',pct:.037,note:'one\ntwo'}]).includes('"a,""b"""'));
 assert.equal(new Date(timeValue('2026-01-09')).toISOString(),'2026-01-09T00:00:00.000Z');
});
