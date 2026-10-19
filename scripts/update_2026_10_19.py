"""Import audited October releases and their published historical charts once.

Usage: python scripts/update_2026_10_19.py <asset-library>
The saved publisher files remain the evidence; no missing response is a residual.
"""
import copy, hashlib, json, re, sys
from pathlib import Path
import fitz
from bs4 import BeautifulSoup
from poll_dates import normalize_periods

R=Path(__file__).resolve().parents[1]; A=Path(sys.argv[1]); DAY='2026-10-19'
register=A/'_work/research-data.json';d=json.loads(register.read_text('utf8'))
w=json.loads((R/'data/wording.json').read_text('utf8'))
assert not any(s['id']=='K1643' for s in d['sources']),'Already imported'
sources={s['id']:s for s in d['sources']};polls={p['id']:p for p in d['polls']}
update=dict(reviewed_on=DAY,series=[],snapshots={},decisions=[],search=[])
nextp=max(int(p[1:]) for p in polls)+1;nextq=max(int(q['id'][1:]) for q in d['questions'])+1
def save_source(sid,file,url):
 z=dict(id=sid,file=file,url=url);d['sources'].append(z);sources[sid]=z
save_source('K1643','kiis-1643.html','https://kiis.com.ua/?lang=ukr&cat=reports&id=1643')
save_source('RO26','rating-oct2026.html','https://www.ratinggroup.ua/news/socpol-oct2026')
save_source('RO26P','rating-2026-october.pdf','https://cdn.prod.website-files.com/685c279caf66f4023ad2cab4/6ac74321c48d501c925096d4_RG_UA_1000_CATI_05102026_press_compressed.pdf')
LURL='https://www.slovoidilo.ua/2026/10/16/dajdzhest/suspilstvo/rezultaty-soczopytuvannya-temu-perehovornyj-trek-ta-hotovnist-sluzhyty-sylax-oborony'
save_source('LM26','slovoidilo-2026-september.html',LURL)
lh=BeautifulSoup((A/'sources/slovoidilo-2026-september.html').read_bytes(),'html.parser')
lu=[a['href'].replace('http:','https:') for a in lh.select('a[href]') if '_origin.png' in a['href']]
for i,u in enumerate(lu,1):save_source('LM26I'+str(i),f'lemur-sep2026-{i}.png',u)
norm=lambda s:' '.join(s.split())
texts={sid:norm(BeautifulSoup((A/'sources'/sources[sid]['file']).read_bytes(),'html.parser').get_text(' ',strip=True)) for sid in ['K1643','K2']}
pdf=fitz.open(A/'sources/rating-2026-october.pdf')
def newpoll(start,end,source,title,*,org='КМІС',n=None,published=None,method='',limits='',priority='Основне',wave_label=''):
 global nextp
 pid='P'+str(nextp);nextp+=1
 z=dict(id=pid,priority=priority,pollster=org,commissioner='Власна ініціатива' if org=='КМІС' else ('«Слово і діло»' if 'Lemur' in org else 'У релізі окремо не вказано'),title=title,start=start,end=end,period='',published=published,n=n,method=method or 'Паспорт окремої ретроспективної хвилі не наведено',population='Доросле населення на підконтрольній уряду території України; без населення за кордоном і недоступних окупованих територій.',topics=title,limits=limits,source=source,report='',check='Джерело та формулювання звірено '+DAY,fieldwork_periods=[dict(start=start,end=end)],date_source=source,date_source_location='Методологічний опис' if len(start)==10 else 'Підпис місяця на ретроспективному графіку',date_checked_on=DAY,date_status='reported_day' if len(start)==10 else 'reported_month',date_note='Дати поля наведені в методології джерела.' if len(start)==10 else 'Відомий лише місяць з ретрографіка. Дні, база і незалежність від інших публікацій цього місяця не встановлені.')
 if wave_label:z['wave_label']=wave_label;z['date_note']+=' '+wave_label+' — позначення джерела; це не встановлені дні або половина місяця.'
 normalize_periods(z);d['polls'].append(z);polls[pid]=z;return pid
kp=newpoll('2026-10-08','2026-10-16','K1643','Війна і мир: Донбас, тривалість, перешкоди миру',n=1031,published=DAY,method='CATI; випадкові мобільні номери; статистичне зважування',limits='Дизайн-ефект 1,3; максимальна формальна похибка 4,0%. Для експериментальних половин близько 500 — до 5,7%. Підперіоди 8–9 жовтня (n=274) і 10–16 (n=757) є частинами цієї вибірки, не додатковими незалежними хвилями. Війна додає систематичні зміщення.')
rp=newpoll('2026-10-03','2026-10-05','RO26','Суспільно-політичні настрої: переговори та території',org='Соціологічна група «Рейтинг»',n=1000,published='2026-10-08',method='CATI; випадкова вибірка мобільних телефонних номерів; зважування',limits='95%, формальна похибка до 3,1%. Без ТОТ і територій без українського мобільного зв’язку; звіт не подає днів і n для більшості історичних точок.')
polls[rp]['report']='RO26P'
lp=newpoll('2026-09-25','2026-10-01','LM26','Переговорний трек: сьома хвиля онлайн-панелі',org='Lemur / «Слово і діло»',n=1200,published='2026-10-16',method='CAWI; самозаповнення анкети учасниками панелі Lemur',priority='Додаткове: онлайн',limits='Інтернет-користувачі 18+; без недоступних ТОТ. Імовірнісність рекрутингу і відсів панелі не описані. Заявлені 2,89% без дизайн-ефекту не охоплюють похибку самовідбору. «Вересень» у графіках охоплює поле до 1 жовтня.')
def meta(sid,name,org,note,order=None):
 z=dict(id=sid,name=name,org=org,title=name,question=name,note=note,caption=note.split('. ')[0]+'.')
 if order:z['order']=order
 update['series'].append(z)
def reported(label):return dict(kind='reported',label=label)
def opt(i):return dict(kind='option',indices=[i])
def agg(*ii):return dict(kind='aggregate',indices=list(ii))
def instrument(sid,pid,question,options,source,location,mapping,*,prompt='',basis='questionnaire',note='',instructions='',statements=None):
 z=dict(id=f'oct19-{sid}-{pid}',series=sid,polls=[pid],question_ids=[],question=question,prompt=prompt,options=options,instructions=instructions,mapping=mapping,source_url=sources[source]['url'],location=location,basis=basis,note=note,language='uk',reviewed_on=DAY,evidence_sha256=hashlib.sha256((A/'sources'/sources[source]['file']).read_bytes()).hexdigest())
 if statements:z['statements']=statements
 if source in texts:
  for v in [question,prompt]+options+(statements or []):
   if v:assert norm(v) in texts[source],(source,v)
 w['items'].append(z);return z
def question(z,pid,source,location,title,values,*,dimension='Переговори',base='',note='',sort=None):
 global nextq
 qid='Q'+str(nextq);nextq+=1;z['question_ids'].append(qid)
 base=base or ('Усі опитані; n='+str(polls[pid]['n']) if polls[pid]['n'] else 'Відповідна ретроспективна хвиля; n не встановлено')
 q=dict(id=qid,poll=pid,dimension=dimension,scenario=title,result='; '.join(f'{k}: {v}%' for k,v in values.items()),base=base,limit=note or z['note'],source=source,location=location,cluster='Окремий розподіл; не оцінка розміру групи')
 d['questions'].append(q)
 for key,value in values.items():
  old=next((r for r in d['dynamics'] if r['series']==z['series'] and r['poll']==pid and r['answer']==key),None)
  if old:assert round(old['pct']*100,6)==value,(pid,key,old,value)
  else:d['dynamics'].append(dict(poll=pid,series=z['series'],period=polls[pid]['period'],sort=sort or polls[pid]['end'],answer=key,pct=value/100,source=source,location=location,note=q['limit']+' База: '+base))
 return qid
def snapshot(qid,z,values,source,location,caption='',heading=''):
 def text(m):
  if m['kind']=='reported':return m['label']
  parts=[z['options'][i] for i in m['indices']]
  return 'Сума відповідей: '+' + '.join('«'+p+'»' for p in parts) if m['kind']=='aggregate' else parts[0]
 update['snapshots'].setdefault(qid,[]).append(dict(unit='percent',heading=heading,caption=caption or z['note'] or 'Усі опубліковані категорії; округлення збережено.',rows=[dict(label=text(z['mapping'][key]),value=v) for key,v in values.items()],source_url=sources[source]['url'],location=location))
def snap_only(z,pid,source,location,title,values,**kw):
 qid=question(z,pid,source,location,title,{},**kw);q= d['questions'][-1];q['result']='; '.join(f'{key}: {v}%' for key,v in values.items());snapshot(qid,z,values,source,location);return qid
KNOTE='Повтор стандартного питання; підперіоди жовтневої вибірки не додані окремими точками. Порядок питання про тривалість і очікувану дату завершення рандомізовано.'
old=next(z for z in w['items'] if 'Q04' in z['question_ids'])
z=instrument('KIIS_DONBAS_GUARANTEES_2026',kp,old['question'],old['options'],'K1643','Графік 1.1; додаток 1',copy.deepcopy(old['mapping']),prompt=old['prompt'],note=KNOTE,instructions='РАНДОМІЗАЦІЯ ПОРЯДКУ')
kdon=question(z,kp,'K1643','Графік 1.1','Донбас в обмін на гарантії',{'Приймають':35,'Категорично відкидають':61},dimension='Пакет умов',sort='2026-10-08')
package=dict(question_id=kdon,values=[7,28,61,4,0],mappings=[opt(i) for i in range(5)],source_url=sources['K1643']['url'],image_url='',location='Графік 1.1',note='Усі п’ять категорій графіка, включно з опублікованою нульовою відмовою. '+KNOTE,reported_accept=35)
packages=json.loads((R/'data/kiis-packages.json').read_text('utf8'));packages['records'].append(package);packages['reviewed_on']=DAY
eopts=['Декілька місяців','Пів року','1 рік','Стільки, скільки потрібно буде','ВАЖКО СКАЗАТИ (НЕ ЗАЧИТУВАТИ)','ВІДМОВА ВІДПОВІДАТИ (НЕ ЗАЧИТУВАТИ)']
emaps={'Стільки, скільки потрібно':opt(3),'Один рік':opt(2),'Декілька місяців–пів року':agg(0,1),'Невизначені':reported('Важко сказати')}
z=instrument('KIIS_WAR_ENDURANCE',kp,'Скільки ще часу ви готові терпіти війну?',eopts,'K1643','Графік 3; додаток 1',emaps,note=KNOTE+' Відмови окремо у зведеному графіку не наведені.',instructions='ЗАЧИТАТИ')
kend=question(z,kp,'K1643','Графік 3','Скільки ще готові терпіти війну',dict(zip(emaps,[62,4,21,13])),dimension='Готовність терпіти війну',sort='2026-10')
audit=json.loads((R/'data/kiis-series-audit.json').read_text('utf8'));audit['series_counts']['KIIS_WAR_ENDURANCE']=18
for m in audit['series']:
 if m['id']=='KIIS_WAR_ENDURANCE':m['title']='Терпіти війну стільки, скільки потрібно: 71% у травні 2022 і 62% у жовтні 2026';m['note']=m['note'].replace('17 точок.','18 точок.')+' Жовтень 2026: 8–16 жовтня, n=1031; підперіоди не окремі хвилі.'
end_sid='KIIS_EXPECTED_END_2026_2027'
meta(end_sid,'Коли завершиться війна: 2026, 2027 чи пізніше','КМІС','Порівнюються ті самі календарні межі. У липні–серпні два варіанти до кінця 2026 об’єднані; у жовтні об’єднано другу половину 2027 і 2028+. Повні первинні шкали — в окремих питаннях.')
kmaps={'До кінця 2026':opt(0),'Перше півріччя 2027':opt(1),'Друге півріччя 2027 або пізніше':agg(2,3),'Невизначені':reported('Важко сказати')}
ko=['До кінця цього 2026 року','У першій половині наступного 2027 року','У другій половині наступного 2027 року','У 2028 році і пізніше',*eopts[4:]]
z=instrument(end_sid,kp,'На вашу думку, коли може завершитися війна?',ko,'K1643','Графік 2; додаток 1',kmaps,note='Прогноз часу, не бажана тривалість. Змінено опції порівняно з липнем–серпнем; зіставлення після явного укрупнення календарних інтервалів.',instructions='ЗАЧИТАТИ')
q=question(z,kp,'K1643','Графік 2','Очікувана дата завершення війни',dict(zip(kmaps,[10,13,56,21])),dimension='Очікування завершення війни',sort='2026-10')
zdetail=copy.deepcopy(z);zdetail['mapping']={str(i):opt(i) for i in range(4)}|{'dk':reported('Важко сказати')};snapshot(q,zdetail,dict(zip(zdetail['mapping'],[10,13,17,39,21])),'K1643','Графік 2')
ks=BeautifulSoup((A/'sources'/sources['K2']['file']).read_bytes(),'html.parser');alltext=norm(ks.get_text(' ',strip=True))
jopts=['У найближчі декілька тижнів, до кінця літа цього 2026 року','Восени-взимку цього 2026 року','У першій половині наступного 2027 року','У другій половині наступного 2027 року чи пізніше','ВАЖКО СКАЗАТИ (НЕ ЗАЧИТУВАТИ)','ВІДМОВА ВІДПОВІДАТИ (НЕ ЗАЧИТУВАТИ)']
z=instrument(end_sid,'P02','На вашу думку, коли може завершитися війна?',jopts,'K2','Графік 4; додаток 1',{'До кінця 2026':agg(0,1),'Перше півріччя 2027':opt(2),'Друге півріччя 2027 або пізніше':opt(3),'Невизначені':reported('Важко сказати')},note='Два варіанти до кінця 2026 сумуються: 5%+16%=21%. Це календарно порівнюваний інтервал із жовтнем; повні опції збережено.')
q=question(z,'P02','K2','Графік 4','Очікувана дата завершення війни',dict(zip(z['mapping'],[21,15,45,19])),dimension='Очікування завершення війни',sort='2026-08')
zz=copy.deepcopy(z);zz['mapping']={str(i):opt(i) for i in range(4)}|{'dk':reported('Важко сказати')};snapshot(q,zz,dict(zip(zz['mapping'],[5,16,15,45,19])),'K2','Графік 4')
attq='З якою точкою зору щодо обстрілів Росією українських об’єктів економіки, як-от порти, склади, АЗС тощо, Ви згодні в більшій мірі?'
atto=['Росія хоче знищити економіку України, створити життя українців нестерпним, щоб змусити до капітуляції','Росія діє у відповідь – це Україна почала масштабно атакувати російські об’єкти економіки і спровокувала її на відповідь','Росія атакує лише пов’язані з армією об’єкти і не хоче знищувати економіку і робити життя українців нестерпним','ІНШЕ (ЩО САМЕ?) (НЕ ЗАЧИТУВАТИ)',*eopts[4:]]
z=instrument('OCT19_KIIS_ATTACKS',kp,attq,atto,'K1643','Графік 4; додаток 1',{'a':opt(0),'b':opt(1),'c':opt(2),'dk':reported('Важко сказати')},instructions='ЗАЧИТАТИ. РАНДОМІЗАЦІЯ ПОРЯДКУ',note='Варіант про економічні об’єкти відрізняється від січневого питання про енергетику; не з’єднано як дослівний повтор. Формулювання задає оцінні альтернативи, «інше» та відмова окремо не опубліковані.')
snap_only(z,kp,'K1643','Графік 4','Трактування ударів РФ і примусу до капітуляції',dict(zip(z['mapping'],[92,3,2,3])),dimension='Сприйняття агресії')
statements=['«Українська влада має бути більш поступливою у мирних переговорах, щоб домовитися з Росією.»','«Росія хоче підкорити Україну, тому не готова на мир, при якому Україна буде суверенною державою з сильною армією.»']
agree=['Повністю згодні','Скоріше згодні','Скоріше не згодні','Зовсім не згодні',*eopts[4:]]
for i,vals in enumerate([[5,15,21,52,7],[68,15,6,5,5]]):
 z=instrument('OCT19_KIIS_AGREE_'+str(i),kp,'Ви повністю згодні, скоріше згодні, скоріше не згодні чи зовсім не згодні з наступними твердженнями?',agree,'K1643','Графік 5; додаток 1',dict(zip(['a','b','c','d','dk'],[opt(0),opt(1),opt(2),opt(3),reported('Важко сказати')])),prompt=statements[i],instructions='РАНДОМІЗАЦІЯ ТВЕРДЖЕНЬ',note='Випадкова половина A1, близько 500 респондентів. Два твердження оцінюються окремо: згода не утворює взаємовиключних груп. 20% згоди з поступливістю не зіставні безпосередньо з 12% вибору цієї причини в A2.')
 snap_only(z,kp,'K1643','Графік 5','Поступливість влади' if i==0 else 'Росія не готова до миру із сильною Україною',dict(zip(z['mapping'],vals)),base='Половина A1; близько 500, точну реалізовану базу в релізі не наведено',dimension='Експеримент формулювання')
fo=['Українська влада занадто непоступлива і це заважає можливості домовитися з Росією','Росія хоче підкорити Україну, тому не готова на мир, при якому Україна буде суверенною державою з сильною армією',*eopts[4:]]
z=instrument('OCT19_KIIS_FORCED',kp,'Що краще відповідає Вашій думці про те, що перешкоджає досягненню миру?',fo,'K1643','Графік 6; додаток 1',{'ua':opt(0),'ru':opt(1),'dk':reported('Важко сказати')},instructions='ЗАЧИТАТИ. РАНДОМІЗАЦІЯ ПОРЯДКУ',note='Випадкова половина A2, близько 500. Вимушений вибір між двома оціночними альтернативами; це інший інструмент, ніж незалежна оцінка згоди у A1. Відмова окремо не опублікована.')
snap_only(z,kp,'K1643','Графік 6','Що перешкоджає миру: вибір причини',{'ua':12,'ru':78,'dk':10},base='Половина A2; близько 500, точну реалізовану базу не наведено',dimension='Експеримент формулювання')

# Rating: positions of printed numerals are paired with the printed column labels.
def columns(file,p,bottom):
 f=fitz.open(A/'sources'/file);words=f[p-1].get_text('words')
 ticks=sorted([t for t in words if t[1]>330 and re.fullmatch(r"\d\d['`’]2[2-6]",t[4])],key=lambda t:t[0]);xs=[(t[0]+t[2])/2 for t in ticks];gs=[[] for _ in ticks]
 for t in words:
  if t[4].isdigit() and 80<t[1]<bottom and 145<t[0]<900:
   x=(t[0]+t[2])/2;j=min(range(len(xs)),key=lambda j:abs(xs[j]-x))
   if abs(xs[j]-x)<7:gs[j].append((t[1],int(t[4])))
 return [(re.sub(r"['`’]",'-',t[4]),[v for y,v in sorted(g,reverse=True)]) for t,g in zip(ticks,gs)]
rpool={r['sort'][:7]:r['poll'] for r in d['dynamics'] if r['series']=='RATING_REALISTIC_END'};rpool['2026-10']=rp
def rating_poll(label,suffix=''):
 month='20'+label[-2:]+'-'+label[:2];key=month+suffix
 if key not in rpool:rpool[key]=newpoll(month,month,'RO26P','Моніторинг «Рейтингу»: '+month+suffix,org='Соціологічна група «Рейтинг»',limits='Ретроспективний запис. Не рахувати як додаткову незалежну вибірку без паспорта; може збігатися з іншими публікаціями за місяць.',wave_label='хвиля '+suffix if suffix else '')
 return rpool[key],month
RN='Текст питання й опції — з опублікованого графіка, не окремої анкети. Історичні дні та n не підмінені паспортом жовтня. Заміри одного місяця I/II — різні точки; їхнє розташування на осі трохи розведене для видимості без приписування точних днів.'
def rating_series(sid,name,page,options,reorder,suffixes={}):
 meta(sid,name,'Рейтинг',RN)
 points=columns('rating-2026-october.pdf',page,350 if page in [9,11] else 330)
 for j,(label,vals) in enumerate(points):
  assert len(vals)==len(options),(page,j,vals)
  pid,month=rating_poll(label,suffixes.get(j,''));qtext=norm(pdf[page-1].get_text()).split('2026 ',1)[-1]
  qtext={8:'Яке ваше загальне відчуття війни зараз?',9:'З яким з цих тверджень Ви згодні?',10:'Який сценарій розвитку подій щодо війни Ви підтримуєте?'}[page]
  for v in [qtext]+options:assert v in norm(pdf[page-1].get_text()),(page,v)
  z=instrument(sid,pid,qtext,options,'RO26P',f'PDF, с. {page}',{str(i):opt(i) for i in range(len(options))},basis='report' if pid==rp else 'retrospective',note=RN)
  question(z,pid,'RO26P',f'PDF, с. {page}',name,dict(zip(z['mapping'],[vals[i] for i in reorder])),dimension='Сценарії та переговори',sort=month)
rating_series('RATING_CURRENT_WAR_STATE','Хто зараз перемагає у війні',8,['Україна перемагає','Жодна зі сторін не перемагає','Важко відповісти','Росія перемагає'],[3,2,1,0],{14:'I',15:'II',16:'I',17:'II',18:'I',19:'II'})
rating_series('RATING_PEACE_OR_VICTORY','Мир чи перемога: пріоритет',9,['Мир важливіший за будь-яку перемогу','Важко відповісти','Перемога важливіша за будь-який мир'],[2,1,0],{18:'I',19:'II',20:'I',21:'II',23:'I',24:'II',26:'I',27:'II',29:'II',30:'I',31:'II'})
rating_series('RATING_WAR_SCENARIO','Бойові дії чи пошук компромісу',10,['Припинити бойові дії і почати пошук компромісу на переговорах','Важко відповісти','Інше','Воювати до повернення кордонів станом на 23 лютого 2022 року','Воювати до повернення Донбасу і Криму'],[4,3,2,1,0])
# Preserve original 2025 categories, including the option missing from the new retrospective.
oldword=next(z for z in w['items'] if z['id']=='rating-realistic')
oldkeys=['Відмова від переговорів, війна до звільнення всього','Компромісні переговори за участю інших країн','Інше','Важко відповісти','Погодитися на більшість вимог росії']
oldword['mapping'].update({oldkeys[2]:opt(2),oldkeys[3]:opt(1),oldkeys[4]:opt(0)})
for label,vals in columns('rating-2025-february.pdf',17,360):
 pid,month=rating_poll(label)
 assert len(vals) in [4,5]
 question(oldword,pid,'RT25FP','PDF, с. 17','Реалістичний шлях завершення війни',dict(zip(oldkeys,vals)),dimension='Сценарії та переговори',sort=month,note='Дані з первинного графіка 2025, включно з «інше», невизначеністю і надрукованою підтримкою більшості вимог РФ. У ретроспективі жовтня 2026 дрібні категорії переглянуті; первинні значення збережено. Ненадруковане значення не прирівняно до нуля.')
newoptions=['Відмовитися від переговорів і воювати до звільнення усіх територій','Шукати компромісне рішення на переговорах із залученням інших країн','Шукати компроміс на прямих переговорах з росією','Інше','Важко відповісти']
for j,(label,vals) in enumerate(columns('rating-2026-october.pdf',11,350)):
 if j<15:continue
 pid,month=rating_poll(label);options=newoptions if j>=16 else [newoptions[i] for i in [0,1,3,4]]
 keys=[oldkeys[0],oldkeys[1]]+(['Прямі переговори з росією'] if j>=16 else [])+oldkeys[2:4]
 z=instrument('RATING_REALISTIC_END',pid,'Яким, на Вашу думку, є реальний шлях завершити війну?',options,'RO26P','PDF, с. 11',dict(zip(keys,[opt(i) for i in range(len(keys))])),basis='report' if pid==rp else 'retrospective',note=RN+' З квітня 2025 додано прямі переговори. «Погодитися на більшість вимог росії» не наведено в цій ретроспективі. Старі дрібні категорії з первинного графіка 2025 не переписані за новою ретроспективою.')
 question(z,pid,'RO26P','PDF, с. 11','Реалістичний шлях завершення війни',dict(zip(keys,vals)),dimension='Сценарії та переговори',sort=month)
for sid,page,name,months,vectors,question_text,options in [
 ('RATING_DECIDE_TERRITORY',12,'Хто має вирішувати щодо територіальних поступок',['12-25','01-26','10-26'],[[70,6,7,18],[66,6,7,20],[68,6,9,17]],'Хто, на Вашу думку, повинен приймати остаточне рішення щодо територіальних поступок в обмін на мир?',['Народ на референдумі','Важко відповісти','Верховна Рада','Президент']),
 ('RATING_TERRITORY_GUARANTEES',13,'Територіальні поступки та гарантії безпеки',['08-25','10-26'],[[33,5,59,3],[35,6,56,3]],'Чи повинна Україна йти на територіальні поступки заради встановлення довготривалого миру?',['Не повинна йти на поступки','Важко відповісти','Повинна йти на поступки за умов реальних гарантій безпеки від США та країн Європи, які включатимуть фінансування нашої армії та необхідної зброї','Повинна йти на поступки за будь-яких умов'])]:
 meta(sid,name,'Рейтинг',RN+' Вступ і перелік альтернатив можуть задавати оцінний контекст; підтримка умовних поступок не є безумовною підтримкою втрати територій.')
 for label,vals in zip(months,vectors):
  pid,month=rating_poll(label)
  for text in [question_text]+options:assert text in norm(pdf[page-1].get_text()),(page,text)
  z=instrument(sid,pid,question_text,options,'RO26P',f'PDF, с. {page}',{str(i):opt(i) for i in range(4)},basis='report' if pid==rp else 'retrospective',note=RN)
  question(z,pid,'RO26P',f'PDF, с. {page}',name,dict(zip(z['mapping'],vals)),dimension='Території та гарантії',sort=month)

# Additional online panel: every printed category in all seven published columns.
LN='Додаткове джерело: онлайн-панель Lemur, а не ймовірнісна телефонна вибірка. Заголовок і категорії інфографіки наведені дослівно; повної анкети не опубліковано. Ретроспективний заголовок не доводить дослівної сталості анкет минулих хвиль. Похибка самовідбору не охоплена заявленою формальною похибкою.'
lpool={'2026-05':'P13','2026-08':'P14','2026-09':lp}
for month in ['2026-03','2026-04','2026-06','2026-07']:lpool[month]=newpoll(month,month,'LM26','Lemur: ретроспективна хвиля '+month,org='Lemur / «Слово і діло»',priority='Додаткове: онлайн',limits=LN)
ldata=[
 ('LEMUR_TERRITORY_ACCEPT',1,'Онлайн · Прийнятність втрати підконтрольних територій','ОЦІНКА ПРИЙНЯТНОСТІ ВТРАТИ ПІДКОНТРОЛЬНИХ ТЕРИТОРІЙ УКРАЇНИ (ВИВЕДЕННЯ УКРАЇНСЬКИХ ВІЙСЬК) ЯК УМОВИ ПЕРЕМИР’Я ЗАРАДИ НЕГАЙНОГО ПРИПИНЕННЯ ВОГНЮ',['Цілком прийнятно заради якнайшвидшого закінчення війни','Прийнятно лише як вимушене «заморожування», без офіційної відмови від цих територій','Прийнятно лише за умови негайного отримання Україною членства в НАТО та вступу до ЄС','Скоріше неприйнятно, оскільки це заохотить агресора до нових нападів','Категорично неприйнятно, війна має тривати щонайменше до відновлення кордонів 2022 року','Важко відповісти'],[[15,19,7,31,18,10],[17,17,9,31,17,9],[17,17,7,32,18,9],[16,20.5,7,28,19,9.5],[15,22,7,28,19,9],[15,25,6,28.5,17,8.5],[15.5,23,5,30.5,19,7]]),
 ('LEMUR_CEASEFIRE_CONDITION',2,'Онлайн · Прийнятна і реалістична умова припинення вогню','УМОВА ПРИПИНЕННЯ ВОГНЮ, ЯКУ ВВАЖАЮТЬ НАЙБІЛЬШ ПРИЙНЯТНОЮ І РЕАЛІСТИЧНОЮ ДЛЯ УКРАЇНИ',['«Заморожування» конфлікту за фактичною лінією фронту без офіційної відмови від територій, але з наданням чітких гарантій безпеки від Заходу','Повернення до лінії розмежування станом на 23 лютого 2022 року з подальшим дипломатичним вирішенням питання Криму та ОРДЛО','Повне звільнення всіх територій до кордонів 1991 року перед початком будь-яких переговорів','Припинення вогню на будь-яких умовах, щоб зупинити загибель людей','Важко відповісти'],[[30,24.5,24,14,7.5],[28,23,23,17,9],[28,25.5,24,14,8.5],[30,23,25.5,14,7.5],[26.5,25,26.5,15,7],[33,22,24,15,6],[32,24,22,15,7]]),
 ('LEMUR_NATO_EU_SUCCESS',3,'Онлайн · Угода без НАТО: оцінка успіху','НАСКІЛЬКИ ВВАЖАТИМУТЬ УСПІХОМ УКРАЇНИ МИРНУ УГОДУ, ЯКЩО ВОНА ПЕРЕДБАЧАТИМЕ ВІДМОВУ ВІД НАТО В ОБМІН НА ВСТУП ДО ЄС ТА ДВОСТОРОННІ БЕЗПЕКОВІ СОЮЗИ',[str(i) for i in range(1,11)]+['важко відповісти'],[[6.5,2,3,3,34,3.5,6,6,4,13,19],[6,2,2,2,33.5,3,6,7,4.5,14,20],[5,2,3,2,31,5,8,6,3,17,18],[6,2,3,3,38,3,6,6,5,12,16],[7,2.5,3,2,37,3,5,6,6,13.5,15],[6,2,3,1,43,3,6,7,4,10,15],[5,2,3.5,2.5,40,5,6.5,5,4.5,11,15]]),
 ('LEMUR_TERRITORY_NATO',4,'Онлайн · Території в обмін на НАТО','РІВЕНЬ ПОГОДЖЕННЯ З ТВЕРДЖЕННЯМ: «УКРАЇНА МАЄ ЙТИ НА ТЕРИТОРІАЛЬНІ ПОСТУПКИ В ОБМІН НА ГАРАНТОВАНЕ ЧЛЕНСТВО В НАТО ТА БЕЗПЕКУ ДЛЯ МАЙБУТНІХ ПОКОЛІНЬ»',['Цілком погоджуюся','Скоріше погоджуюся','Скоріше не погоджуюся','Категорично не погоджуюся','Важко відповісти'],[[7,15,30,32,16],[8,17,29,31,15],[5.5,16,29.5,32,17],[8,13.5,28.5,36,14],[7,16,32,31,14],[5,16.5,31,35,12.5],[5,17,29,36,13]]),
 ('LEMUR_US_GUARANTEES',5,'Онлайн · Віра у виконання гарантій США','НАСКІЛЬКИ ВІРЯТЬ В ТЕ, ЩО США РЕАЛЬНО ВИКОНАЮТЬ СВОЇ БЕЗПЕКОВІ ЗОБОВ’ЯЗАННЯ У РАЗІ НОВОГО НАПАДУ РОСІЇ ПІСЛЯ ПІДПИСАННЯ УГОДИ',['Повністю вірю','Скоріше вірю','Скоріше не вірю','Зовсім не вірю','Важко відповісти'],[[2,9,34,45,10],[3,8.5,33,44,11.5],[2,9.5,35,42.5,11],[3,10,37,39,11],[2,13,35.5,38,11.5],[2,11,39,39,9],[2,11,35,44,8]])]
for sid,image,name,qtext,options,matrix in ldata:
 note=LN+(' Шкала 1–10; 1 – абсолютна поразка, 5 – ні перемога, ні поразка, 10 – безумовна перемога. 99 — код невизначеної відповіді, не бал.' if image==3 else '')
 meta(sid,name,'«Слово і діло» / Lemur · онлайн-панель',note)
 for j,vals in enumerate(matrix):
  month='2026-'+str(j+3).zfill(2);pid=lpool[month];z=instrument(sid,pid,qtext,options,'LM26I'+str(image),'Інфографіка; стовпчик '+month,{str(i):opt(i) for i in range(len(options))},basis='report' if pid==lp else 'retrospective',note=note)
  question(z,pid,'LM26I'+str(image),'Інфографіка; стовпчик '+month,name,dict(zip(z['mapping'],vals)),dimension='Мирні домовленості · онлайн',sort=month)

# Keep published regional crosses, never as separate independent national polls.
kh=BeautifulSoup((A/'sources/kiis-1643.html').read_bytes(),'html.parser')
for table in kh.find_all('table'):
 if table.find('table') is not None:continue
 text=norm(table.get_text(' ',strip=True))
 if 'Жовтень 2026 року' not in text or '100% у рядку' not in text:continue
 region='';kind='Donbas' if 'Відмова' in text else 'Endurance';answers=['Готові схвалити','Категорично проти','Важко сказати','Відмова'] if kind=='Donbas' else ['Декілька місяців-пів року','1 рік','Стільки, скільки потрібно буде','Важко сказати']
 for tr in table.find_all('tr'):
  cells=[norm(c.get_text(' ',strip=True)) for c in tr.find_all(['th','td'],recursive=False)]
  if not cells:continue
  region_label=re.sub(r'\s*\[\s*\d+\s*\]','',cells[0]).strip()
  if region_label in ['Захід','м. Київ','Центр / Північ','Південь','Нижнє Подніпров’я','Схід']:region=region_label
  if cells[0]=='Жовтень 2026 року' and region:
   vals=[int(v) for v in cells[1:]];assert len(vals)==4,(kind,cells)
   for answer,value in zip(answers,vals):d['crosses'].append(dict(poll=kp,question='Донбас в обмін на гарантії' if kind=='Donbas' else 'Готовність терпіти війну',group=region,answer=answer,pct=value/100,base='Респонденти відповідного макрорегіону; n не опубліковано',source='K1643',location='Таблиця 1' if kind=='Donbas' else 'Таблиця 2',note='Підгруповий розподіл; округлення збережено.'))
assert len([r for r in d['crosses'] if r['source']=='K1643'])==48
update['decisions']=[
 dict(source='K1643',decision='Повтор Донбасу і тривалості війни; 75% допустимості переговорів — цитата вересня, не новий жовтневий замір. Підперіоди не окремі хвилі.'),
 dict(source='K1643',decision='A1 оцінює два твердження окремо; A2 змушує обрати причину. Три окремі питання; не одні й ті самі категорії або часові ряди.'),
 dict(source='RO26P',decision='Розширено існуючий RATING_REALISTIC_END; старі дрібні категорії з RT25FP збережено. Прямі переговори додані у 04.2025; стару згоду з більшістю вимог РФ не обнулено після зникнення з графіка.'),
 dict(source='LM26',decision='П’ять додаткових онлайн-рядів; перша версія повного інструмента не відома, збережено заголовки/опції офіційної інфографіки. 99 у шкалі 1–10 не числовий результат.')]
update['primary_polls']={'kiis':kp,'rating':rp,'lemur':lp};update['kiis_package_question']=kdon
update['search']=[dict(pollster=name,url=url,result=result) for name,url,result in [
 ('КМІС','https://kiis.com.ua/?lang=ukr&cat=reports','Новий реліз 1643 від 19.10.2026; імпортовано'),('Рейтинг','https://www.ratinggroup.ua/news/socpol-oct2026','Новий реліз від 08.10.2026; імпортовано'),('ФДІ','https://dif.org.ua/category/opinion-polls','Новішої тематичної хвилі після попереднього зрізу не виявлено'),('Центр Разумкова','https://razumkov.org.ua/sotsiologiia/pres-relizy','Новішої тематичної хвилі не виявлено'),('Gallup','https://news.gallup.com/topic/country-ukr.aspx','Нова українська хвиля з теми не знайдена; опитування інших країн не підмішано'),('NDI','https://ndi.org/publications/challenges-and-opportunities-facing-ukraines-democracy','Новішої відкритої української хвилі за березень 2026 не виявлено'),('IRI','https://www.iri.org/resources/ukraine-survey-of-public-opinion-june-2026/','Новішої тематичної публікації не виявлено'),('Info Sapiens','https://www.sapiens.com.ua/ua/publications','Новішої тематичної публікації не виявлено'),('SOCIS','https://socis.kiev.ua/ua/','Новішої тематичної хвилі після зрізу не виявлено'),('Lord Ashcroft','https://lordashcroftpolls.com/','Остання знайдена тематична хвиля — травень 2026; нової немає'),('FRF','https://frf.org.ua/','Публікації 01–03.10 стосуються вже внесеної вересневої хвилі'),('Active Group','https://activegroup.com.ua/research/','Нової тематичної публікації після зрізу не виявлено'),('«Слово і діло» / Lemur',LURL,'Нова публікація від 16.10.2026; додаткові онлайн-ряди імпортовано')]]
for z in [w]:z['checked_at']=DAY;z['review']['date']=DAY;z['review']['catalogue_total']=len(d['questions'])
d['as_of']=DAY
d['coverage'].append(['Поповнення 19.10.2026','КМІС, Рейтинг, Lemur','Паспорти, повні опції, 48 регіональних перетинів і ретроспективні графіки звірено','Повтори продовжують ряди свого полстера; експеримент A1/A2, онлайн-панель та зміни опцій розрізнено','Цитовані вересневі 75% не стали жовтневою точкою; дні та n історичних замірів не домислено.'])
for file,obj in [(register,d),(R/'data/wording.json',w),(R/'data/kiis-series-audit.json',audit),(R/'data/kiis-packages.json',packages),(R/'data/update-2026-10-19.json',update)]:file.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf8')
print(update['primary_polls'],'package question',kdon)
print({k:len(d[k]) for k in ['polls','questions','dynamics','crosses','sources']},'new series',len(update['series']))
