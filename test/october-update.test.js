import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {waves,mainSource} from '../lib.js';
const read=f=>JSON.parse(fs.readFileSync(new URL('../data/'+f,import.meta.url),'utf8'));
const d=read('research.json'),w=read('wording.json'),more=read('more-charts.json'),update=read('update-2026-10-19.json');
const points=id=>waves(d.dynamics.filter(r=>r.series===id));
test('October repeats extend their own pollster series and quoted September results are not new waves',()=>{
 assert.equal(points('KIIS_DONBAS_GUARANTEES_2026').length,7);
 assert.deepEqual(points('KIIS_DONBAS_GUARANTEES_2026').at(-1).rows.map(r=>r.pct),[.35,.61]);
 assert.equal(points('KIIS_WAR_ENDURANCE').length,18);
 assert.equal(points('KIIS_ALLOW_NEGOTIATIONS').at(-1).poll,'P119');
 assert.equal(d.polls.filter(p=>p.source==='K1643').length,1);
 assert.equal(d.questions.filter(q=>q.poll==='P128'&&q.dimension==='Експеримент формулювання').length,3);
});
test('Rating keeps all retrospective waves and distinct monthly I/II samples without assigning days',()=>{
 for(const [id,n] of [['RATING_REALISTIC_END',26],['RATING_CURRENT_WAR_STATE',21],['RATING_PEACE_OR_VICTORY',33],['RATING_WAR_SCENARIO',27],['RATING_DECIDE_TERRITORY',3],['RATING_TERRITORY_GUARANTEES',2]])assert.equal(points(id).length,n,id);
 const june=points('RATING_CURRENT_WAR_STATE').filter(w=>w.sort==='2026-06');assert.equal(june.length,2);
 for(const wave of june){const p=d.polls.find(p=>p.id===wave.poll);assert.equal(p.date_precision,'month');assert.equal(p.n,null);assert.match(p.wave_label,/хвиля I/);}
 const latest=points('RATING_WAR_SCENARIO').at(-1);assert.deepEqual(latest.rows.map(r=>r.pct),[.57,.05,.04,.13,.21]);
});
test('Revised publisher retrospectives never overwrite the original small categories or invent zeros',()=>{
 const old=d.dynamics.filter(r=>r.series==='RATING_REALISTIC_END'&&r.poll==='P103');
 assert.equal(old.find(r=>r.answer==='Інше').pct,.03);
 assert.equal(old.find(r=>r.answer==='Погодитися на більшість вимог росії').pct,.01);
 const latest=points('RATING_REALISTIC_END').at(-1).rows;
 assert(latest.some(r=>r.answer==='Прямі переговори з росією'&&r.pct===.26));
 assert(!latest.some(r=>r.answer==='Погодитися на більшість вимог росії'));
 assert(!d.dynamics.some(r=>r.series==='RATING_REALISTIC_END'&&r.sort<'2025-04'&&r.answer==='Прямі переговори з росією'));
});
test('Calendar end-date comparisons use stated aggregations with full original scales in question charts',()=>{
 const ww=w.items.filter(z=>z.series==='KIIS_EXPECTED_END_2026_2027');assert.equal(ww.length,2);
 const july=ww.find(z=>z.polls.includes('P02')),oct=ww.find(z=>z.polls.includes('P128'));
 assert.deepEqual(july.mapping['До кінця 2026'].indices,[0,1]);assert.deepEqual(oct.mapping['Друге півріччя 2027 або пізніше'].indices,[2,3]);
 assert.deepEqual(more.questions[oct.question_ids[0]].plots[0].rows.map(r=>r.value),[10,13,17,39,21]);
});
test('Regional tables are parsed once without collecting the surrounding page layout',()=>{
 const rows=d.crosses.filter(r=>r.source==='K1643');assert.equal(rows.length,48);
 assert.equal(new Set(rows.map(r=>[r.question,r.group,r.answer].join('|'))).size,48);
 assert.equal(new Set(rows.map(r=>r.group)).size,6);
 assert.equal(rows.find(r=>r.question==='Донбас в обмін на гарантії'&&r.group==='Захід'&&r.answer==='Готові схвалити').pct,.34);
});
test('Online panel remains additional and code 99 is uncertainty, not a numeric score',()=>{
 for(const m of update.series.filter(s=>s.id.startsWith('LEMUR_'))){
  const ww=points(m.id);assert.equal(ww.length,7);for(const wave of ww)assert(!mainSource(d.polls.find(p=>p.id===wave.poll)));
 }
 const z=w.items.find(z=>z.series==='LEMUR_NATO_EU_SUCCESS'&&z.polls.includes('P130'));
 const q=more.questions[z.question_ids[0]];assert.equal(q.plots[0].rows.length,11);
 assert.equal(z.options.at(-1),'важко відповісти');assert.equal(q.plots[0].rows.at(-1).value,15);
 assert.equal(d.polls.find(p=>p.id==='P130').end,'2026-10-01');
});
