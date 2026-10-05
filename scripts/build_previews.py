"""Generate the two README examples from the same audited data as the website."""
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
data = json.loads((ROOT / 'data/research.json').read_text('utf8'))
wording = json.loads((ROOT / 'data/wording.json').read_text('utf8'))['items']
charts = json.loads((ROOT / 'data/more-charts.json').read_text('utf8'))
INK, SECONDARY, GRID, PAPER = '#0b0b0b', '#52514e', '#e1e0d9', '#fcfcfb'
COLORS = ['#2a78d6', '#eb6834', '#898781']

def text(x, y, value, size=17, weight='400', anchor='start', color=INK):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{escape(str(value))}</text>'

def paragraph(value, y, width=95, size=17, color=SECONDARY):
    parts = []
    for line in wrap(value, width, break_long_words=False, break_on_hyphens=False):
        parts.append(text(40, y, line, size, color=color))
        y += size * 1.45
    return ''.join(parts), y

def finish(filename, title, description, content, height):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc><rect width="100%" height="100%" fill="{PAPER}"/><g font-family="&quot;Source Sans 3&quot;, &quot;Trebuchet MS&quot;, sans-serif">{content}</g></svg>\n'
    (OUT / filename).write_text(svg, 'utf8')

def credit(y, note, source, url):
    body, y = paragraph(note, y, size=13, width=125)
    body += text(40, y + 6, 'Графік: Valentyn Hatsko, TG: @gorbach_squad.', 13, '600')
    body += f'<a href="{escape(url, quote=True)}">{text(40, y + 26, "Джерело: " + source, 13, color=SECONDARY)}</a>'
    body += text(40, y + 46, 'Дані, код і метод: github.com/velgaks/peace-agreement-polls', 13, color=SECONDARY)
    return body, round(y + 70)

# All eight waves and all three published response categories.
sid = 'RATING_DIRECT_TALKS'
rows = [r for r in data['dynamics'] if r['series'] == sid]
w = next(w for w in wording if w['series'] == sid)
title = 'Підтримка прямих переговорів зросла з 38% до 64%'
body = text(40, 43, title, 27, '600')
part, y = paragraph(w['question'], 78)
body += part + text(40, y + 2, '«Рейтинг» · січень 2024 — лютий 2025', 14, color=SECONDARY)
keys = ['Підтримують', 'Не підтримують', 'Не визначилися']
for i, key in enumerate(keys):
    x = 40 + i * 260
    body += f'<line x1="{x}" x2="{x+24}" y1="{y+30}" y2="{y+30}" stroke="{COLORS[i]}" stroke-width="3" stroke-dasharray="{["", "8 4", "3 4"][i]}"/>'
    body += text(x + 33, y + 35, w['options'][w['mapping'][key]['indices'][0]], 16)
top, bottom, left, right = y + 62, y + 332, 82, 854
date = lambda s: datetime.strptime(s, '%Y-%m').replace(tzinfo=timezone.utc).timestamp()
dates = sorted({r['sort'] for r in rows})
start, end = date(dates[0]), date(dates[-1])
xpos = lambda s: left + (date(s) - start) / (end - start) * (right - left)
ypos = lambda p: bottom - p * (bottom - top)
for value in [0, .25, .5, .75, 1]:
    yy = ypos(value)
    body += f'<line x1="{left}" x2="{right}" y1="{yy}" y2="{yy}" stroke="{GRID}"/>'
    body += text(left - 12, yy + 5, f'{round(value*100)}%', 14, anchor='end', color=SECONDARY)
for i, key in enumerate(keys):
    rs = sorted((r for r in rows if r['answer'] == key), key=lambda r:r['sort'])
    points = ' '.join(f'{xpos(r["sort"]):.2f},{ypos(r["pct"]):.2f}' for r in rs)
    body += f'<polyline points="{points}" fill="none" stroke="{COLORS[i]}" stroke-width="2.5" stroke-dasharray="{["", "8 4", "3 4"][i]}"/>'
    for r in rs:
        body += f'<circle cx="{xpos(r["sort"])}" cy="{ypos(r["pct"])}" r="4.5" fill="{COLORS[i]}" stroke="{PAPER}" stroke-width="1.5"/>'
    body += text(right + 14, ypos(rs[-1]['pct']) + 5, f'{round(rs[-1]["pct"]*100)}%', 18, '600')
for d, label in [('2024-01','січ. 2024'), ('2024-06','черв. 2024'), ('2024-10','жовт. 2024'), ('2025-02','лют. 2025')]:
    body += text(xpos(d), bottom + 28, label, 14, anchor='middle', color=SECONDARY)
foot, height = credit(bottom + 63, 'Питання й опції — з ретроспективного графіка звіту; лінії з’єднують заміри.', '«Рейтинг», PDF, с. 19; зібрано у жовтні 2026.', w['source_url'])
finish('negotiations-trend.svg', title, w['question'], body + foot, height)

# Complete published distribution; no residuals or regrouping of rounded values.
w = next(w for w in wording if 'Q13' in w['question_ids'])
plot = charts['questions']['Q13']['plots'][0]
title = '55% повністю не приймають визнання територій Росії'
body = text(40, 43, title, 27, '600')
part, y = paragraph(w['question'], 78)
body += part
part, y = paragraph(w['prompt'], y + 4, color=INK)
body += part + text(40, y + 5, 'NDI / КМІС · 3–28 березня 2026', 14, color=SECONDARY)
top, left, right = y + 47, 300, 870
for v in [0, 25, 50, 75, 100]:
    xx = left + v / 100 * (right - left)
    body += text(xx, top - 11, f'{v}%', 13, anchor='middle', color=SECONDARY)
for i, row in enumerate(plot['rows']):
    yy = top + i * 52
    body += text(40, yy + 19, row['label'], 17)
    length = row['value'] / 100 * (right - left)
    body += f'<rect x="{left}" y="{yy}" width="{length}" height="25" fill="{COLORS[0]}"/>'
    body += text(left + length + 10, yy + 19, f'{row["value"]}%', 18, '600')
foot, height = credit(top + 52 * 5 + 23, 'Округлені частки всіх опублікованих категорій; питання та опції відтворено дослівно.', 'NDI / КМІС, PDF, с. 21; зібрано у жовтні 2026.', w['source_url'])
finish('territory-recognition.svg', title, w['question'] + ' ' + w['prompt'], body + foot, height)
print('Generated two README charts from audited JSON.')
