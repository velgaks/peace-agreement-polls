"""Import visually checked KIIS historical charts; run once against the local register.

Usage: python scripts/import_kiis_series.py /path/to/peace-agreement-polls
The source and reconciliation log is docs/KIIS-TIME-SERIES-AUDIT.md.
"""
import copy, hashlib, json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup
from poll_dates import normalize_periods

R=Path(__file__).resolve().parents[1]; A=Path(sys.argv[1])
path=A/'_work/research-data.json'; d=json.loads(path.read_text('utf8'))
wp=R/'data/wording.json'; w=json.loads(wp.read_text('utf8'))
assert not any(r['series']=='KIIS_WHO_WINS' for r in d['dynamics']), 'Already imported'
sources={s['id']:s for s in d['sources']}
for n in [1445,1464,1534,1627]:
 sid='K'+str(n)
 if sid not in sources:
  s=dict(id=sid,file=f'kiis-series-{n}.html',url=f'https://kiis.com.ua/?lang=ukr&cat=reports&id={n}')
  d['sources'].append(s);sources[sid]=s
html={sid:BeautifulSoup((A/'sources'/sources[sid]['file']).read_bytes(),'html.parser') for sid in ['K1372','K1445','K1464','K1534','K1627','K1639','K1551','K1572','K1583','K1597','K1608','K2']}
norm=lambda t:' '.join(t.split())
byq={qid:x for x in w['items'] for qid in x['question_ids']}
polls={p['id']:p for p in d['polls']}
population='Громадяни України 18+ на підконтрольній уряду території; без населення за кордоном і недоступних окупованих територій.'

def poll(pid,start,end,source,n=None,title='',note='',method='',published=None):
 p=dict(id=pid,priority='Основне',pollster='КМІС',commissioner='У ретроспективному графіку не зазначено' if len(start)==7 else 'КМІС; замовник окремих питань у релізі не зазначений',title=title,start=start,end=end,period='',published=published,n=n,method=method or ('CATI; випадкова вибірка мобільних номерів' if len(start)==10 else 'Паспорт окремої історичної хвилі у джерелі порівняння не наведено'),population=population,topics=title,limits=note,source=source,report='',check='Звірено з указаним першоджерелом; точність дат збережено.',fieldwork_periods=[dict(start=start,end=end)],date_source=source,date_source_location='Паспорт релізу' if len(start)==10 else 'Підпис місяця в ретроспективному графіку / таблиці',date_checked_on='2026-10-06',date_status='reported_day' if len(start)==10 else 'reported_month',date_note=note or 'Дати поля та розмір вибірки наведені в методологічному описі.')
 normalize_periods(p);d['polls'].append(p);polls[pid]=p

unknown='Відомий лише місяць із ретроспективного порівняння. Точні дні та n цієї хвилі не опубліковані у звіреному джерелі; збіг місяця з іншим записом не доводить тотожність вибірок. Це запис історичної точки, а не підтвердження ще однієї незалежної вибірки.'
poll('P120','2022-05','2022-05','K1372',title='Травень 2022: перемога, реалістичний результат і готовність терпіти',note=unknown)
poll('P121','2023-12','2023-12','K1372',title='Грудень 2023: перемога, реалістичний результат і готовність терпіти',note=unknown)
poll('P122','2024-02-05','2024-02-10','K1372',1202,'Сприйняття перебігу війни через майже два роки вторгнення',published='2024-02-21')
poll('P123','2024-05','2024-05','K1534',title='Травень 2024: готовність терпіти війну',note=unknown)
poll('P124','2025-02','2025-02','K1639',title='Лютий 2025: перемога, реалістичний сценарій і допустимість перемовин',note=unknown)
poll('P125','2025-02','2025-02','K1534',title='Лютий 2025: готовність терпіти війну',note=unknown+' Тотожність із лютневою точкою релізу 1639 (P124) не встановлена; записи не слід рахувати як доведено різні опитування.')
poll('P126','2025-03','2025-03','K1534',title='Березень 2025: готовність терпіти війну',note=unknown)
poll('P127','2026-07-16','2026-07-31','K1627',1808,'Хто переможе: телефонна й особиста частини липневого дослідження',note='Загалом 1808 інтерв’ю: 905 CATI і 903 CAPI. Часовий ряд використовує лише CATI (n=905); загальна оцінка та CAPI збережені як окремі панелі того самого питання. У кожній частині близько 300 інтерв’ю у м. Києві; вагу Києва приведено до його частки в населенні.',method='Змішаний дизайн: CATI (випадкові мобільні номери) і CAPI (стратифікована триступенева вибірка, квоти на останньому ступені); окреме зважування',published='2026-08-10')
# Reuse documented omnibus intervals; question-module bases are kept separately.
for pid,n,sid in [('P28',989,'K1445'),('P29',985,'K1464'),('P31',1011,'K1534')]:
 polls[pid]['check']+=' Для питання про готовність терпіти війну окремий реліз '+sid+' наводить n='+str(n)+'; база питання вказана в каталозі, загальний паспорт омнібусу не замінено.'

meta=[
 dict(id='KIIS_WHO_WINS',name='Хто переможе у війні',org='КМІС',title='Безумовна віра в перемогу України: 80% у травні 2022 і 47% у вересні 2026',question=byq['Q139']['question'],caption='Липень 2026: лише телефонна частина дослідження.',note='Шість точок. У липні 2026 використано CATI (905 інтерв’ю), а не загальну змішану вибірку 1808: 85% очікують перемоги України проти 82% у змішаній. Це та сама комбінація округлених значень, яку реліз 1639 показує як липневу. Невизначені та відмови там, де вони подані разом, залишені категорією графіка. Усі опубліковані категорії показані; окрема анкета травня 2022, грудня 2023 і лютого 2025 не підтверджена.'),
 dict(id='KIIS_REALISTIC_ENDING',name='Реалістичний сценарій завершення війни',org='КМІС',title='Державність із вимушеними територіальними втратами: 6% у травні 2022 і 41% у вересні 2026',question=byq['Q140']['question'],caption='Прогноз респондентів; формулювання змінювалося.',note='П’ять точок. У лютому 2024 питання починається «На Вашу думку, що виглядає як найбільш реалістичний результат…», а остання опція — «Перенесення бойових дій на територію Російської Федерації». У версії 2025–2026 додано явне розрізнення бажаного й можливого та повне відновлення територіальної цілісності в останній опції. Лінія цієї категорії з’єднує близькі, але не ідентичні формулювання; точні версії в паспорті. Опції про втрати не означають юридичного визнання територій Росії. У релізі 1372 числа взято з графіка 5, а не з суперечливої прози (52% і 14% у лютому 2024).'),
 dict(id='KIIS_ALLOW_NEGOTIATIONS',name='Чи допускають переговори зараз',org='КМІС',title='Переговори з Росією допускають 74% у лютому 2025 і 75% у вересні 2026',question=byq['Q141']['question'],caption='Допустимість переговорів не означає підтримки поступок.',note='Дві підтверджені точки саме цього питання. Опубліковано суми «Так, допускаю» + «Скоріше допускаю» і двох негативних відповідей. Питання про дипломатичний шлях, успіх переговорів або переговори за певних поступок вимірюють інше і сюди не включені. Анкета лютого 2025 відома лише через ретроспективний реліз 1639.'),
 dict(id='KIIS_WAR_ENDURANCE',name='Скільки ще готові терпіти війну',org='КМІС',title='Терпіти війну стільки, скільки потрібно: 71% у травні 2022 і 62% у вересні 2026',question=byq['Q143']['question'],caption='Декілька місяців і пів року об’єднано, як у графіках КМІС.',note='17 точок. Показано чотири категорії зі зведених графіків; детальні розподіли з окремими місяцями, півріччям і відмовами, де доступні, збережено у графіках усіх питань. Готовність терпіти не дорівнює ставленню до переговорів чи поступок. Попередній зріз 26.11–13.12.2025 (n=547, 63% «стільки, скільки потрібно») перекривається з фінальним 26.11–29.12 (n=1001, 62%) і не є додатковою незалежною точкою. У низці давніх хвиль встановлено лише місяць, не дні поля.')]
audit=dict(reviewed_on='2026-10-06',series=meta,snapshots={},checks=[dict(source='K1569',decision='Не додано окремою точкою: попередній зріз перекривається з K1572',values=[15,1,63,21]),dict(source='K1627',decision='У ряд включено CATI; загальна і CAPI вибірки — панелі того самого питання'),dict(source='K1407',decision='Виключено з національних рядів: CAWI українських біженців у трьох країнах'),dict(url='https://kiis.com.ua/?lang=ukr&cat=reports&id=1305',decision='Окреме населення: лише місто Київ'),dict(url='https://kiis.com.ua/?lang=ukr&cat=reports&id=1409',decision='Окреме населення: лише місто Київ'),dict(url='https://kiis.com.ua/?lang=ukr&cat=reports&id=1501',decision='Окреме населення: лише місто Київ')])
nextq=144
def add(sid,pid,sort,values,source,location,template,current=None,basis='questionnaire',note='',base='',question=None,options=None,mapping=None,detail=None):
 global nextq
 qid=current or 'Q'+str(nextq)
 if not current:nextq+=1
 z=byq[template] if current else copy.deepcopy(byq[template])
 z.update(id='kiis-'+qid,series=sid,polls=[pid],question_ids=[qid],source_url=sources[source]['url'],location=location+'; формулювання: додаток / підпис графіка',basis=basis,note=note,reviewed_on='2026-10-06',evidence_sha256=hashlib.sha256((A/'sources'/sources[source]['file']).read_bytes()).hexdigest())
 if source!='K1639':z['instructions']=''
 if question:z['question']=question
 if options:z['options']=options
 # The current full instrument is a reference, not proof of older wording.
 if basis in ('reference','retrospective'):
  z['note']+=' Числа — з ретроспективного графіка. Текст і опції — з указаного пізнішого джерела; окремої анкети історичної хвилі не підтверджено.'
  z['instructions']=''
 if sid=='KIIS_WHO_WINS':
  keys=['Безумовно, Україна','Скоріше, Україна','Скоріше, Росія','Безумовно, Росія','Невизначені']
  maps={k:dict(kind='option',indices=[i]) for i,k in enumerate(keys[:-1])}
 elif sid=='KIIS_REALISTIC_ENDING':
  keys=['Державність із втратами','Лінія 24.02.2022','Донбас повністю','Кордони 1991 року','Бойові дії в Росії','Невизначені']
  maps={k:dict(kind='option',indices=[i]) for i,k in enumerate(keys[:-1])}
 elif sid=='KIIS_ALLOW_NEGOTIATIONS':
  keys=['Допускають','Не допускають','Невизначені'];maps={keys[0]:dict(kind='aggregate',indices=[0,1]),keys[1]:dict(kind='aggregate',indices=[2,3])}
 else:
  keys=['Стільки, скільки потрібно','Один рік','Декілька місяців–пів року','Невизначені'];maps={keys[0]:dict(kind='option',indices=[3]),keys[1]:dict(kind='option',indices=[2]),keys[2]:dict(kind='aggregate',indices=[0,1])}
 maps[keys[-1]]=dict(kind='reported',label='Важко сказати')
 z['mapping']=mapping or maps
 if not current:w['items'].append(z)
 qbase=base or ('Усі опитані; n='+str(polls[pid]['n']) if polls[pid]['n'] else 'Усі опитані відповідної історичної хвилі; n у джерелі не наведено')
 if current:
  q=next(q for q in d['questions'] if q['id']==current);q['limit']=note
 else:
  m=next(m for m in meta if m['id']==sid)
  q=dict(id=qid,poll=pid,dimension={'KIIS_WHO_WINS':'Очікування перемоги','KIIS_REALISTIC_ENDING':'Очікування завершення війни','KIIS_ALLOW_NEGOTIATIONS':'Переговори','KIIS_WAR_ENDURANCE':'Готовність терпіти війну'}[sid],scenario=m['name'],result='; '.join(f'{k}: {v}%' for k,v in zip(keys,values)),base=qbase,limit=note,source=source,location=location,cluster='Окремий розподіл, не перетин позицій');d['questions'].append(q)
 for k,v in zip(keys,values):d['dynamics'].append(dict(poll=pid,series=sid,period=polls[pid]['period'],sort=sort,answer=k,pct=v/100,source=source,location=location,note=note+' База: '+qbase))
 if detail:audit['snapshots'][qid]=detail
 return qid

V='KIIS_WHO_WINS';E='KIIS_WAR_ENDURANCE';S='KIIS_REALISTIC_ENDING';N='KIIS_ALLOW_NEGOTIATIONS'
ref='Повні категорії опублікованого графіка; відмови окремо не показані.'
for pid,sort,vals in [('P120','2022-05',[80,15,1,0,4]),('P121','2023-12',[65,23,2,0,9]),('P122','2024-02',[60,29,3,1,7])]:
 add(V,pid,sort,vals,'K1372','Графік 1','Q139',basis='questionnaire' if pid=='P122' else 'reference',note=ref)
add(V,'P124','2025-02',[46,31,7,1,16],'K1639','Графік 1','Q139',basis='reference',note=ref)
def panel(values,caption,heading=''):
 return dict(values=values,caption=caption,heading=heading)
july=add(V,'P127','2026-07',[60,25,2,0,13],'K1627','Додаток 2, CATI; відповідні агрегати — реліз 1639, графік 1','Q139',note='У часовому ряді тільки CATI, n=905. «Важко сказати» у зведеному графіку 1639 — 13%; додаток 1627 подає окремо 12% невизначених і 1% відмов. Не додавати загальні 82% чи CAPI 78% як незалежні заміри.',base='Телефонна частина, n=905; загальний паспорт дослідження n=1808',detail=[panel([60,25,2,0,12,1],'Додаток 2: усі шість опцій; n=905. У динаміці останні дві категорії подані разом.','Телефонні інтерв’ю (CATI)'),panel([59,23,2,0,15,1],'Та сама хвиля, об’єднана вибірка n=1808; не додаткова точка динаміки. Авторський агрегат перемоги Росії 3%, сума округлених сегментів 2%.','CATI + особисті інтерв’ю'),panel([57,21,2,1,18,1],'Додаток 2: особисті інтерв’ю n=903; не незалежна додаткова хвиля.','Особисті інтерв’ю (CAPI)')])
add(V,'P119','2026-09',[47,32,5,2,14],'K1639','Графік 1','Q139',current='Q139',note=ref)

oldquestion='На Вашу думку, що виглядає як найбільш реалістичний результат війни для України?'
oldopts=copy.deepcopy(byq['Q140']['options']);oldopts[4]='Перенесення бойових дій на територію Російської Федерації'
assert oldquestion in norm(html['K1372'].get_text(' ',strip=True))
for pid,sort,vals in [('P120','2022-05',[6,10,9,61,10,5]),('P121','2023-12',[15,9,3,61,8,4]),('P122','2024-02',[19,9,4,52,14,3])]:
 add(S,pid,sort,vals,'K1372','Графік 5; Додаток 1, Б4','Q140',basis='questionnaire' if pid=='P122' else 'reference',question=oldquestion,options=oldopts,note='Старе формулювання питання і п’ятої опції відрізняється від 2025–2026. Це прогноз, а не бажаний сценарій. Збережено значення графіка, включно з округленням; у прозі релізу є неузгоджені суми й згадки років.')
add(S,'P124','2025-02',[33,16,5,25,14,7],'K1639','Таблиця 1','Q140',basis='reference',note='Ретроспективна таблиця 2025/2026; питання відділяє бажане від можливого.')
add(S,'P119','2026-09',[41,14,4,23,12,6],'K1639','Таблиця 1','Q140',current='Q140',note='Прогноз, а не бажаний сценарій. Версія питання та останньої опції відрізняється від 2024 року. Відмови окремо не опубліковані.')
add(N,'P124','2025-02',[74,19,7],'K1639','Графік 2','Q141',basis='reference',note='Опубліковані суми двох позитивних і двох негативних відповідей; не згода на поступки.')
add(N,'P119','2026-09',[75,21,4],'K1639','Графік 2','Q141',current='Q141',note='Опубліковані суми двох позитивних і двох негативних відповідей; не згода на поступки. Відмови окремо не опубліковані.')

endurance=[
 ('P120','2022-05',[71,2,18,8],'K1372','Графік 7','reference',None,[14,4,2,71,8]),
 ('P121','2023-12',[73,2,18,7],'K1372','Графік 7','reference',None,[16,2,2,73,7]),
 ('P122','2024-02',[73,3,21,4],'K1372','Графік 7','questionnaire',1202,[18,3,3,73,4]),
 ('P123','2024-05',[72,5,12,11],'K1534','Графік 1','reference',None,None),
 ('P28','2024-10',[63,6,19,12],'K1445','Графік 4','questionnaire',989,[15,4,6,63,12]),
 ('P29','2024-12',[57,3,21,18],'K1464','Графік 1','questionnaire',985,[18,3,3,57,18]),
 ('P125','2025-02',[57,4,24,15],'K1534','Графік 1','reference',None,None),
 ('P126','2025-03',[54,3,24,18],'K1534','Графік 1','reference',None,None),
 ('P31','2025-06',[60,6,20,14],'K1534','Графік 1','questionnaire',1011,None),
 ('P47','2025-09',[62,4,21,13],'K1551','Графік 6; Додаток 1','questionnaire',1023,[17,4,4,62,12,1]),
 ('P48','2025-12',[62,3,14,21],'K1572','Графік 5; Додаток 1','questionnaire',1001,[11,3,3,62,20,1]),
 ('P50','2026-01',[65,3,17,15],'K1583','Графік 4','questionnaire',1003,None),
 ('P01','2026-02',[52,4,26,18],'K1597','Графік 3, точка «Лют.26»','reference',None,None),
 ('P51','2026-03',[54,3,28,16],'K1597','Графік 3; Додаток 1','questionnaire',1003,[25,3,3,54,14,2]),
 ('P52','2026-04',[48,4,29,19],'K1608','Графік 4; Додаток 1','questionnaire',1005,[25,4,4,48,17,2]),
 ('P02','2026-08',[61,5,20,15],'K2','Графік 5','questionnaire',974,None),
 ('P119','2026-09',[62,4,23,11],'K1639','Графік 4','questionnaire',1002,None)]
for pid,sort,vals,source,location,basis,n,detail in endurance:
 text=norm(html[source].get_text(' ',strip=True));match=re.findall(r'Скільки ще часу [Вв]и готові терпіти війну\?',text)
 question=match[-1] if match else byq['Q143']['question']
 note='У ряді декілька місяців і пів року зведені, як у ретроспективних графіках КМІС. Часовий горизонт не є мірою підтримки поступок.'
 if n is None:note+=' База цього питання у відповідній давній хвилі не встановлена; n загального омнібусу не підміняє її.'
 if pid=='P48':note+=' Використано повну грудневу вибірку; попередній перекривний зріз n=547 з релізу 1569 не додано окремою точкою.'
 detailed=None
 if detail:
  detailed=[panel(detail,'Усі опубліковані окремі категорії. У часовому ряді місяці та пів року об’єднані; невизначені й відмови, якщо опубліковані окремо, тут розділені.')]
 qid=add(E,pid,sort,vals,source,location,'Q143',current='Q143' if pid=='P119' else None,basis=basis,note=note,base=f'База питання: n={n}' if n else 'База питання цієї історичної хвилі у звіреному релізі не наведена',question=question,detail=detailed)
 if detail and len(detail)==5:
  audit['snapshots'][qid][0]['last_label']='Важко сказати (категорія графіка видавця)'

d['as_of']='2026-10-06';w['review']['catalogue_total']=len(d['questions']);w['review']['date']='2026-10-06';w['checked_at']='2026-10-06'
audit['series_counts']={m['id']:len({r['poll'] for r in d['dynamics'] if r['series']==m['id']}) for m in meta}
path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8');wp.write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n','utf8')
(R/'data/kiis-series-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n','utf8')
print(audit['series_counts']);print('polls',len(d['polls']),'questions',len(d['questions']))
