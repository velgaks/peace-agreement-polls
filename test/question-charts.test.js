import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {questionChartsHTML,questionChartRows,valueText} from '../question-charts.js';
import {SERIES} from '../series.js';
import {indexWording,answerText} from '../wording.js';
const read=name=>JSON.parse(fs.readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const data=read('research.json'),more=read('more-charts.json'),wording=read('wording.json');
const index=indexWording([...wording.items,...more.wording]);
test('Every collected question has finite chart values, units, provenance and an export',()=>{
 assert.equal(Object.keys(more.questions).length,data.questions.length);
 for(const q of data.questions){
  const entry=more.questions[q.id],poll=data.polls.find(p=>p.id===q.poll);assert(entry.plots.length,q.id);
  for(const plot of entry.plots){assert(plot.rows.length);assert(plot.caption);assert.match(plot.source_url,/^https:\/\//);assert(['percent','mean5','mean10'].includes(plot.unit));
   for(const row of plot.rows){assert(row.label);assert(Number.isFinite(row.value));assert(row.value>=0&&row.value<=(plot.unit==='percent'?100:Number(plot.unit.slice(4))));}
  }
  const html=questionChartsHTML(q.id,entry,poll);assert(!html.includes('undefined'));assert(!html.includes('NaN'));assert(html.includes('data-question-csv'));
  assert.equal(questionChartRows(q.id,entry,index.byQuestion.get(q.id),poll,q.base).length,entry.plots.flatMap(p=>p.rows).length);
 }
});
test('All 23 registered time series have mappings and maintain source wording',()=>{
 assert.equal(SERIES.length,23);
 for(const meta of SERIES){const rows=data.dynamics.filter(r=>r.series===meta.id);assert(rows.length);for(const row of rows)assert(answerText(index.byWave.get(meta.id+'|'+row.poll),row.answer));}
 const old=index.byWave.get('SOCIS_CONCESSIONS_MULTI|P72');assert(!old.options.includes('ЖОДНИХ ПОСТУПОК'));
 assert(index.byWave.get('SOCIS_CONCESSIONS_MULTI|P74').options.includes('ЖОДНИХ ПОСТУПОК'));
});
test('Bounded means, experimental marginals and subgroup percentages are not mixed',()=>{
 assert.equal(more.questions.Q107.plots[0].unit,'mean10');assert.equal(more.questions.Q107.plots[0].rows.length,11);
 assert.equal(valueText(more.questions.Q107.plots[0],3.3),'3,3');
 assert.equal(more.questions.Q111.plots[1].unit,'mean5');
 assert.equal(more.questions.Q25.plots.length,13);assert.match(more.questions.Q25.note,/11–30/);
 assert.match(more.questions.Q23.plots[0].caption,/Лише серед/);
 assert.match(more.questions.Q109.plots[0].caption,/переказ/);
 assert.equal(more.questions.Q13.plots[0].rows[0].value,55);
 assert.equal(data.dynamics.find(r=>r.series==='NDI_PEACE_PRICE_TERRITORY_REJECT'&&r.poll==='P10'&&r.answer==='Повністю не приймаю').pct,.55);
});

test('Scenario charts retain the complete Info Sapiens and NDI distributions',()=>{
 assert.equal(more.questions.Q114.plots.length,3);
 assert.deepEqual(more.questions.Q114.plots.map(p=>p.rows.map(r=>r.value)),[[82,11,7],[80,13,7],[45,37,18]]);
 assert.deepEqual(more.questions.Q137.plots[0].rows.map(r=>r.value),[58,12,9,5,15]);
 assert.deepEqual(more.questions.Q138.plots[0].rows.map(r=>r.value),[59,13,8,6,14]);
});
test('Chart labels and source strings are HTML escaped',()=>{
 const html=questionChartsHTML('Q', {series:[],plots:[{rows:[{label:'<script>alert(1)</script>',value:5}],unit:'percent',heading:'<bad>',caption:'a&b',source_url:'https://example.com/?q="test"',location:'<page>'}]},{pollster:'<name>',period:'2026'});
 assert(!html.includes('<script>'));assert(html.includes('&lt;script&gt;'));assert(html.includes('a&amp;b'));
});
