import {esc,pct} from './lib.js';
const number=n=>new Intl.NumberFormat('uk-UA',{maximumFractionDigits:2}).format(n);
export function valueText(plot,value){return plot.unit==='percent'?pct(value/100):number(value);}
export function questionChartsHTML(id,entry,poll){
 if(!entry)return '';
 const plots=entry.plots.map((plot,i)=>{
  const mean=plot.unit!=='percent',max=mean?Number(plot.unit.slice(4)):100,min=mean?1:0;
  const rows=mean?[...plot.rows].sort((a,b)=>b.value-a.value):plot.rows;
  return `<figure class="answer-figure" aria-label="${esc(plot.heading||'Відповіді на питання '+id)}">
   ${plot.heading?`<figcaption class="answer-heading">${esc(plot.heading)}</figcaption>`:''}
   <p class="small muted">${mean?`Середній бал · шкала ${min}–${max}`:'Частка опитаних, %'}</p>
   <div class="answer-scale" aria-hidden="true"><span>${min}${mean?'':'%'}</span><span>${max}${mean?'':'%'}</span></div>
   <div class="answer-bars" role="list">${rows.map(r=>{
    const width=(r.value-min)/(max-min)*100;
    return `<div class="answer-bar-row" role="listitem"><div class="answer-label"><span>${esc(r.label)}</span><strong>${valueText(plot,r.value)}</strong></div><div class="answer-track${mean?' mean-track':''}" aria-hidden="true">${mean?`<i class="mean-point" style="left:${width}%"></i>`:`<i class="answer-fill" style="width:${width}%"></i>`}</div></div>`;
   }).join('')}</div><p class="small muted answer-caption">${esc(plot.caption)}</p>
   <p class="answer-credit"><strong>Графік: Valentyn Hatsko, TG: @gorbach_squad.</strong><br>Джерело: ${esc(poll.pollster)} · ${esc(poll.period)} · <a href="${esc(plot.source_url)}" target="_blank" rel="noopener">${esc(plot.location)} ↗</a><br>Дані, код і метод: github.com/velgaks/peace-agreement-polls</p>
  </figure>`;
 }).join('');
 return `<details class="detail question-chart" open><summary>Графік відповідей${entry.plots.length>1?' · '+entry.plots.length+' панелей':''}</summary><div class="detail-body">${entry.note?`<p class="small muted">${esc(entry.note)}</p>`:''}<p class="small muted">База та обмеження — над графіком і в примітках нижче.</p>${plots}<div class="chart-actions"><button data-question-csv="${esc(id)}">Дані цього питання CSV ↓</button>${entry.series.map(s=>`<a class="button" href="#trends?series=${encodeURIComponent(s)}">Динаміка ↗</a>`).join('')}</div></div></details>`;
}
export function questionChartRows(id,entry,wording,poll,base){
 return entry.plots.flatMap(plot=>plot.rows.map(row=>({question_id:id,poll:poll.id,period:poll.period,base,question_verbatim:wording.question,prompt_verbatim:wording.prompt,prompt_items_verbatim:JSON.stringify(wording.prompt_items||[]),experiment_dimensions_verbatim:JSON.stringify(wording.experiment_dimensions||[]),chart_heading:plot.heading,answer:row.label,value:row.value,unit:plot.unit,wording_basis:wording.basis,note:plot.caption,source_url:plot.source_url,location:plot.location})));
}
