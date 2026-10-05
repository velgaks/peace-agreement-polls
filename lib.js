export const unique = xs => [...new Set(xs)];
export const esc = s => String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const pct = n => new Intl.NumberFormat('uk-UA',{maximumFractionDigits:1}).format(n*100)+'%';
export function timeValue(key){
  const parts=key.split('-').map(Number);
  return Date.UTC(parts[0],parts.length>1?parts[1]-1:6,parts[2]||15);
}
export function waves(rows){return unique(rows.map(r=>r.sort+'|'+r.poll)).map(key=>{const rs=rows.filter(r=>r.sort+'|'+r.poll===key);return {key,sort:rs[0].sort,poll:rs[0].poll,rows:rs,time:timeValue(rs[0].sort)}}).sort((a,b)=>a.time-b.time||a.key.localeCompare(b.key));}
// A missing answer must break the path. It is never imputed as zero.
export function segments(ws,answer){
  const out=[];let current=[];
  for(let i=0;i<ws.length;i++){
    const row=ws[i].rows.find(r=>r.answer===answer);
    if(row)current.push({...row,time:ws[i].time});else{if(current.length)out.push(current);current=[];}
  }
  if(current.length)out.push(current);return out;
}
export function csv(rows){
  if(!rows.length)return '';
  const keys=unique(rows.flatMap(Object.keys));
  const cell=v=>'"'+(v!==null&&typeof v==='object'?JSON.stringify(v):String(v??'')).replace(/^[=+@]/,"'$&").replaceAll('"','""')+'"';
  return '\ufeff'+[keys,...rows.map(r=>keys.map(k=>r[k]))].map(r=>r.map(cell).join(',')).join('\r\n');
}
export const mainSource = poll => poll.priority.startsWith('Основне');
