import {esc} from './lib.js';
import {basisLabel} from './wording.js';

export function scenarioHTML(item){
 if(item.prompt_items?.length)return `<ul class="scenario-items">${item.prompt_items.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>`;
 return item.prompt?`<p class="verbatim">${esc(item.prompt)}</p>`:'';
}

export function questionContentHTML(record,item){
 const heading=`<h3>${esc(record.scenario)}</h3>`;
 if(!item?.question)return heading+`<p class="small muted">${item?esc(basisLabel(item)):'Дослівне формулювання ще не звірено.'} · Заголовок — тематичний опис, не цитата.</p>`;
 return `${heading}<div class="question-text"><p class="small muted">${esc(basisLabel(item))} · ${esc(record.id)}</p><p class="verbatim">${esc(item.question)}</p>${item.prompt?`<div class="question-scenario"><p class="small muted">Сценарій / твердження</p>${scenarioHTML(item)}</div>`:''}</div>`;
}

export function experimentHTML(item){
 if(!item?.experiment_dimensions?.length)return '';
 return `<div class="experiment-dimensions"><p class="small muted">Параметри експерименту — дослівно з анкети. З кожного виміру випадково обирали один рівень.</p>${item.experiment_dimensions.map(d=>`<div class="experiment-dimension"><h4>${esc(d.name)}</h4><ol>${d.levels.map(level=>`<li>${esc(level)}</li>`).join('')}</ol></div>`).join('')}</div>`;
}
