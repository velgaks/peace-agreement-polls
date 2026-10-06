import {esc,pct} from './lib.js';
import {answerText,basisLabel} from './wording.js?v=packages-1';
import {scenarioHTML} from './question-content.js';

export function packageRows(packages,data,index){
 const questions=new Map(data.questions.map(q=>[q.id,q])),polls=new Map(data.polls.map(p=>[p.id,p]));
 return packages.records.map(r=>{
  const q=questions.get(r.question_id),w=index.byQuestion.get(q.id),p=polls.get(q.poll);
  return {...r,q,w,p,answers:r.mappings.map(m=>answerText({...w,mapping:{answer:m}},'answer'))};
 }).sort((a,b)=>b.p.end.localeCompare(a.p.end)||a.q.id.localeCompare(b.q.id));
}
const colors=r=>r.question_id==='Q142'?['#2a78d6','#eb6834','#898781']:r.question_id==='Q064'?['#2a78d6','#eb6834','#52514e','#898781']:['#2a78d6','#86b6ef','#eb6834','#898781','#52514e'];
function bars(r){
 const palette=colors(r),h=36+r.values.length*33;
 let svg=`<svg class="package-bars" viewBox="0 0 420 ${h}" role="img" aria-label="${esc(r.answers.map((a,i)=>a+': '+pct(r.values[i]/100)).join('; '))}"><g font-family="Source Sans 3, sans-serif" font-size="12" fill="#52514e">`;
 for(const v of [0,25,50,75,100])svg+=`<line x1="${12+v*3.6}" x2="${12+v*3.6}" y1="23" y2="${h-10}" stroke="#e1e0d9" stroke-width=".7"/><text x="${12+v*3.6}" y="14" text-anchor="${v===0?'start':'middle'}">${v}%</text>`;
 r.values.forEach((v,i)=>{const y=31+i*33;svg+=`<rect x="12" y="${y}" width="${v*3.6}" height="15" fill="${palette[i]}"><title>${esc(r.answers[i])}: ${pct(v/100)}</title></rect><text x="${18+v*3.6}" y="${y+13}" fill="#0b0b0b" font-size="14">${pct(v/100)}</text>`;});
 return svg+'</g></svg>';
}
export function packagesHTML(rows){
 const groups=[...new Set(rows.map(r=>r.p.id))];
 return groups.map(id=>{
  const group=rows.filter(r=>r.p.id===id),first=group[0];
  return `<article class="package-wave"><div class="chart-meta"><span>КМІС · ${esc(first.p.period)}</span><a href="#catalog?poll=${id}">Паспорт опитування ↗</a></div>
   ${group.map(r=>{
    const w=r.w,palette=colors(r);
    // Context that defines the scenario must remain visible, even with its instruction collapsed.
    const context=w.question.startsWith('Уявіть,')?`<p>${esc(w.question)}</p>`:'';
    const conditions=w.prompt?context+scenarioHTML(w):`<p>${esc(w.question)}</p>`;
    return `<section class="package-row" id="package-${esc(r.q.id)}" aria-label="${esc(r.q.scenario)}">
     <div class="package-conditions"><h3>${esc(r.q.scenario)}</h3><div class="package-verbatim">${conditions}</div>
      <details class="detail"><summary>Питання, повна шкала та примітки</summary><div class="detail-body"><p>${esc(w.question)}</p><ol>${w.options.map(o=>`<li>${esc(o)}</li>`).join('')}</ol><p class="small muted">${esc(basisLabel(w))}. ${esc(w.note)} ${esc(r.note)}</p><p class="small muted">База: ${esc(r.q.base)}. ${esc(first.p.date_note)}</p><p><a href="${esc(w.source_url)}" target="_blank" rel="noopener">Анкета ↗</a> · <a href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(r.location)} ↗</a>${r.image_url?` · <a href="${esc(r.image_url)}" target="_blank" rel="noopener">Оригінальний графік ↗</a>`:''}</p></div></details>
      <div class="record-links"><a href="${esc(r.source_url)}" target="_blank" rel="noopener">Джерело: ${esc(r.location)} ↗</a>${r.series||w.series==='KIIS_DONBAS_GUARANTEES_2026'?`<a href="#trends?series=${esc(r.series||w.series)}">Динаміка цього пакета ↗</a>`:''}</div>
     </div><figure class="package-distribution"><figcaption class="small muted">Частка опитаних · ${esc(r.p.period)}</figcaption><div class="package-legend">${r.answers.map((a,i)=>`<span><i style="background:${palette[i]}"></i>${esc(a)}</span>`).join('')}</div>${bars(r)}${r.reported_accept!==null&&r.reported_accept!==undefined?`<p class="small muted">Прийняття загалом у тексті КМІС: ${r.reported_accept}%. Сума округлених градацій на графіку: ${r.values[0]+r.values[1]}%.</p>`:''}</figure>
    </section>`;
   }).join('')}
   <div class="chart-credit">Пакети оцінювали цілком; умови та шкали між хвилями можуть відрізнятися.<br><strong>Графік: Valentyn Hatsko, TG: @gorbach_squad.</strong> Джерело: КМІС; зібрано у жовтні 2026.<br>Дані, код і метод: github.com/velgaks/peace-agreement-polls</div></article>`;
 }).join('')||'<p class="empty">За цими умовами нічого не знайдено.</p>';
}
export function packageCSVRows(rows){
 return rows.flatMap(r=>r.values.map((v,i)=>({question_id:r.q.id,poll:r.p.id,period:r.p.period,question_verbatim:r.w.question,conditions_verbatim:r.w.prompt,options_verbatim:JSON.stringify(r.w.options),answer:r.answers[i],value:v,unit:'percent',reported_accept:r.reported_accept,base:r.q.base,source_url:r.source_url,location:r.location,note:r.note})));
}
