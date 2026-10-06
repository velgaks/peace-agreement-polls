import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {indexWording,answerText} from '../wording.js';
import {packageRows,packagesHTML,packageCSVRows} from '../packages.js';
const read=f=>JSON.parse(fs.readFileSync(new URL('../data/'+f,import.meta.url),'utf8'));
const data=read('research.json'),wording=read('wording.json'),more=read('more-charts.json'),packages=read('kiis-packages.json');
const index=indexWording([...wording.items,...more.wording]),rows=packageRows(packages,data,index);
test('Repeated packages have identical instruments and two complete published distributions',()=>{
 for(const s of packages.series){
  const rr=rows.filter(r=>r.series===s.id);assert.equal(rr.length,2);
  for(const field of ['question','prompt','options'])assert.deepEqual(rr[0].w[field],rr[1].w[field]);
  for(const r of rr){const points=data.dynamics.filter(p=>p.series===s.id&&p.poll===r.p.id);assert.deepEqual(points.map(p=>Math.round(p.pct*100)),r.values);}
 }
});
test('Published rounding conflicts and nonresponse are preserved rather than inferred',()=>{
 const byq=new Map(rows.map(r=>[r.q.id,r]));
 assert.deepEqual(byq.get('Q051').values,[10,44,35,10]);
 assert.match(byq.get('Q051').note,/30%.*35%/);
 assert.deepEqual(byq.get('Q065').values,[4,27,61,7]);assert.equal(byq.get('Q065').reported_accept,32);
 assert.deepEqual(byq.get('Q04').values,[5,27,60,7,1]);assert.equal(byq.get('Q04').reported_accept,33);
 assert.deepEqual(byq.get('Q064').values,[61,10,21,9]);
 assert.deepEqual(byq.get('Q142').values,[69,22,9]);assert.equal(byq.get('Q142').w.options.length,6);
 assert.equal(byq.get('Q142').series,undefined);
});
test('Package comparison, question charts and CSV use the same audited rows and full wording',()=>{
 assert.equal(rows.length,27);
 for(const r of rows){
  assert.equal(r.values.length,r.answers.length);
  assert.deepEqual(more.questions[r.q.id].plots[0].rows.map(p=>p.value),r.values);
  const csv=packageCSVRows([r]);assert.equal(csv.length,r.values.length);
  assert.equal(csv[0].question_verbatim,r.w.question);assert.equal(csv[0].conditions_verbatim,r.w.prompt);
  assert.match(packagesHTML([r]),/Питання, повна шкала/);
 }
});
test('Reported category names have no editorial suffix in legends or snapshot labels',()=>{
 for(const w of [...wording.items,...more.wording])for(const [key,m] of Object.entries(w.mapping))if(m.kind==='reported')assert.equal(answerText(w,key),m.label);
 assert(!JSON.stringify(more.questions).includes('категорія графіка видавця'));
 assert(!packagesHTML(rows).includes('undefined'));
});
