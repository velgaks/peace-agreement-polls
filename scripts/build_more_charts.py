"""Build chart inputs from the audited register; never infer a residual to 100%.

Usage: python scripts/build_more_charts.py /path/to/peace-agreement-polls
The archive supplies publisher PDFs/HTML used for additional exact transcriptions.
"""
import json,sys,copy,re
from pathlib import Path
import fitz
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]; A=Path(sys.argv[1])
d=json.loads((R/'data/research.json').read_text('utf8')); original=json.loads((A/'_work/research-data.json').read_text('utf8'))
w=json.loads((R/'data/wording.json').read_text('utf8'))['items']; byq={q:i for i in w for q in i['question_ids']}; qs={q['id']:q for q in d['questions']}; sources={s['id']:s for s in original['sources']}
norm=lambda s:' '.join(s.split())
def evidence(sid,pages):
 p=A/'sources'/sources[sid]['file']
 if p.suffix=='.pdf':
  doc=fitz.open(p);return norm(' '.join(doc[i-1].get_text() for i in pages))
 return norm(BeautifulSoup(p.read_bytes(),'html.parser').get_text(' ',strip=True))
extra={'series':[],'wording':[],'questions':{},'reviewed_on':'2026-10-05'}
def series(sid,name,org,title,note):
 extra['series'].append(dict(id=sid,name=name,org=org,title=title,question=name,note=note,caption=note.split('. ')[0]+'.'))
def bind(sid,polls,z,maps):
 z=copy.deepcopy(z);z.update(id='chart-'+sid+'-'+polls[0],series=sid,polls=polls,question_ids=[],mapping=maps)
 extra['wording'].append(z);return z
def newword(sid,pages,q,opts,note='',instructions=''):
 t=evidence(sid,pages)
 for v in [q,instructions]+opts:
  if v:assert norm(v) in t,(sid,v)
 return dict(question=q,prompt='',options=opts,instructions=instructions,source_url=sources[sid]['url'],location='PDF, с. '+', '.join(map(str,pages)),basis='retrospective',note=note,language='uk')
def mapping(sid,indices):
 keys=list(dict.fromkeys(r['answer'] for r in d['dynamics'] if r['series']==sid))
 assert len(keys)==len(indices),(sid,keys,indices)
 return {k:dict(kind='aggregate' if isinstance(i,list) else 'option',indices=i if isinstance(i,list) else [i]) for k,i in zip(keys,indices)}
sid='DIF_COMPROMISE_GENERAL'
series(sid,'Компроміси заради миру','ФДІ / Центр Разумкова','У грудні 2022 року 61,8% пов’язували припинення війни лише з перемогою','Дві хвилі 2022 року. Один варіант відповіді; питання не називає конкретних поступок.')
z=newword('D22P',[23,24],'На Вашу думку, чи варто йти на компроміси із Росією заради припинення війни?',['Заради миру варто йти на будь-які компроміси','Можна йти на компроміси, але не на всі','Війна може припинитися лише у разі перемоги','Важко сказати/Відмова'],instructions='(у %; один варіант відповіді)')
bind(sid,['P113','P37'],z,mapping(sid,[0,1,2,3]))
sid='RAZUMKOV_WHEN_TALKS'
series(sid,'Коли вести переговори','Центр Разумкова','Згода з переговорами «вже зараз» зросла з 16,6% до 35,2%','Кожне твердження оцінювали окремо. Показано лише відповідь «Так»; сума ліній не є розподілом населення.')
z=byq['Q083'];maps={k:dict(kind='statement',statement_index=i,indices=[0]) for i,k in enumerate(dict.fromkeys(r['answer'] for r in d['dynamics'] if r['series']==sid))}
for q in ['Q083','Q084','Q085','Q086']:
 z=bind(sid,[qs[q]['poll']],byq[q],maps);z['prompt']=''
sid='SOCIS_CONCESSIONS_MULTI'
series(sid,'Які поступки допускають','SOCIS','У жовтні 2025 року 31,6% обрали «ЖОДНИХ ПОСТУПОК»','Множинний вибір. Опція «ЖОДНИХ ПОСТУПОК» відсутня в перших двох точках таблиці; це не нуль.')
z=newword('SC20251121P',[48],'На які поступки можна піти на переговорах задля завершення бойових дій?',['Відмова від членства в НАТО','Надання російській мові на певних територіях офіційного статусу','Територіальні поступки','Відмова від членства в ЄС','Скорочення чисельності армії','ЖОДНИХ ПОСТУПОК','ВВ/ НЕ ЗНАЮ/ ВIДМОВА'],instructions='Cума відповідей перевищує 100%. Респондент міг обрати декілька варіантів відповіді',note='Дослівний заголовок ретроспективної таблиці; анкети кожної хвилі тут не наведено. Червень 2025 додав окрему категорію відмови від будь-яких поступок; це змінює контекст порівняння.')
maps=mapping(sid,[0,1,2,3,4,6,5])
bind(sid,['P74','P81','P75'],z,maps)
old=copy.deepcopy(z);old['options'].pop(5)
oldmaps={k:dict(v,indices=[5] if v['indices']==[6] else v['indices']) for k,v in maps.items() if v['indices']!=[5]}
bind(sid,['P72','P80'],old,oldmaps)
sid='IRI_CONCESSIONS_2022'
series(sid,'Прийнятні поступки у 2022 році','IRI / Рейтинг','Нейтралітет і відмову від НАТО допускали 37% у квітні та 29% у червні 2022','Множинний вибір; сума може перевищувати 100%. Дослівні опції наведено англійською, мовою звіту.')
for q in ['Q112','Q113']:bind(sid,[qs[q]['poll']],byq[q],mapping(sid,list(range(8))))
sid='SAPIENS_NATO_BAN_2022'
series(sid,'Неприйняття заборони вступу до НАТО','Info Sapiens','У березні 2022 року заборону вступу до НАТО відкидали 51% і 45%','Показано лише неприйняття одного сценарію. Умова питання — гарантія негайного припинення війни.')
z=bind(sid,['P89','P88'],byq['Q114'],mapping(sid,[0]));z['prompt']=z['statements'][2];z.pop('statements')
z['basis']='retrospective'
for sid,name,title,qids in [
 ('ISPP_VICTORY','Повернення до лінії 24.02.2022 як перемога','Згода з поверненням до лінії 24.02.2022 та подальшими переговорами зросла до 59,2%',['Q118','Q121','Q124']),
 ('ISPP_PEACE_PRICE','Мир, але не будь-якою ціною','У 2025 році 76,3% погодилися: «Україні потрібен мир, але не будь-якою ціною»',['Q119','Q122','Q125']),
 ('ISPP_SHAME_WAR','«Маленька ганьба» чи велика війна','Згода із судженням «Краще маленька ганьба, ніж велика війна» зросла до 37%',['Q120','Q123','Q126'])]:
 series(sid,name,'ІСПП НАПН України',title,'Показано згоду та незгоду. Невизначені й ті, хто не відповів, не включені до цих двох ліній.')
 for q in qids:bind(sid,[qs[q]['poll']],byq[q],mapping(sid,[0,1]))
sid='ISPP_PEACE_OPTIONS_2023_24'
series(sid,'Прийнятна умова миру: 2023–2024','ІСПП НАПН України','Вимогу повної капітуляції Росії обирали 42% у 2023 та 31,9% у 2024','Показано п’ять змістовних категорій; «інше» та невизначені в цьому ряді не наведені. Версія 2025 року має інший перелік опцій і показана окремо.')
z=newword('ISPP25S',[115],'Якби війну можна було завершити просто зараз, яка з перелічених нижче умов укладення миру була б для Вас прийнятною',['повна і безумовна капітуляція країни-агресора, виплата нею компенсацій та репарацій за завдану шкоду в повному обсязі','повернення до державних кордонів 1991 року, включно з Донбасом і Кримом','припинення вогню та відведення військ обох сторін від лінії зіткнення','повернення під український контроль територій, окупованих після 24 лютого 2022 року','перетворення нинішньої лінії зіткнення на державний кордон з країною-агресором, якщо це відкриє шлях для вступу України до НАТО і ЄС','інше','важко відповісти'])
bind(sid,['P110','P111'],z,mapping(sid,[0,1,2,3,4]))
for sid,name,qids,values in [('NDI_PEACE_PRICE_TERRITORY_REJECT','Неприйняття визнання територій Росії',['Q137','Q13'],'70% в обох хвилях'),('NDI_PEACE_PRICE_LANGUAGE_REJECT','Неприйняття офіційного статусу російської',['Q138','Q14'],'72% у 2025 та 70% у 2026')]:
 series(sid,name,'NDI / КМІС','Умову відкидають '+values,'Авторські агрегати неприйняття; не сума округлених сегментів. У серпні 2025 повної шкали у звіті немає.')
 for q in qids:
  z=copy.deepcopy(byq[q]);z['options']=z['options'] or z['partial_options'];z.pop('partial_options',None)
  bind(sid,[qs[q]['poll']],z,mapping(sid,[[0,1]]))

# Snapshot charts refer to exact options, or explicitly labelled author aggregates.
wave={(z['series'],p):z for z in w+extra['wording'] for p in z['polls']}
def label(z,m):
 if m['kind']=='reported':return m['label']+' (категорія графіка видавця)'
 texts=[z['options'][i] for i in m['indices']]
 if m['kind']=='statement':return z['statements'][m['statement_index']]+' — '+texts[0]
 return 'Сума відповідей: '+' + '.join('«'+t+'»' for t in texts) if m['kind']=='aggregate' else texts[0]
def plot(q,pairs,*,unit='percent',caption='',heading='',options=None,complete=False):
 z=byq[q];opts=options or z['options'];rows=[]
 for idx,val in pairs:
  ids=idx if isinstance(idx,list) else [idx]
  texts=[opts[i] for i in ids]
  rows.append(dict(label=('Сума відповідей: '+' + '.join('«'+s+'»' for s in texts)) if isinstance(idx,list) else texts[0],value=val))
 p=dict(rows=rows,unit=unit,heading=heading,caption=caption or ('Наведено всі опубліковані категорії; округлення збережено.' if complete else 'Показано лише значення, внесені до реєстру; решту не обчислено як залишок.'))
 extra['questions'].setdefault(q,dict(plots=[],series=[]))['plots'].append(p)
def direct(q,values,**kw):plot(q,list(enumerate(values)),**kw)
links={'Q07':'RAZUMKOV_MINIMUM_PEACE','Q08':'GALLUP_NEGOTIATIONS','Q112':'IRI_CONCESSIONS_2022','Q113':'IRI_CONCESSIONS_2022','Q114':'SAPIENS_NATO_BAN_2022','Q137':'NDI_PEACE_PRICE_TERRITORY_REJECT','Q138':'NDI_PEACE_PRICE_LANGUAGE_REJECT','Q13':'NDI_PEACE_PRICE_TERRITORY_REJECT','Q14':'NDI_PEACE_PRICE_LANGUAGE_REJECT'}
for q in ['Q083','Q084','Q085','Q086']:links[q]='RAZUMKOV_WHEN_TALKS'
for seriesid,qids in [('ISPP_VICTORY',['Q118','Q121','Q124']),('ISPP_PEACE_PRICE',['Q119','Q122','Q125']),('ISPP_SHAME_WAR',['Q120','Q123','Q126'])]:
 for q in qids:links[q]=seriesid
for q,z in byq.items():
 sid=links.get(q,z['series']);rs=[r for r in d['dynamics'] if r['series']==sid and r['poll']==qs[q]['poll']]
 if not rs:continue
 exact=wave[(sid,qs[q]['poll'])]
 extra['questions'][q]=dict(series=[sid],plots=[dict(unit='percent',heading='',caption='Ті самі опубліковані категорії, що й у часовому ряді. Пропущені категорії не дорівнюють нулю.',rows=[dict(label=label(exact,exact['mapping'][r['answer']]),value=round(r['pct']*100,6)) for r in rs])])
plot('Q01',[(0,25),(1,70),([2,3],5)])
for q,yes,no in [('Q03',25,68),('Q05',59,31),('Q042',38,54),('Q043',47,38),('Q044',57,33),('Q046',10,82),('Q047',29,61),('Q048',51,40),('Q049',17,76),('Q050',39,49),('Q051',54,30),('Q052',17,75),('Q059',17,74),('Q065',32,61),('Q066',42,49),('Q067',53,37),('Q068',61,33)]:plot(q,[([0,1],yes),(2,no)])
for q,v in [('Q053',74),('Q058',69)]:plot(q,[([0,1],v)])
plot('Q06',[(1,75.2)]);direct('Q09',[10,19,23,42,6],complete=True);direct('Q10',[37,11,7,5,4,30,17],caption='Множинний вибір: сума може перевищувати 100%.')
direct('Q07',[28.8,27.5,21.7,11.1,5.6,5.2],complete=True)
direct('Q11',[66,22,12],complete=True);direct('Q12',[64.1,44.4,35.8,34.9,28.6,16.3,1.8,4.5],caption='Множинний вибір: сума може перевищувати 100%.')
for q,vals in [('Q13',[55,14,10,4,16]),('Q14',[54,15,11,7,13])]:
 extra['questions'][q]['plots']=[];direct(q,vals,complete=True,caption='Округлені сегменти. Авторський агрегат неприйняття — 70%; сума двох округлених сегментів — 69%.')
for q,vals in [('Q15',[30,29,35,6]),('Q128',[20,25,52,4]),('Q129',[12,26,55,7]),('Q130',[44,32,21,4]),('Q131',[15,26,56,4]),('Q132',[26,69,5])]:direct(q,vals,complete=True)
plot('Q16',[([0,1],28.8),([2,3],58.8)])
direct('Q17',[72.2,20.8,7],complete=True)
direct('Q18',[20.4,20.9,22.3,29.4,7],complete=True,heading='Територіальні компроміси')
f=byq['Q18']['followups'][0];direct('Q18',[6.6,9.4,21.1,55.2,7.7],options=f['options'],heading=f['question']+'. '+f['statements'][0],complete=True)
direct('Q19',[33,16,15,11,10,15],complete=True);direct('Q20',[74,24,2],complete=True);direct('Q21',[3,5,11,78,3],complete=True)
direct('Q22',[23,59.6,17.4],complete=True)
for q,yes,no,dk in [('Q23',25.6,63.1,11.4),('Q24',4.7,90.4,4.9)]:plot(q,[([0,1],yes),([2,3],no),(4,dk)],caption=('Лише серед прихильників будь-яких компромісів; не частка всього населення.' if q=='Q23' else 'Опубліковані агрегати прийнятності; округлення збережено.'))
plot('Q041',[(0,86),(1,10)],caption='Суми повної та часткової згоди з обраним твердженням; невизначені не показані.')
plot('Q045',[(0,18),([1,2],59)],caption='Частки серед усіх опитаних, не серед прихильників перемир’я. Інші відповіді не показані.')
plot('Q064',[(0,61),(1,10)],caption='Серед усіх опитаних. 86%/14% серед тих, хто обрав голосування, — інша база.')
plot('Q069',[(0,77),(1,12),([2,3],11)])
for q,yes,no in [('Q076',8,78),('Q077',5,81.9),('Q078',7,78)]:plot(q,[(0,yes),(1,no)])
plot('Q087',[(0,6),(2,51)])
plot('Q088',[(0,10)])
f=byq['Q088']['followups'][0];plot('Q088',list(enumerate([6,14,14])),options=f['statements'],heading=f['question'],caption='Для кожної вимоги — сума «Повністю прийнятним» і «Скоріше прийнятним». Інші категорії не показані.')
for q,yes,no in [('Q089',9,81),('Q092',13.4,75.8),('Q093',34.7,50.8),('Q094',20,69.8),('Q095',22.3,60.5)]:plot(q,[([0,1],yes),([2,3],no)])
direct('Q090',[21.3,23.5,34.7,20.5],complete=True);direct('Q091',[72.8,7.1,20.1],complete=True);direct('Q096',[43,54,3],complete=True)
plot('Q107',[(9,2.5),(8,2.9),(10,3),(6,3.2),(0,3.3),(7,3.4),(5,3.6),(3,4.1),(2,4.3),(1,4.6),(4,6.2)],options=byq['Q107']['statements'],unit='mean10',caption='Середні бали, шкала 1–10. Джерело: с. 20; це не відсотки підтримки.')
direct('Q108',[8.4,9.4,11.7,14.8,21,34.8],complete=True)
for q,v in [('Q109',54),('Q110',52)]:plot(q,[(0,v)],options=['Повернення всіх територій у кордонах 1991 року'],caption='Назва — переказ аналітичної категорії авторів. Дослівне питання та повна шкала не опубліковані.')
plot('Q111',[(0,63)],options=['Підтримують припинення війни через переговори'],caption='Переказ категорії авторів; після самітів. Повної шкали в публікації немає.')
plot('Q111',[(0,3.45),(1,3.77)],options=['До самітів','Після самітів'],unit='mean5',caption='Парна база n=437, середній бал за шкалою 1–5. Підписи точок — періоди, не опції анкети.')
extra['questions']['Q114']['plots']=[];plot('Q114',list(enumerate([82,80,45])),options=byq['Q114']['statements'],caption='Для кожного сценарію — «Ні, не готові прийняти такий сценарій». Показано лише цю категорію.')
direct('Q115',[2,83,11,4],complete=True);direct('Q116',[74,22,4],complete=True);direct('Q117',[43,55,1],complete=True)
direct('Q127',[35.4,20.1,16.1,11.1,7.6,.9,8.8],complete=True);direct('Q136',[32,31,16,7,5,1,3,7],complete=True)

# The factorial experiment: publish parameter-level marginals, not 96 tiny groups.
t=evidence('K25A',[]);html=BeautifulSoup((A/'sources'/sources['K25A']['file']).read_bytes(),'html.parser')
tables=html.find_all('table');table=next(tab for tab in tables if '44' in tab.get_text() and 'Можуть прийняти' in tab.get_text())
experiment=[]
for tr in table.find_all('tr'):
 cells=[norm(c.get_text(' ',strip=True)) for c in tr.find_all(['td','th'])]
 if len(cells)==3 and all(re.fullmatch(r'\d+',v) for v in cells[1:]):experiment.append((cells[0],int(cells[1]),int(cells[2])))
assert len(experiment)==13,experiment
for labeltext,yes,no in experiment:
 assert labeltext in t
 plot('Q25',[([0,1],yes),(2,no)],heading=labeltext,caption='Прийнятність пакета з цим пунктом за рівної представленості інших умов. Не окремий ефект і не частка сталої групи.')
extra['questions']['Q25']['note']='Показано 13 рівнів п’яти параметрів із таблиці 1. Окремі 96 комбінацій мали лише 11–30 відповідей; для них автори не вважають оцінки статистично надійними.'
assert set(extra['questions'])==set(qs),set(qs)-set(extra['questions'])
for q,entry in extra['questions'].items():
 for p in entry['plots']:
  ceiling=100 if p['unit']=='percent' else int(p['unit'][4:])
  assert all(0<=r['value']<=ceiling for r in p['rows']),q
  p['source_url']=byq[q]['source_url'];p['location']='PDF, с. 20' if q=='Q107' else byq[q]['location']
(R/'data/more-charts.json').write_text(json.dumps(extra,ensure_ascii=False,indent=2)+'\n','utf8')
(R/'more-series.js').write_text('// Generated by scripts/build_more_charts.py\nexport const MORE_SERIES='+json.dumps(extra['series'],ensure_ascii=False,indent=2)+';\n','utf8')
print('Added series:',len(extra['series']),'question charts:',len(extra['questions']),'plots:',sum(len(q['plots']) for q in extra['questions'].values()))
