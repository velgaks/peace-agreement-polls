import {esc,pct} from './lib.js';
import {answerText,basisLabel} from './wording.js?v=packages-1';
import {scenarioHTML} from './question-content.js';

export function packageRows(packages,data,index){
 const questions=new Map(data.questions.map(q=>[q.id,q])),polls=new Map(data.polls.map(p=>[p.id,p]));
 return packages.records.map(r=>{
  const q=questions.get(r.question_id),w=index.byQuestion.get(q.id),p=polls.get(q.poll);
  return {...r,q,w,p,answers:r.mappings.map(m=>answerText({...w,mapping:{answer:m}},'answer'))};
 }).sort((a,b)=>b.p.end.localeCompare(a.p.end)||a.q.id.localeCompare(b.q.id)).map((r,i)=>({...r,number:i+1}));
}
const SHORT={
 Q042:'Окуповані території за РФ, без НАТО, вступ до ЄС',
 Q043:'Окуповані території за РФ без визнання, НАТО та ЄС',
 Q044:'Повернення Херсонщини й Запоріжжя, НАТО та ЄС',
 Q046:'Скорочення армії, передача територій, відмова від НАТО',
 Q047:'Гарантії Європи без США, визнання Криму США',
 Q048:'Гарантії США і Європи, поступове послаблення санкцій',
 Q049:'Скорочення армії, передача територій, відмова від НАТО',
 Q050:'Гарантії Європи без США, визнання Криму США',
 Q051:'Гарантії США і Європи, поступове послаблення санкцій',
 Q052:'Передача Донбасу, обмеження армії, російська мова',
 Q053:'Заморожування фронту, зброя і гроші, закриття неба',
 Q058:'Заморожування фронту, зброя і гроші, закриття неба',
 Q059:'Передача Донбасу, обмеження армії, російська мова',
 Q060:'Передача Донбасу в обмін на гарантії США і Європи',
 Q061:'Передача Донбасу в обмін на гарантії США і Європи',
 Q02:'Передача Донбасу в обмін на гарантії США і Європи',
 Q062:'Передача Донбасу в обмін на гарантії США і Європи',
 Q063:'Передача Донбасу в обмін на гарантії США і Європи',
 Q04:'Передача Донбасу в обмін на гарантії США і Європи',
 Q03:'Передача Донбасу; США без військ, закриття неба й безкоштовної зброї',
 Q064:'Референдум: ЄС у 2027, компроміси, гарантії, відбудова',
 Q065:'Заморожування фронту без гарантій, грошей і зброї',
 Q066:'Заморожування фронту; європейські війська не воюють',
 Q067:'Заморожування фронту; великі обсяги грошей і зброї',
 Q068:'Заморожування фронту; європейські війська відбивають напад',
 Q05:'Заморожування фронту; великі обсяги грошей і зброї',
 Q142:'Припинення вогню, зміцнення армії, рух до ЄС і НАТО'
};
const BUCKETS={easy:'Легко погоджуються',hard:'Важко, але прийнятно',support:'Підтримують загалом / «Так»',reject:'Відкидають / «Ні»',uncertain:'Важко сказати',refusal:'Відмова',abstain:'Не голосували би'};
export function packageSegments(r){
 let offset=0;
 return r.values.map((value,i)=>{
  const bucket=r.question_id==='Q142'?['support','reject','uncertain'][i]:r.question_id==='Q064'?['support','reject','abstain','uncertain'][i]:['easy','hard','reject','uncertain','refusal'][i];
  const segment={value,label:r.answers[i],bucket,offset};offset+=value;return segment;
 });
}
export const packageAcceptance=r=>r.reported_accept??packageSegments(r).filter(s=>['easy','hard','support'].includes(s.bucket)).reduce((sum,s)=>sum+s.value,0);
const label=r=>SHORT[r.q.id]||r.q.scenario;
function wordingHTML(r){
 const w=r.w;
 return `<details class="detail package-wording" id="package-${esc(r.q.id)}"><summary><span class="package-number">${r.number}.</span> ${esc(label(r))}<span class="package-wording-date">${esc(r.p.period)}</span></summary><div class="detail-body">
  <p class="small muted">${esc(basisLabel(w))}</p><div class="package-verbatim"><p>${esc(w.question)}</p>${scenarioHTML(w)}</div>
  ${w.instructions?`<p class="small verbatim">${esc(w.instructions)}</p>`:''}<h4>Повна шкала — дослівно</h4><ol>${w.options.map(o=>`<li>${esc(o)}</li>`).join('')}</ol>
  <h4>Опубліковані відповіді</h4><dl class="package-exact-values">${r.answers.map((a,i)=>`<dt>${esc(a)}</dt><dd>${pct(r.values[i]/100)}</dd>`).join('')}</dl>
  <details class="detail"><summary>Примітки та методика</summary><div class="detail-body"><p>${esc(w.note)}</p><p>${esc(r.note)}</p><p>База: ${esc(r.q.base)}. ${esc(r.p.date_note)}</p>${r.reported_accept!=null?`<p>Авторський агрегат прийняття: ${r.reported_accept}%; сума округлених градацій: ${packageSegments(r).filter(s=>['easy','hard','support'].includes(s.bucket)).reduce((sum,s)=>sum+s.value,0)}%.</p>`:''}</div></details>
  <div class="record-links"><a href="${esc(w.source_url)}" target="_blank" rel="noopener">Формулювання ↗</a><a href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(r.location)} ↗</a>${r.image_url?`<a href="${esc(r.image_url)}" target="_blank" rel="noopener">Оригінальний графік ↗</a>`:''}<a href="#catalog?poll=${esc(r.p.id)}">Паспорт опитування ↗</a>${r.series||w.series==='KIIS_DONBAS_GUARANTEES_2026'?`<a href="#trends?series=${esc(r.series||w.series)}">Динаміка цього пакета ↗</a>`:''}</div>
 </div></details>`;
}
export function packagesHTML(rows){
 if(!rows.length)return '<p class="empty">За цими умовами нічого не знайдено.</p>';
 const used=new Set(rows.flatMap(r=>packageSegments(r).map(s=>s.bucket)));
 return `<figure class="package-comparison" aria-labelledby="package-comparison-title"><figcaption id="package-comparison-title">Відповіді на різні пакети умов, %</figcaption>
  <div class="package-comparison-legend">${Object.entries(BUCKETS).filter(([key])=>used.has(key)).map(([key,text])=>`<span><i class="package-segment--${key}"></i>${esc(text)}</span>`).join('')}</div>
  <div class="package-comparison-axis" aria-hidden="true"><span>Пакет / дати поля</span><div>${[0,25,50,75,100].map(v=>`<span style="left:${v}%">${v}%</span>`).join('')}</div></div>
  <div class="package-comparison-rows">${rows.map(r=>{
   const segments=packageSegments(r),description=segments.map(s=>s.label+': '+pct(s.value/100)).join('; ');
   return `<div class="package-comparison-row"><button class="package-label" data-package="${esc(r.q.id)}" aria-controls="package-${esc(r.q.id)}"><span><span class="package-number">${r.number}.</span> ${esc(label(r))}</span><small>${esc(r.p.period)}${r.question_id==='Q064'?' · Голосування':r.question_id==='Q142'?' · Підтримка загалом':''}</small></button><button class="package-stacked-bar" data-package="${esc(r.q.id)}" aria-controls="package-${esc(r.q.id)}" aria-label="${esc(label(r)+'. '+r.p.period+'. '+description+'. Відкрити повне формулювання.')}" title="${esc(description)}">${segments.map(s=>`<span class="package-segment package-segment--${s.bucket}" style="left:${s.offset}%;width:${s.value}%" title="${esc(s.label)}: ${pct(s.value/100)}" aria-hidden="true">${s.value>=6?pct(s.value/100):''}</span>`).join('')}</button></div>`;
  }).join('')}</div>
  <div class="chart-credit">Шкали різняться; повні умови й опції — під графіком. Частки не нормалізовані.<br><strong>Графік: Valentyn Hatsko, TG: @gorbach_squad.</strong> Джерело: КМІС; зібрано у жовтні 2026.<br>Дані, код і метод: github.com/velgaks/peace-agreement-polls</div></figure>
  <div class="package-full-wording"><h3>Повні формулювання та шкали</h3><p class="small muted">Натисніть назву або смугу на графіку, щоб відкрити відповідний пакет.</p>${rows.map(wordingHTML).join('')}</div>`;
}
export function packageCSVRows(rows){
 return rows.flatMap(r=>r.values.map((v,i)=>({question_id:r.q.id,poll:r.p.id,period:r.p.period,question_verbatim:r.w.question,conditions_verbatim:r.w.prompt,options_verbatim:JSON.stringify(r.w.options),answer:r.answers[i],value:v,unit:'percent',reported_accept:r.reported_accept,base:r.q.base,source_url:r.source_url,location:r.location,note:r.note})));
}
