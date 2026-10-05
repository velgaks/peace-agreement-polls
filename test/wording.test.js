import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {SERIES} from '../series.js';
import {indexWording,wordingKey,answerText,basisLabel} from '../wording.js';
const read=name=>JSON.parse(fs.readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const data=read('research.json'),wording=read('wording.json'),more=read('more-charts.json'),index=indexWording([...wording.items,...more.wording]);
test('Every plotted measurement has a source-specific question and answer mapping',()=>{
 const series=new Set(SERIES.map(s=>s.id));
 for(const row of data.dynamics.filter(r=>series.has(r.series))){
  const item=index.byWave.get(wordingKey(row.series,row.poll));
  assert(item,`${row.series} ${row.poll}`);assert(item.question);assert(item.options.length);
  assert.match(item.source_url,/^https:\/\//);assert(answerText(item,row.answer));
 }
});
test('NDI and IRI retain the published uncertainty labels',()=>{
 assert.equal(answerText(index.byWave.get('NDI_ENTER_NEGOTIATIONS|P60'),'Не визначилися'),'Не знаю');
 assert.equal(answerText(index.byWave.get('IRI_PEACE_REFERENDUM|P114'),'Важко відповісти / немає відповіді'),'Важко відповісти/Немає відповіді');
});
test('Donbas acceptance is explicitly an aggregate of two verbatim answers',()=>{
 const jan=index.byWave.get('KIIS_DONBAS_GUARANTEES_2026|P49'),jul=index.byWave.get('KIIS_DONBAS_GUARANTEES_2026|P02');
 assert.equal(jan.options[2],'Ця умова абсолютна неприйнятна');
 assert.equal(jul.options[2],'Ця умова абсолютно неприйнятна');
 assert.deepEqual(jan.mapping['Приймають'].indices,[0,1]);
 assert.match(answerText(jan,'Приймають'),/^Сума відповідей:/);
});
test('SOCIS preserves wording changes instead of assigning the latest text to old waves',()=>{
 const may=index.byWave.get('SOCIS_WAR_SCENARIO|P71'),june=index.byWave.get('SOCIS_WAR_SCENARIO|P74');
 assert.match(may.options[2],/Мінських угод/);assert(!june.options[2].includes('Мінських угод'));
 assert.match(june.question,/один найбільш підходящий варіант відповіді/);
 assert.equal(june.options[0][0],'п');
});
test('Missing historical questionnaires and publication language stay explicit',()=>{
 assert.equal(index.byWave.get('KIIS_TERRITORY_GENERAL|P26').basis,'reference');
 assert.equal(index.byWave.get('GALLUP_NEGOTIATIONS|P05').language,'en');
 assert.equal(index.byWave.get('GALLUP_NEGOTIATIONS|P05').basis,'publication-language');
 for(const id of index.byQuestion.keys())assert(data.questions.some(q=>q.id===id));
});

test('Every catalogue record is audited; unavailable instruments are never fabricated',()=>{
 assert.equal(index.byQuestion.size,data.questions.length);
 const missing=[];
 for(const q of data.questions){
  const w=index.byQuestion.get(q.id);assert(w,q.id);assert(basisLabel(w));
  assert.match(w.source_url,/^https:\/\//);assert(w.reviewed_on);
  if(w.basis==='unavailable'){missing.push(q.id);assert.equal(w.question,'');assert.deepEqual(w.options,[]);assert(w.note);}
  else {assert(w.question);assert(w.options.length||w.partial_options?.length);}
 }
 assert.deepEqual(missing,wording.review.missing_full_wording);
});
test('NDI retrospective records retain their own wave and only published scale fragments',()=>{
 for(const [current,old] of [['Q13','Q137'],['Q14','Q138']]){
  const a=index.byQuestion.get(current),b=index.byQuestion.get(old);
  assert.notEqual(a.id,b.id);assert.deepEqual(a.polls,['P10']);assert.deepEqual(b.polls,['P117']);
  assert.equal(a.options.length,5);assert.equal(b.basis,'retrospective');assert.equal(b.options.length,0);assert.equal(b.partial_options.length,2);
 }
});
test('Batteries and bundled catalogue entries retain distinct statements and scales',()=>{
 assert.equal(index.byQuestion.get('Q107').statements.length,11);
 assert.equal(index.byQuestion.get('Q114').statements.length,3);
 assert.equal(index.byQuestion.get('Q088').followups[0].statements.length,3);
 assert.match(index.byQuestion.get('Q12').question,/КОНКРЕТНІ КРОКИ/);
 assert.match(index.byQuestion.get('Q116').location,/4/);
});
