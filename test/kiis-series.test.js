import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {waves} from '../lib.js';
const read=name=>JSON.parse(fs.readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const d=read('research.json'),w=read('wording.json'),a=read('kiis-series-audit.json'),more=read('more-charts.json');

test('KIIS histories retain full comparable bins without duplicate wave categories',()=>{
 for(const [id,count,bins] of [['KIIS_WHO_WINS',6,5],['KIIS_REALISTIC_ENDING',5,6],['KIIS_ALLOW_NEGOTIATIONS',2,3],['KIIS_WAR_ENDURANCE',17,4]]){
  const ws=waves(d.dynamics.filter(r=>r.series===id));assert.equal(ws.length,count);
  assert.equal(a.series_counts[id],count);
  for(const wave of ws){assert.equal(wave.rows.length,bins);assert.equal(new Set(wave.rows.map(r=>r.answer)).size,bins);}
  assert.equal(ws.at(-1).poll,'P119');
 }
});

test('July CATI and mixed-mode estimates remain one wave with distinct snapshot bases',()=>{
 const rs=d.dynamics.filter(r=>r.series==='KIIS_WHO_WINS'&&r.poll==='P127');
 assert.deepEqual(rs.map(r=>r.pct),[.60,.25,.02,0,.13]);
 const z=w.items.find(z=>z.series==='KIIS_WHO_WINS'&&z.polls.includes('P127'));
 const panels=more.questions[z.question_ids[0]].plots;
 assert.equal(panels.length,3);assert.match(panels[0].caption,/905/);assert.match(panels[1].caption,/1808/);assert.match(panels[2].caption,/903/);
 assert.deepEqual(panels[0].rows.slice(-2).map(r=>r.value),[12,1]);
});

test('Preliminary December results are audited but never another independent point',()=>{
 const rs=d.dynamics.filter(r=>r.series==='KIIS_WAR_ENDURANCE');
 assert.equal(new Set(rs.filter(r=>r.sort==='2025-12').map(r=>r.poll)).size,1);
 assert(rs.every(r=>r.source!=='K1569'));
 assert.deepEqual(a.checks.find(c=>c.source==='K1569').values,[15,1,63,21]);
});

test('Historical instruments preserve wording changes and unknown date precision',()=>{
 const old=w.items.find(z=>z.series==='KIIS_REALISTIC_ENDING'&&z.polls.includes('P122'));
 const latest=w.items.find(z=>z.question_ids.includes('Q140'));
 assert.notEqual(old.question,latest.question);assert.notEqual(old.options[4],latest.options[4]);
 for(const pid of ['P120','P121','P123','P124','P125','P126']){
  const p=d.polls.find(p=>p.id===pid);assert.equal(p.date_precision,'month');assert.equal(p.n,null);
 }
 for(const q of d.questions.filter(q=>q.source==='K1372'))assert(more.questions[q.id]);
});
