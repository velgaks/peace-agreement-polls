"""Export a supplied research register to the public, reproducible static bundle."""
import argparse, csv, json, pathlib
root=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('register',type=pathlib.Path)
args=parser.parse_args()
data=json.loads(args.register.read_text(encoding='utf-8'))
# The public bundle contains references, not local archive paths or downloaded reports.
data['sources']=[{'id':s['id'],'url':s['url']} for s in data['sources']]
for key in ['dynamics','crosses']:
    for row in data[key]:row['pct']=round(row['pct'],6)
(root/'data').mkdir(exist_ok=True)
(root/'data/research.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources={s['id']:s['url'] for s in data['sources']}
for name in ['polls','questions','dynamics','crosses']:
    rows=[dict(r,source_url=sources.get(r.get('source'),'')) for r in data[name]]
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (root/f'data/{name}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
print('Exported', {k:len(data[k]) for k in ['polls','questions','dynamics','crosses','sources']})
