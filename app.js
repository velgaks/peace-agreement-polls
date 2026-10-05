import {unique,esc,pct,timeValue,waves,segments,csv,mainSource} from './lib.js';
import {SERIES} from './series.js';
import {indexWording,wordingKey,answerText,questionText,basisLabel} from './wording.js';
const $=id=>document.getElementById(id);
const COLORS=['#2a78d6','#eb6834','#52514e','#0d366b','#898781','#86b6ef'];
const DASH=['','7 3','2 3','10 3 2 3','4 4','1 3'];
const TEXT={uk:{credit:'Графік: Valentyn Hatsko, TG: @gorbach_squad.',repo:'Дані, код і метод: github.com/velgaks/peace-agreement-polls',retrieved:'джерела зібрано у жовтні 2026'}};
const T=TEXT.uk;
let data,source,polls,wording,wordingIndex,selected=SERIES[0].id,currentRows=[],catalogRows=[];
function sourceLink(id,label='Джерело ↗'){
 const url=source[id]?.url;return url&&/^https?:\/\//.test(url)?`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)}</a>`:'';
}
const field=r=>{const p=polls[r.poll];return p?.start&&p?.end?p.period:r.period;};
function download(name,body,type='text/csv;charset=utf-8'){
 const status=$('status');const previous=status.querySelector('a[data-download]');if(previous)URL.revokeObjectURL(previous.href);
 const url=URL.createObjectURL(new Blob([body],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.dataset.download='';a.textContent='Завантажити '+name;
 status.replaceChildren(document.createTextNode('Файл готовий. Якщо завантаження не почалося: '),a);a.click();
}
const withURLs=rows=>rows.map(r=>({...r,source_url:source[r.source]?.url||''}));
const option=(v,t)=>`<option value="${esc(v)}">${esc(t)}</option>`;
const wordingFor=(series,poll)=>wordingIndex.byWave.get(wordingKey(series,poll));
const wordingURL=(item,label='Формулювання ↗')=>`<a href="${esc(item.source_url)}" target="_blank" rel="noopener">${esc(label)}</a>`;
 function wordingHTML(item,includeQuestion=true){
  if(!item)return '<p class="small muted">Дослівне питання та повний перелік опцій ще не звірено з першоджерелом.</p>';
  const list=values=>`<ul>${values.map(v=>`<li>${esc(v)}</li>`).join('')}</ul>`;
  const scale=(values,label='Варіанти відповіді')=>values.length?`<details class="wording-options"><summary>${label} (${values.length})</summary>${list(values)}</details>`:'';
  return `${includeQuestion&&item.question?`<p class="verbatim">${esc(questionText(item))}</p>`:''}
   ${item.statements?`<p class="small">Твердження / сценарії, кожен оцінюється окремо:</p>${list(item.statements)}`:''}
   ${scale(item.options)}${item.instructions?`<p class="small verbatim">${esc(item.instructions)}</p>`:''}
   ${(item.followups||[]).map(f=>`<p class="verbatim">${esc(f.question)}</p>${list(f.statements||[])}${scale(f.options)}`).join('')}
   ${item.partial_options?scale(item.partial_options,'Лише опції, цитовані у публікації; перелік неповний'):''}
   ${item.source_excerpt?`<p class="small">Опублікований фрагмент, не повне питання:</p><p class="verbatim">${esc(item.source_excerpt)}</p>`:''}
   <p class="small muted">${esc(basisLabel(item))}. ${esc(item.note)}</p>`;
 }
const csvWording=rows=>withURLs(rows).map(r=>{const w=wordingFor(r.series,r.poll);return {...r,answer_key:r.answer,answer:answerText(w,r.answer),question_verbatim:w.question,prompt_verbatim:w.prompt,options_verbatim:JSON.stringify(w.options),interviewer_instructions:w.instructions,wording_basis:w.basis,wording_note:w.note,wording_source_url:w.source_url,question_source_url:w.question_source_url||w.source_url};});
function renderSeriesList(){
 const term=$('series-search').value.toLocaleLowerCase('uk');
 const list=SERIES.filter(s=>(s.name+' '+s.org+' '+s.question).toLocaleLowerCase('uk').includes(term));
 $('series-list').innerHTML=list.map(s=>`<button class="series-option" data-series="${s.id}" aria-pressed="${s.id===selected}">${esc(s.name)}<span>${esc(s.org)}</span></button>`).join('')||'<p class="empty">Нічого не знайдено.</p>';
 $('series-list').querySelectorAll('button').forEach(b=>b.onclick=()=>{selected=b.dataset.series;history.replaceState(null,'','#trends?series='+selected);renderTrend();renderSeriesList();});
}
function chartSVG(meta,rs){
 const ws=waves(rs),answers=meta.order||unique(rs.map(r=>r.answer));
 const width=840,height=425,left=45,right=770,top=36,bottom=365;
 const min=ws[0].time,max=ws.at(-1).time;
 const x=t=>left+(t-min)/(max-min||1)*(right-left),y=v=>bottom-v*(bottom-top);
 let svg=`<svg id="trend-chart" class="chart-svg" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="svg-title svg-desc"><title id="svg-title">${esc(meta.title)}</title><desc id="svg-desc">${esc(questionText(wordingFor(meta.id,ws.at(-1).poll)))} ${esc(meta.note)} Точні значення доступні на точках графіка та у CSV.</desc><g font-family="Source Sans 3, sans-serif" font-size="12" fill="#52514e">`;
 for(let v=0;v<=1.001;v+=.25){svg+=`<line x1="${left}" x2="${right}" y1="${y(v)}" y2="${y(v)}" stroke="#e1e0d9" stroke-width=".7"/><text x="${left-10}" y="${y(v)+4}" text-anchor="end">${Math.round(v*100)}%</text>`;}
 const span=max-min;
 const fmt=new Intl.DateTimeFormat('uk-UA',{month:'short',year:'numeric',timeZone:'UTC'});
 const ticks=span>864e5*730?unique(ws.map(w=>new Date(w.time).getUTCFullYear())).map(yr=>({t:Math.max(min,Math.min(max,Date.UTC(yr,0,1))),label:String(yr)})):ws.map(w=>({t:w.time,label:fmt.format(w.time)}));
 // Two January waves retain separate points; axis labels need not repeat the month.
 let lastX=-Infinity;
 ticks.forEach((t,i)=>{const xx=x(t.t);if(xx-lastX<88&&i<ticks.length-1)return;if(xx-lastX<55)return;lastX=xx;svg+=`<text x="${xx}" y="${bottom+28}" text-anchor="${i===0?'start':i===ticks.length-1?'end':'middle'}">${esc(t.label)}</text>`;});
 const endpoints=[];
 answers.forEach((answer,i)=>{
  const color=COLORS[i%COLORS.length];const dash=DASH[i%DASH.length];
  segments(ws,answer).forEach(seg=>{
   if(seg.length>1)svg+=`<polyline points="${seg.map(r=>`${x(r.time)},${y(r.pct)}`).join(' ')}" fill="none" stroke="${color}" stroke-width="2.2" stroke-dasharray="${dash}"/>`;
   seg.forEach(r=>{const idx=rs.indexOf(rs.find(a=>a.poll===r.poll&&a.sort===r.sort&&a.answer===answer));const label=`${field(r)} · ${answerText(wordingFor(meta.id,r.poll),answer)}: ${pct(r.pct)}`;svg+=`<circle cx="${x(r.time)}" cy="${y(r.pct)}" r="4" fill="${color}" stroke="#fcfcfb" stroke-width="1.3" tabindex="0" data-point="${idx}" aria-label="${esc(label)}"><title>${esc(label)}</title></circle>`;});
  });
  const end=ws.at(-1).rows.find(r=>r.answer===answer);if(end)endpoints.push({value:end.pct,color,yy:y(end.pct)});
 });
 endpoints.sort((a,b)=>a.yy-b.yy);let last=-Infinity;
 endpoints.forEach(e=>{e.labelY=Math.max(e.yy,last+20);last=e.labelY;});
 const overflow=Math.max(0,(endpoints.at(-1)?.labelY||0)-bottom);
 endpoints.forEach(e=>{const yy=e.labelY-overflow;svg+=`<line x1="${right+7}" x2="${right+18}" y1="${e.yy}" y2="${yy}" stroke="${e.color}"/><text class="end-value" x="${right+22}" y="${yy+5}" fill="#0b0b0b">${pct(e.value)}</text>`;});
 return svg+'</g></svg>';
}
function renderTrend(){
 const meta=SERIES.find(s=>s.id===selected)||SERIES[0];selected=meta.id;
 currentRows=data.dynamics.filter(r=>r.series===selected).sort((a,b)=>timeValue(a.sort)-timeValue(b.sort));
 const ws=waves(currentRows),answers=meta.order||unique(currentRows.map(r=>r.answer));
 const latest=wordingFor(meta.id,ws.at(-1).poll);
 const legendAnswers=answers.map(a=>answerText(latest,a));
 const passport=ws.map(w=>{const exact=wordingFor(meta.id,w.poll);const refs=[...new Map(w.rows.map(r=>[r.source+'|'+r.location,r])).values()];return `<tr><td>${esc(field(w.rows[0]))}</td><td>${wordingHTML(exact)}</td><td>${wordingURL(exact)}<br><span class="small muted">${esc(exact.location)}</span>${exact.question_source_url?`<br><a href="${esc(exact.question_source_url)}" target="_blank" rel="noopener">Питання в графіку ↗</a>`:''}<br>${refs.map(r=>sourceLink(r.source,'Числа: '+(r.location||'джерело'))).join('<br>')}</td></tr>`;}).join('');
 $('chart-panel').innerHTML=`<div class="chart-meta"><span>${esc(meta.org)}</span><span>Заміри: ${ws.length} · ${ws[0].sort.slice(0,4)}–${ws.at(-1).sort.slice(0,4)}</span></div><h2 class="chart-title">${esc(meta.title)}</h2><p class="chart-subtitle verbatim">${esc(questionText(latest))}</p><p class="wording-basis small muted">${esc(basisLabel(latest))} · ${esc(field(ws.at(-1).rows[0]))} · ${wordingURL(latest,'Джерело формулювання ↗')}</p><div class="legend">${legendAnswers.map((a,i)=>`<span class="legend-item"><i class="legend-mark" style="border-color:${COLORS[i]};border-top-style:${i?'dashed':'solid'}"></i><span>${esc(a)}</span></span>`).join('')}</div><div class="chart-wrap">${chartSVG(meta,currentRows)}</div><div id="point-readout" class="point-readout" aria-live="polite">Натисніть точку або перейдіть до неї клавішею Tab, щоб побачити точне значення й опцію цієї хвилі.</div><div class="chart-credit">${esc(meta.caption)}<br><strong>${T.credit}</strong> Джерело: ${esc(meta.org)}; ${T.retrieved}.<br>${T.repo}</div><div class="chart-actions"><button id="trend-csv">Дані CSV ↓</button><button id="trend-svg">Графік SVG ↓</button><button id="share-series">Копіювати посилання ↗</button></div><details class="detail" open><summary>Примітки: формулювання та методика</summary><div class="detail-body"><p>${esc(meta.note)}</p><p>Над графіком — дослівне формулювання з джерела останнього заміру. Повний перелік опцій та версії попередніх хвиль — у паспорті. Суми відповідей позначені окремо.</p><p>${esc(latest.note)}</p></div></details><details class="detail"><summary>Паспорт графіка · заміри: ${ws.length}</summary><div class="table-wrap"><table class="chart-passport"><thead><tr><th>Дата</th><th>Питання та опції — дослівно з джерела</th><th>Джерело</th></tr></thead><tbody>${passport}</tbody></table></div></details>`;
 $('chart-panel').querySelectorAll('[data-point]').forEach(p=>{const show=()=>{const r=currentRows[Number(p.dataset.point)];$('point-readout').innerHTML=`<strong>${esc(field(r))}</strong> · ${esc(answerText(wordingFor(meta.id,r.poll),r.answer))}: <strong>${pct(r.pct)}</strong> · ${sourceLink(r.source,r.location)}`;};p.onmouseenter=show;p.onfocus=show;p.onclick=show;});
 $('trend-csv').onclick=()=>download(meta.id+'.csv',csv(csvWording(currentRows)));
 $('trend-svg').onclick=()=>exportSVG(meta,legendAnswers,latest);
 $('share-series').onclick=async()=>{try{await navigator.clipboard.writeText(location.href);$('share-series').textContent='Посилання скопійовано';}catch{$('point-readout').textContent=location.href;}};
}
function lines(text,max=84){const result=[];let line='';for(const word of text.split(' ')){if(line.length+word.length>max){result.push(line);line='';}line+=(line?' ':'')+word;}if(line)result.push(line);return result;}
function exportSVG(meta,answers,exact){
 let y=32,header='';for(const line of lines(meta.title,65)){header+=`<text x="25" y="${y}" font-size="23" font-weight="600">${esc(line)}</text>`;y+=30;}y+=8;
 for(const line of lines(questionText(exact),95)){header+=`<text x="25" y="${y}" font-size="13">${esc(line)}</text>`;y+=19;}y+=12;
 answers.forEach((a,i)=>{for(const [j,line] of lines(a,90).entries()){header+=`${j===0?`<line x1="25" x2="45" y1="${y-5}" y2="${y-5}" stroke="${COLORS[i]}" stroke-width="3" stroke-dasharray="${DASH[i]}"/>`:''}<text x="53" y="${y}" font-size="13">${esc(line)}</text>`;y+=19;}});
 const chart=$('trend-chart').outerHTML.replace('class="chart-svg"','').replace('<svg ','<svg x="0" y="'+(y+5)+'" width="840" height="425" ');
 y+=455;let caption='';for(const l of ['Примітка. '+meta.note+' '+exact.note,basisLabel(exact)+'. Формулювання: '+exact.source_url,T.credit+' Джерело: '+meta.org+'; жовтень 2026.',T.repo]){for(const line of lines(l,110)){caption+=`<text x="25" y="${y}" font-size="11">${esc(line)}</text>`;y+=16;}}
 const body=`<svg xmlns="http://www.w3.org/2000/svg" width="840" height="${y+15}" viewBox="0 0 840 ${y+15}"><rect width="100%" height="100%" fill="#fcfcfb"/><g fill="#0b0b0b" font-family="Source Sans 3, sans-serif">${header}${chart}${caption}</g></svg>`;
 download(meta.id+'.svg',body,'image/svg+xml;charset=utf-8');
}
function renderQuestions(){
 const term=$('question-search').value.toLocaleLowerCase('uk'),dim=$('dimension-filter').value;
 const rows=data.questions.filter(q=>(!dim||q.dimension===dim)&&($('question-priority').value==='all'||mainSource(polls[q.poll]))&&(/^p\d{2,3}$/.test(term)?q.poll.toLowerCase()===term:JSON.stringify({...q,wording:wordingIndex.byQuestion.get(q.id),pollster:polls[q.poll].pollster,commissioner:polls[q.poll].commissioner}).toLocaleLowerCase('uk').includes(term)));
 $('question-count').textContent=`Показано ${rows.length} із ${data.questions.length} питань.`;
 $('question-list').innerHTML=rows.map(q=>{const p=polls[q.poll],exact=wordingIndex.byQuestion.get(q.id);const values=exact?data.dynamics.filter(r=>r.series===exact.series&&r.poll===q.poll):[];const result=values.length?values.map(r=>pct(r.pct)+' — '+answerText(exact,r.answer)).join('; '):q.result;return `<article class="record"><div class="record-side"><strong>${esc(p.pollster)}</strong><span>${esc(p.period)}</span><span class="badge">${esc(q.dimension)}</span></div><div><h3>${esc(exact?.question?questionText(exact):q.scenario)}</h3>${exact?`<p class="small muted">${esc(basisLabel(exact))}${exact.basis==='unavailable'?' · Заголовок — тематичний опис, не цитата.':''}</p>`:'<p class="small muted">Тематичний опис; дослівне формулювання ще не звірено.</p>'}<p class="result">${values.length?'':'<span class="small muted">Результат (переказ): </span>'}${esc(result)}</p><p class="small muted">База: ${esc(q.base)}</p><details class="detail"><summary>Опції, примітки та джерело</summary><div class="detail-body">${wordingHTML(exact,false)}<p>${esc(q.limit)}</p><p>${exact?wordingURL(exact)+' · ':''}${sourceLink(q.source,'Оригінал: '+q.location)}</p></div></details><div class="record-links"><a href="#catalog?poll=${q.poll}">Паспорт ${q.poll}</a>${sourceLink(q.source,q.location+' ↗')}</div></div></article>`;}).join('')||'<p class="empty">За цими умовами нічого не знайдено.</p>';
}
function renderCatalog(){
 const term=$('catalog-search').value.toLocaleLowerCase('uk'),year=$('year-filter').value,priority=$('priority-filter').value;
 catalogRows=data.polls.filter(p=>(!year||(p.period+' '+p.start+' '+p.end).includes(year))&&(priority==='all'||(priority==='main'?mainSource(p):!mainSource(p)))&&(/^p\d{2,3}$/.test(term)?p.id.toLowerCase()===term:JSON.stringify(p).toLocaleLowerCase('uk').includes(term)));
 $('catalog-count').textContent=`Показано ${catalogRows.length} із ${data.polls.length} записів. Це не кількість незалежних вибірок.`;
 $('catalog-list').innerHTML=catalogRows.map(p=>`<article class="record"><div class="record-side"><strong>${esc(p.id)} · ${esc(p.pollster)}</strong><span>${esc(p.period)}</span><span class="badge">${esc(p.priority)}</span></div><div><h3>${esc(p.title)}</h3><p class="small muted">${esc(p.commissioner)} · n = ${esc(p.n||'не встановлено')} · ${esc(p.method||'не встановлено')}</p><details class="detail"><summary>Паспорт і межі інтерпретації</summary><dl><dt>Публікація</dt><dd>${esc(p.published||'Дату не встановлено')}</dd><dt>Охоплення</dt><dd>${esc(p.population||'Не встановлено')}</dd><dt>Обмеження</dt><dd>${esc(p.limits)}</dd><dt>Перевірка</dt><dd>${esc(p.check)}</dd></dl></details><div class="record-links">${sourceLink(p.source,'Публікація ↗')}${p.report?sourceLink(p.report,'Повний звіт ↗'):''}<a href="#conditions?poll=${p.id}">Питання цієї хвилі</a></div></div></article>`).join('')||'<p class="empty">За цими умовами нічого не знайдено.</p>';
}
function route(){
 const [raw,query='']=location.hash.slice(1).split('?'),view=['trends','conditions','catalog','methods'].includes(raw)?raw:'trends';const params=new URLSearchParams(query);
 document.querySelectorAll('section[id^="view-"]').forEach(s=>s.hidden=s.id!=='view-'+view);
 document.querySelectorAll('.nav a').forEach(a=>{if(a.dataset.view===view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 if(view==='trends'){if(SERIES.some(s=>s.id===params.get('series')))selected=params.get('series');renderSeriesList();renderTrend();}
 if(view==='conditions'){if(params.has('poll')){$('question-search').value=params.get('poll');$('question-priority').value='all';$('dimension-filter').value='';}renderQuestions();}
 if(view==='catalog'){if(params.has('poll')){$('catalog-search').value=params.get('poll');$('year-filter').value='';$('priority-filter').value='all';}renderCatalog();}
}
async function init(){
 try{
  const wr=await fetch('data/wording.json?v=catalogue-2');if(!wr.ok)throw new Error('Wording HTTP '+wr.status);wording=await wr.json();wordingIndex=indexWording(wording.items);
  const response=await fetch('data/research.json?v=catalogue-2');if(!response.ok)throw new Error('HTTP '+response.status);data=await response.json();source=Object.fromEntries(data.sources.map(s=>[s.id,s]));polls=Object.fromEntries(data.polls.map(p=>[p.id,p]));
  $('stats').innerHTML=`<div><strong>${SERIES.length}</strong><span>часових серій</span></div><div><strong>${data.polls.length}</strong><span>записів у каталозі</span></div><div><strong>${data.questions.length}</strong><span>питань і сценаріїв</span></div>`;
  $('dimension-filter').innerHTML=option('','Усі виміри')+unique(data.questions.map(q=>q.dimension)).sort((a,b)=>a.localeCompare(b,'uk')).map(d=>option(d,d)).join('');
  $('year-filter').innerHTML=option('','Усі роки')+['2026','2025','2024','2023','2022'].map(y=>option(y,y)).join('');
  $('coverage-list').innerHTML=data.coverage.map(r=>`<details class="detail"><summary>${esc(r[0])} · ${esc(r[1])}</summary><div class="detail-body"><p>${esc(r[2])}</p><p>${esc(r[3])}</p><p>${esc(r[4])}</p></div></details>`).join('');
  route();$('status').textContent='';
  $('series-search').oninput=renderSeriesList;
  ['question-search','dimension-filter','question-priority'].forEach(id=>$(id).addEventListener(id.includes('search')?'input':'change',renderQuestions));
  ['catalog-search','year-filter','priority-filter'].forEach(id=>$(id).addEventListener(id.includes('search')?'input':'change',renderCatalog));
  $('catalog-csv').onclick=()=>download('poll-catalog.csv',csv(withURLs(catalogRows)));
  window.addEventListener('hashchange',route);
 }catch(error){$('status').innerHTML='Не вдалося завантажити дані. Спробуйте оновити сторінку або <a href="data/dynamics.csv">завантажте CSV</a>.';console.error(error);}
}
init();
