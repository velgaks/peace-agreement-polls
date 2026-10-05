// Numerical series use stable keys; display text always comes from source wording.
export const wordingKey=(series,poll)=>series+'|'+poll;
export function indexWording(items){
 const byWave=new Map(),byQuestion=new Map();
 for(const item of items){
  for(const poll of item.polls){const key=wordingKey(item.series,poll);if(byWave.has(key))throw new Error('Duplicate wording: '+key);byWave.set(key,item);}
  for(const id of item.question_ids||[]){if(byQuestion.has(id))throw new Error('Duplicate question wording: '+id);byQuestion.set(id,item);}
 }
 return {byWave,byQuestion};
}
export function answerText(item,key){
 const map=item?.mapping[key];
 if(!map)throw new Error('Missing source wording: '+key);
 if(map.kind==='reported')return map.label+' (категорія графіка видавця)';
 const texts=map.indices.map(i=>{if(!item.options[i])throw new Error('Missing option');return item.options[i];});
 return map.kind==='aggregate'?'Сума відповідей: '+texts.map(t=>'«'+t+'»').join(' + '):texts[0];
}
export const questionText=item=>[item.question,item.prompt].filter(Boolean).join('\n\n');
export const basisLabel=item=>({questionnaire:'Текст анкети',report:'Текст зі звіту',retrospective:'Текст із ретроспективного графіка / таблиці',reference:'Текст іншої хвилі; анкету цього заміру не підтверджено','publication-language':'Англомовна публікація; українську анкету не підтверджено'}[item.basis]);
