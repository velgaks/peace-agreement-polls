import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {csv} from '../lib.js';

const data=JSON.parse(fs.readFileSync(new URL('../data/research.json',import.meta.url),'utf8'));
const polls=Object.fromEntries(data.polls.map(p=>[p.id,p]));
const sources=new Set(data.sources.map(s=>s.id));
const statuses=new Set(['reported_day','reported_month','retrospective_day','wave_dates_unresolved','partial_aggregate','source_conflict','corrected_retrospective_label']);
const display=value=>value.split('-').reverse().join('.');
function day(value,end=false){
 assert.match(value,/^\d{4}-\d{2}(?:-\d{2})?$/);
 const iso=value.length===7?value+'-01':value;
 const date=new Date(iso+'T00:00:00Z');
 assert.equal(date.toISOString().slice(0,10),iso);
 if(end&&value.length===7)date.setUTCMonth(date.getUTCMonth()+1,0);
 return date.getTime();
}

test('All fieldwork periods preserve source precision and have an audit trail',()=>{
 assert.equal(data.polls.length,118);
 for(const p of data.polls){
  assert(p.fieldwork_periods.length>0,p.id);
  let previous=-Infinity;
  for(const period of p.fieldwork_periods){
   assert.equal(period.start.length,period.end.length,p.id);
   assert(day(period.start)>previous,p.id);
   assert(day(period.start)<=day(period.end,true),p.id);
   previous=day(period.end,true);
  }
  assert.equal(p.start,p.fieldwork_periods[0].start,p.id);
  assert.equal(p.end,p.fieldwork_periods.at(-1).end,p.id);
  assert.equal(p.period,p.fieldwork_periods.map(({start,end})=>start===end?display(start):`${display(start)}–${display(end)}`).join('; '),p.id);
  const lengths=new Set(p.fieldwork_periods.flatMap(v=>[v.start.length,v.end.length]));
  assert.equal(p.date_precision,lengths.size>1?'mixed':lengths.has(10)?'day':'month',p.id);
  assert.equal(p.date_kind,p.fieldwork_periods.length>1?'aggregate':'single_wave',p.id);
  assert(statuses.has(p.date_status),p.id);
  assert(sources.has(p.date_source),p.id);
  assert(p.date_note&&p.date_source_location,p.id);
  day(p.date_checked_on);
  if(p.published)day(p.published);
  assert.doesNotMatch(JSON.stringify(p),/перевірити|уточнити|потребує звірки/i,p.id);
 }
});

test('Gallup aggregate keeps the separate waves and unknown October days',()=>{
 assert.deepEqual(polls.P35.fieldwork_periods,[{start:'2024-08-13',end:'2024-08-29'},{start:'2024-10',end:'2024-10'}]);
 assert.equal(polls.P35.date_precision,'mixed');
 assert.equal(polls.P35.date_kind,'aggregate');
 assert.equal(polls.P35.date_status,'partial_aggregate');
 assert.equal(polls.P05.start,'2026-04');
 assert.equal(polls.P11.date_status,'wave_dates_unresolved');
 assert.equal(polls.P11.n,1003);
});

test('Primary ISPP reports correct chart months while retaining source conflicts',()=>{
 for(const [id,month] of [['P107','2023-05'],['P110','2023-10']]){
  const rows=data.dynamics.filter(r=>r.poll===id);
  assert(rows.length>0);
  assert(rows.every(r=>r.sort===month));
  assert(rows.every(r=>r.period===polls[id].period));
  assert.equal(polls[id].n,2000);
 }
 assert.equal(polls.P107.date_status,'source_conflict');
 assert.match(polls.P107.date_note,/8–19/);
 assert.match(polls.P107.date_note,/8–18/);
 assert.equal(polls.P110.date_status,'corrected_retrospective_label');
 assert.equal(polls.P115.start,'2024-09-27');
 assert.equal(polls.P115.end,'2024-10-01');
 assert.equal(polls.P117.end,'2025-08-20');
});

test('Browser CSV exports structured intervals as recoverable JSON',()=>{
 const periods=polls.P35.fieldwork_periods;
 const output=csv([{fieldwork_periods:periods}]);
 const cell=output.split('\r\n')[1];
 assert.deepEqual(JSON.parse(cell.slice(1,-1).replaceAll('""','"')),periods);
 assert(!output.includes('[object Object]'));
});
