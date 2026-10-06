"""Audited chart transcriptions; repeatable import without duplicating observations."""
import json, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
A=Path(sys.argv[1]); register=A/'_work/research-data.json'
d=json.loads(register.read_text('utf8')); w=json.loads((R/'data/wording.json').read_text('utf8'))
byq={q:z for z in w['items'] for q in z['question_ids']}; qs={q['id']:q for q in d['questions']}; ps={p['id']:p for p in d['polls']}
out={'reviewed_on':'2026-10-06','records':[],'series':[]}
common='Відтворено всі категорії оригінального графіка. Округлення збережено; суми можуть відрізнятися від 100%. «Важко сказати» — підпис у публікації; якщо відмови не показані окремо, їхню частку не визначено.'
def add(q,values,report,img,location,note='',indices=None,aggregate=None):
 z=byq[q]; indices=indices or list(range(len(values)))
 maps=[{'kind':'aggregate' if isinstance(i,list) else 'option','indices':i if isinstance(i,list) else [i]} for i in indices]
 if len(values)==4 and len(z['options'])==5 and q!='Q064': maps[-1]={'kind':'reported','label':'Важко сказати'}
 if q=='Q064' or q=='Q142':maps[-1]={'kind':'reported','label':'Важко сказати'}
 out['records'].append(dict(question_id=q,values=values,mappings=maps,source_url=f'https://kiis.com.ua/?lang=ukr&cat=reports&id={report}',image_url='https://kiis.com.ua/'+img if img else '',location=location,note=common+' '+note,reported_accept=aggregate))
add('Q042',[8,30,54,8],1421,'materials/pr/20240723_d/03.JPG','Графік 3')
add('Q043',[10,37,38,15],1421,'materials/pr/20240723_d/03.JPG','Графік 3')
add('Q044',[20,37,33,10],1421,'materials/pr/20240723_d/03.JPG','Графік 3')
for q,v in [('Q046',[2,8,82,8]),('Q047',[4,25,61,11]),('Q048',[12,39,40,10])]:add(q,v,1530,'materials/pr/20250514_s/01.JPG','Графік 1')
discrepancy='У K1543 проза дає 30% неприйняття пакета Європи/України, а графік — 35%; використано 35% із графіка. Травневі 61% і 40% взято з первинного K1530; у прозі K1543 помилково наведено 62% і 35%, але його ретроспективний графік повторює 61% і 40%.'
for q,v in [('Q049',[5,12,76,7]),('Q050',[7,32,49,12]),('Q051',[10,44,35,10])]:add(q,v,1543,'materials/pr/20250807_s/01.JPG','Графік 1',discrepancy)
for q,v in [('Q052',[3,14,75,8]),('Q053',[18,56,15,12])]:add(q,v,1551,'materials/pr/20250915_r/02.JPG','Графік 2')
for q,v in [('Q058',[30,39,16,16]),('Q059',[4,13,74,9])]:add(q,v,1572,'materials/pr/20260102_d/03.JPG','Графік 3')
for q,v in [('Q060',[8,31,54,5,2]),('Q061',[9,31,52,7,1]),('Q02',[7,29,57,6,1]),('Q062',[6,27,62,5,0]),('Q063',[7,29,57,7,1]),('Q04',[5,27,60,7,1])]:
 add(q,v,1626,'','Графік 2; ретроспектива', 'Для липня–серпня авторський агрегат прийняття — 33%, сума округлених градацій — 32%; обидва значення збережено.' if q=='Q04' else '',aggregate=33 if q=='Q04' else None)
add('Q03',[5,20,68,6,1],1589,'materials/pr/20260302_s/03.JPG','Графік 3')
add('Q064',[61,10,21,9],1594,'materials/pr/20260316_s/05.JPG','Графік 5','Серед усіх опитаних. Шкала голосування, а не прийнятності; територіальні компроміси не конкретизовано.')
for q,v,agg in [('Q065',[4,27,61,7],32),('Q066',[7,34,49,10],42),('Q067',[8,45,37,10],53),('Q068',[13,47,33,6],61)]:
 add(q,v,1615,'materials/pr/20260608_s/01.JPG','Графік 1',f'Авторський агрегат прийняття — {agg}%; сума округлених градацій — {v[0]+v[1]}%. Агрегат не є додатковою опцією.',aggregate=agg)
add('Q05',[12,47,31,9,1],1626,'','Графік 3')
add('Q142',[69,22,9],1639,'','Графік 3','Опубліковано лише сумарну підтримку та непідтримку; окремі градації не обчислювали.',indices=[[0,1],[2,3],4])
records={r['question_id']:r for r in out['records']}
for code,title,pair in [
 ('RUSSIA_MAY_2025','Скорочення армії, передача територій і відмова від НАТО',['Q046','Q049']),
 ('USA_MAY_2025','Гарантії Європи без США та визнання Криму США',['Q047','Q050']),
 ('EUROPE_MAY_2025','Гарантії США/Європи та поступове послаблення санкцій',['Q048','Q051']),
 ('RUSSIA_SEP_2025','Донбас, обмеження армії, офіційний статус російської',['Q052','Q059']),
 ('EUROPE_SEP_2025','Заморожування фронту, зброя та закриття неба',['Q053','Q058'])]:
 sid='KIIS_PACKAGE_'+code;z0=byq[pair[0]]
 assert all((byq[q]['question'],byq[q]['prompt'],byq[q]['options'])==(z0['question'],z0['prompt'],z0['options']) for q in pair)
 note='Дослівно однакові питання, пакет і шкала у двох хвилях. Показано всі чотири опубліковані категорії. '+common
 if code.endswith('MAY_2025'):note+=' '+discrepancy
 out['series'].append(dict(id=sid,name=title,org='КМІС',title=title,question=z0['question'],note=note,caption='Повторення одного пакета; округлення збережено.',order=['Легко','Важко, але прийнятно','Неприйнятно','Невизначені']))
 d['dynamics']=[r for r in d['dynamics'] if r['series']!=sid]
 for q in pair:
  z=byq[q];r=records[q];p=ps[qs[q]['poll']];z['series']=sid
  z['mapping']=dict(zip(out['series'][-1]['order'],r['mappings']));r['series']=sid
  for answer,value in zip(out['series'][-1]['order'],r['values']):
   d['dynamics'].append(dict(poll=p['id'],series=sid,period=p['period'],sort=p['end'],answer=answer,pct=value/100,source=qs[q]['source'],location=r['location'],note=r['note']))
qs['Q051']['result']='54% прийнятно; 35% неприйнятно на графіку (у прозі релізу — 30%)'
qs['Q051']['limit']=discrepancy
for q in ['Q049','Q050']:qs[q]['limit']=discrepancy
reported_note='Підписи категорій у графіку відтворено з публікації. Вони можуть відрізнятися від повної шкали анкети; окрему частку відмов не домислюємо.'
for z in w['items']:
 if any(m['kind']=='reported' for m in z['mapping'].values()) and reported_note not in z['note']:z['note']+=' '+reported_note
register.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
(R/'data/wording.json').write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n','utf8')
(R/'data/kiis-packages.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8')
print(len(out['records']),'package observations;',len(out['series']),'repeated-package series')
