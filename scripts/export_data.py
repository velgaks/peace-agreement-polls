"""Export a supplied research register to the public, reproducible static bundle."""
import argparse, csv, json, pathlib
from poll_dates import normalize_periods
root=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('register',type=pathlib.Path)
args=parser.parse_args()
data=json.loads(args.register.read_text(encoding='utf-8'))
for poll in data['polls']:
    if 'fieldwork_periods' in poll:
        normalize_periods(poll)
# The public bundle contains references, not local archive paths or downloaded reports.
data['sources']=[{'id':s['id'],'url':s['url']} for s in data['sources']]
for key in ['dynamics','crosses']:
    for row in data[key]:row['pct']=round(row['pct'],6)
(root/'data').mkdir(exist_ok=True)
(root/'data/research.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources={s['id']:s['url'] for s in data['sources']}
wording=json.loads((root/'data/wording.json').read_text(encoding='utf-8'))
by_question={qid:w for w in wording['items'] for qid in w['question_ids']}
for name in ['polls','questions','dynamics','crosses']:
    rows=[dict(r,source_url=sources.get(r.get('source'),'')) for r in data[name]]
    if name=='polls':
        for r in rows:
            r['date_source_url']=sources.get(r.get('date_source'),'')
            if 'fieldwork_periods' in r:
                r['fieldwork_periods']=json.dumps(r['fieldwork_periods'],ensure_ascii=False)
    if name=='questions':
        for r in rows:
            w=by_question[r['id']]
            r['scenario_summary']=r.pop('scenario')
            r['result_summary']=r.pop('result')
            for key in ['question','prompt','prompt_items','experiment_dimensions','options','instructions','statements','followups','partial_options','source_excerpt','basis','note','language','location','source_url','question_source_url','reviewed_on']:
                value=w.get(key,'')
                r['wording_'+key]=json.dumps(value,ensure_ascii=False) if isinstance(value,(list,dict)) else value
    fields=list(dict.fromkeys(k for r in rows for k in r))
    if name=='questions':
        # Put source wording in view before summaries and internal metadata.
        first=['id','poll','wording_question','wording_prompt','wording_options','wording_source_url','wording_basis']
        fields=first+[key for key in fields if key not in first]
    with (root/f'data/{name}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
print('Exported', {k:len(data[k]) for k in ['polls','questions','dynamics','crosses','sources']})
