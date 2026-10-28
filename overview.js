import {esc,pct,unique,waves,timeValue} from './lib.js';
import {answerText,questionText,basisLabel,wordingKey} from './wording.js';
import {OVERVIEW_INDICATORS,OVERVIEW_CHARTS,latestIndicator} from './overview-data.js';

const COLORS=['#2a78d6','#eb6834','#52514e','#0d366b','#898781','#5598e7'];
const number=new Intl.NumberFormat('uk-UA',{maximumFractionDigits:1});
const valueText=value=>value===null?'Немає даних':pct(value);
const deltaText=change=>change===null?'Немає порівняння'
 :change===0?'→ 0 в. п.':`${change>0?'↑ +':'↓ −'}${number.format(Math.abs(change))} в. п.`;

export function renderOverview(container,{data,series,wordingIndex,drawChart,sourceLink,field,credit}){
 const polls=Object.fromEntries(data.polls.map(p=>[p.id,p]));
 const exactFor=(id,poll)=>wordingIndex.byWave.get(wordingKey(id,poll));
 const period=wave=>wave?field(wave.rows[0]):'Дата не встановлена';
 const indicatorHTML=config=>{
  const item=latestIndicator(config,data.dynamics,{polls,sources:data.sources,wordingIndex});
  const meta=series.find(s=>s.id===config.series);
  const comparison=item.change===null?'Попередній зіставний показник недоступний.'
   :`Попередній: ${pct(item.previousValue)} · ${period(item.previous)}`;
  return `<article class="indicator-card">
   <div class="indicator-topline"><span>${esc(meta.org)}</span><span>${esc(period(item.latest))}</span></div>
   <h3 class="indicator-label">${esc(config.label)}</h3>
   <p class="indicator-value">${valueText(item.value)}</p>
   <p class="indicator-change" aria-label="${esc('Зміна до попереднього заміру: '+deltaText(item.change))}">${deltaText(item.change)}</p>
   <p class="indicator-comparison">${esc(comparison)}</p>
   <details class="indicator-answer"><summary>Питання та джерело</summary>
    ${item.wording?`<p class="verbatim">${esc(questionText(item.wording))}</p><p>${item.wording.mapping?.[config.answer]?'Відповідь: '+esc(answerText(item.wording,config.answer)):'Цю категорію в останньому замірі не наведено.'}</p><p>${esc(basisLabel(item.wording))}.</p>`:''}
    ${item.wordingChanged?'<p>Текст або інструкції відрізняються між хвилями. Версії та примітки — у паспорті ряду.</p>':''}
    <p>${sourceLink(item.source?.id,'Останній замір ↗')}${item.previousSource?' · '+sourceLink(item.previousSource.id,'Попередній замір ↗'):''}</p>
    <p>${esc(meta.note)}</p>
   </details>
   <a class="indicator-link" href="#trends?series=${config.series}">Динаміка та повне питання ↗</a>
  </article>`;
 };
 container.querySelector('#overview-indicators').innerHTML=OVERVIEW_INDICATORS.map(indicatorHTML).join('');

 const chartRows=new Map();
 const chartHTML=id=>{
  const meta=series.find(s=>s.id===id);
  const rows=data.dynamics.filter(r=>r.series===id).sort((a,b)=>timeValue(a.sort)-timeValue(b.sort));
  chartRows.set(id,rows);
  const ws=waves(rows),latest=ws.at(-1),exact=exactFor(id,latest.poll);
  const answers=meta.order||unique(rows.map(r=>r.answer));
  const legend=answers.map((answer,i)=>{
   const wording=[...ws].reverse().map(w=>exactFor(id,w.poll)).find(w=>w?.mapping[answer]);
   const row=latest.rows.find(r=>r.answer===answer);
   return `<div class="overview-legend-item"><i class="legend-mark" style="border-color:${COLORS[i%COLORS.length]};border-top-style:${i?'dashed':'solid'}" aria-hidden="true"></i><span class="overview-answer">${esc(answerText(wording,answer))}</span><strong${row?'':' title="В останньому замірі не опубліковано"'}>${row?pct(row.pct):'—'}</strong></div>`;
  }).join('');
  return `<article class="overview-card" data-overview-series="${id}">
   <div class="chart-meta"><span>${esc(meta.org)}</span><span>Заміри: ${ws.length} · ${esc(ws[0].sort.slice(0,4))}–${esc(latest.sort.slice(0,4))}</span></div>
   <h3 class="overview-title">${esc(meta.title)}</h3>
   <p class="small muted">Останній замір: ${esc(period(latest))} · ${sourceLink(latest.rows[0].source,meta.org+' ↗')}</p>
   <details class="overview-question"><summary>Питання з джерела</summary><p class="verbatim">${esc(questionText(exact))}</p><p>${esc(basisLabel(exact))}. <a href="${esc(exact.source_url)}" target="_blank" rel="noopener">Джерело формулювання ↗</a></p></details>
   <div class="overview-legend" aria-label="Відповіді та частки в останньому замірі">${legend}</div>
   <div class="overview-plot"></div>
   <p class="overview-readout" aria-live="polite">Оберіть точку. Клавіатура: Tab до графіка, ← / → між точками.</p>
   <p class="small muted">${esc(meta.caption)}</p>
   <details class="overview-note"><summary>Формулювання та методика</summary><p>${esc(meta.note)}</p><p>${esc(exact.note)}</p></details>
   <div class="overview-credit"><strong>${esc(credit.credit)}</strong> Джерело: ${esc(meta.org)}; ${esc(credit.retrieved)}.<br>${esc(credit.repo)}</div>
   <a class="overview-card-link" href="#trends?series=${id}">Повний графік, паспорт і дані ↗</a>
  </article>`;
 };
 container.querySelector('#overview-charts').innerHTML=OVERVIEW_CHARTS.map(chartHTML).join('');

 const draw=plot=>{
  const width=Math.round(plot.getBoundingClientRect().width);
  if(!width||Number(plot.dataset.width)===width)return;
  plot.dataset.width=width;
  const card=plot.closest('[data-overview-series]'),id=card.dataset.overviewSeries;
  const rows=chartRows.get(id),meta=series.find(s=>s.id===id);
  plot.innerHTML=drawChart(meta,rows,{compact:true,width});
  const readout=card.querySelector('.overview-readout');
  const points=[...plot.querySelectorAll('[data-point]')];
  points.forEach((point,index)=>{
   point.setAttribute('tabindex',index===0?'0':'-1');
   const show=()=>{
    const row=rows[Number(point.dataset.point)];
    readout.innerHTML=`<strong>${esc(field(row))}</strong> · ${esc(answerText(exactFor(id,row.poll),row.answer))}: <strong>${pct(row.pct)}</strong> · ${sourceLink(row.source,'Джерело ↗')}`;
   };
   point.addEventListener('mouseenter',show);
   const activate=()=>{points.forEach(p=>p.setAttribute('tabindex',p===point?'0':'-1'));show();};
   point.addEventListener('focus',activate);
   point.addEventListener('click',activate);
   point.addEventListener('keydown',event=>{
    let next;
    if(event.key==='ArrowRight')next=(index+1)%points.length;
    else if(event.key==='ArrowLeft')next=(index+points.length-1)%points.length;
    else if(event.key==='Home')next=0;
    else if(event.key==='End')next=points.length-1;
    else return;
    event.preventDefault();points[next].focus();
   });
  });
 };
 const plots=container.querySelectorAll('.overview-plot');
 plots.forEach(draw);
 // Recompute geometry at each card's actual width so mobile labels stay readable.
 const observer=new ResizeObserver(entries=>entries.forEach(({target})=>draw(target)));
 plots.forEach(plot=>observer.observe(plot));
 return ()=>observer.disconnect();
}
