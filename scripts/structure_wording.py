"""Recover questionnaire boundaries and lists from archived publisher HTML.

Usage: python scripts/structure_wording.py /path/to/peace-agreement-polls-archive
"""
import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
norm = lambda value: ' '.join(value.split())

def structure(archive):
    archive = Path(archive)
    registry = json.loads((archive / '_work/research-data.json').read_text('utf8'))
    sources = {s['id']: s for s in registry['sources']}
    document = json.loads((ROOT / 'data/wording.json').read_text('utf8'))
    items = document['items']
    by_question = {qid: w for w in items for qid in w['question_ids']}

    def html(sid):
        return BeautifulSoup((archive / 'sources' / sources[sid]['file']).read_bytes(), 'html.parser')

    # Read the questionnaire cell itself, never the first mention in article prose.
    candidates = []
    for table in html('K2').find_all('table'):
        if table.find('table'):
            continue
        for row in table.find_all('tr'):
            cells = [norm(c.get_text(' ', strip=True)) for c in row.find_all(['td', 'th'], recursive=False)]
            if len(cells) == 6 and cells[0].startswith('Вогонь припиняється') and cells[1:] == ['1','2','3','4','5']:
                candidates.append(cells[0])
    assert len(candidates) == 1, candidates
    by_question['Q05'].update(prompt=candidates[0], location='Додаток 1. Формулювання запитань з анкети', reviewed_on='2026-10-06')

    # Each row is a dimension, each populated cell a level, not one giant prompt.
    matrices = []
    for table in html('K25A').find_all('table'):
        if table.find('table'):
            continue
        rows = [[norm(c.get_text(' ', strip=True)) for c in row.find_all(['td', 'th'], recursive=False)] for row in table.find_all('tr')]
        if rows and rows[0] == ['Назва виміру', 'Рівень 1', 'Рівень 2', 'Рівень 3', 'Рівень 4']:
            matrices.append([{'name': row[0], 'levels': [c for c in row[1:] if c]} for row in rows[1:]])
    assert len(matrices) == 1
    assert [len(d['levels']) for d in matrices[0]] == [4, 2, 3, 2, 2]
    by_question['Q25'].update(prompt='', experiment_dimensions=matrices[0], location='Додаток 1. Формулювання запитань з анкети', reviewed_on='2026-10-06')

    # Restore bullet boundaries only where their concatenation exactly matches
    # the already audited prompt. Never guess sentence/paragraph boundaries.
    lists_by_url = {}
    for sid in ['K1421', 'K1530', 'K1543', 'K1551', 'K1572']:
        lists_by_url[sources[sid]['url']] = [[norm(li.get_text(' ', strip=True)) for li in ul.find_all('li', recursive=False)] for ul in html(sid).find_all(['ul','ol'])]
    restored = []
    for w in items:
        for parts in lists_by_url.get(w['source_url'], []):
            if len(parts) > 1 and norm(' '.join(parts)) == norm(w.get('prompt', '')):
                w['prompt_items'] = parts
                restored.append(w['id'])
                break
    (ROOT / 'data/wording.json').write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print('Repaired Q05; structured Q25 (5 dimensions, 13 levels); restored lists:', len(restored))

if __name__ == '__main__':
    structure(sys.argv[1])
