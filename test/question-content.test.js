import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {questionContentHTML,scenarioHTML,experimentHTML} from '../question-content.js';
const items=JSON.parse(fs.readFileSync(new URL('../data/wording.json',import.meta.url),'utf8')).items;
const byId=id=>items.find(w=>w.question_ids.includes(id));

test('Q05 contains only the questionnaire scenario, never article text or response tables',()=>{
 const w=byId('Q05');
 assert.equal(w.prompt,'Вогонь припиняється за нинішньою лінією фронту. Росія зберігає контроль над усіма окупованими територіями без міжнародного визнання. Водночас Україна для гарантування безпеки у великих обсягах отримує гроші та всю зброю: ракети, ППО, літаки, танки тощо.');
 for(const item of items)assert.doesNotMatch(item.question+' '+item.prompt,/У таблиці нижче|% у стовпчику|коментарі до результатів|Додаток 1\./,item.id);
 const html=questionContentHTML({id:'Q05',scenario:'Перемир’я'},w);
 assert.equal(html.match(/<h3>(.*?)<\/h3>/s)[1],'Перемир’я');
 assert(html.includes(w.question));assert(html.includes(w.prompt));
});

test('Q25 retains all five dimensions and 13 exact levels separately from the question',()=>{
 const w=byId('Q25');assert.equal(w.prompt,'');assert.deepEqual(w.experiment_dimensions.map(d=>d.levels.length),[4,2,3,2,2]);
 const html=experimentHTML(w);assert.equal((html.match(/<li>/g)||[]).length,13);
 assert(html.includes('Надалі Україна може ухвалювати будь-які рішення без контролю з боку Росії'));
 assert(!questionContentHTML({id:'Q25',scenario:'Параметри угоди'},w).includes('Назва виміру'));
});

test('Source bullet boundaries preserve every word of the original scenario',()=>{
 const lists=items.filter(w=>w.prompt_items);assert.equal(lists.length,13);
 for(const item of lists){assert.equal(item.prompt_items.join(' '),item.prompt);assert.equal((scenarioHTML(item).match(/<li>/g)||[]).length,item.prompt_items.length);}
 const html=experimentHTML({experiment_dimensions:[{name:'<name>',levels:['a & b','<script>']}]});
 assert(html.includes('&lt;name&gt;'));assert(html.includes('a &amp; b'));assert(!html.includes('<script>'));
});
