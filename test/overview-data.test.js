import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {OVERVIEW_INDICATORS, OVERVIEW_CHARTS, latestIndicator} from '../overview-data.js';
import {SERIES} from '../series.js';
import {indexWording} from '../wording.js';

const read = name => JSON.parse(fs.readFileSync(new URL('../data/' + name, import.meta.url), 'utf8'));
const data = read('research.json');
const wordingIndex = indexWording([...read('wording.json').items, ...read('more-charts.json').wording]);
const context = {polls: data.polls, sources: data.sources, wordingIndex};
const config = {series: 'instrument', answer: 'yes', label: 'Summary'};
const row = (poll, sort, answer, pct, series = 'instrument') => ({poll, sort, answer, pct, series});

test('Overview selection has four distinct headline topics and six primary-source charts', () => {
  assert.equal(OVERVIEW_INDICATORS.length, 4);
  assert.equal(OVERVIEW_CHARTS.length, 6);
  assert.equal(new Set(OVERVIEW_CHARTS).size, 6);
  for (const id of OVERVIEW_CHARTS) {
    assert(SERIES.some(series => series.id === id));
    const result = latestIndicator({series: id, answer: ''}, data.dynamics, context);
    assert(result.poll.priority.startsWith('Основне'));
    assert(result.waves.length >= 2);
  }
  assert(OVERVIEW_INDICATORS.every(indicator => OVERVIEW_CHARTS.includes(indicator.series)));
});

test('Headline figures use the latest wave and immediately preceding measurement, with source and exact dates', () => {
  const results = OVERVIEW_INDICATORS.map(config => latestIndicator(config, data.dynamics, context));
  assert.deepEqual(results.map(result => [result.series, result.value, result.previousValue, result.change]), [
    ['GALLUP_NEGOTIATIONS', .66, .69, -3],
    ['KIIS_TERRITORY_GENERAL', .53, .54, -1],
    ['KIIS_WAR_ENDURANCE', .62, .62, 0],
    ['KIIS_DONBAS_GUARANTEES_2026', .61, .60, 1]
  ]);
  for (const result of results) {
    assert.equal(result.poll.id, result.latest.poll);
    assert.equal(result.previousPoll.id, result.previous.poll);
    assert.equal(result.source.id, result.latestRow.source);
    assert.equal(result.previousSource.id, result.previousRow.source);
    assert(result.wording);
    assert(result.previousWording);
    assert(result.samePollster);
  }
  assert.equal(results[0].poll.date_precision, 'month');
  assert.equal(results[0].poll.period, '04.2026');
  assert.equal(results[3].poll.period, '08.10.2026–16.10.2026');
});

test('Missing latest or preceding answer never falls back to an older answer or zero', () => {
  const older = row('old', '2025-01', 'yes', .2);
  const latestMissing = latestIndicator(config, [older, row('new', '2026-01', 'no', .6)]);
  assert.equal(latestMissing.value, null);
  assert.equal(latestMissing.change, null);
  assert.equal(latestMissing.latest.poll, 'new');
  const precedingMissing = latestIndicator(config, [row('new', '2026-03', 'yes', .4), older, row('middle', '2026-01', 'no', .6)]);
  assert.equal(precedingMissing.value, .4);
  assert.equal(precedingMissing.previousValue, null);
  assert.equal(precedingMissing.change, null);
  assert.equal(precedingMissing.previous.poll, 'middle');
});

test('Null, blank, nonnumeric and invalid values stay missing; real zero is retained', () => {
  for (const value of [null, undefined, '', '.2', NaN, Infinity, -.1, 1.1]) {
    const result = latestIndicator(config, [row('a', '2025', 'yes', .2), row('b', '2026', 'yes', value)]);
    assert.equal(result.value, null);
    assert.equal(result.change, null);
  }
  const result = latestIndicator(config, [row('a', '2025', 'yes', .037), row('b', '2026', 'yes', 0)]);
  assert.equal(result.value, 0);
  assert.equal(result.change, -3.7);
});

test('Measurements from another series or pollster never contribute to the delta', () => {
  const rows = [row('a', '2025', 'yes', .2), row('b', '2026', 'yes', .4), row('c', '2027', 'yes', .8, 'other')];
  const result = latestIndicator(config, rows);
  assert.equal(result.value, .4);
  assert.equal(result.change, 20);
  const mixed = latestIndicator(config, rows, {polls: [{id: 'a', pollster: 'One'}, {id: 'b', pollster: 'Two'}]});
  assert.equal(mixed.samePollster, false);
  assert.equal(mixed.change, null);
});

test('Two waves within the same month remain separate and input order is unchanged', () => {
  const rows = [row('b', '2026-01-23', 'yes', .35), row('a', '2026-01-09', 'yes', .4)];
  const copy = structuredClone(rows);
  const result = latestIndicator(config, rows);
  assert.equal(result.latest.poll, 'b');
  assert.equal(result.previous.poll, 'a');
  assert.equal(result.change, -5);
  assert.deepEqual(rows, copy);
});

test('No prior measurement means no change, while dates retain their original precision', () => {
  const result = latestIndicator(config, [row('a', '2026-01', 'yes', .2)]);
  assert.equal(result.change, null);
  assert.equal(result.previous, null);
  assert.equal(result.latest.sort, '2026-01');
  const empty = latestIndicator(config, []);
  assert.equal(empty.value, null);
  assert.equal(empty.change, null);
  assert.equal(empty.latest, null);
});

test('Wording changes preserve source text and distinguish missing evidence from unchanged evidence', () => {
  const rows = [row('a', '2025', 'yes', .2), row('b', '2026', 'yes', .4)];
  const item = (poll, question, options = ['Yes', 'No']) => ({series: 'instrument', polls: [poll], question, options});
  const unchanged = latestIndicator(config, rows, {wordingIndex: indexWording([item('a', '  Exact\n question?'), item('b', 'Exact question?')])});
  assert.equal(unchanged.wordingChanged, false);
  const changed = latestIndicator(config, rows, {wordingIndex: indexWording([item('a', 'Exact question?'), item('b', 'Exact Question?', ['Yes', 'No', 'Maybe'])])});
  assert.equal(changed.wordingChanged, true);
  assert.deepEqual(changed.wordingChanges, ['question', 'options']);
  assert.equal(changed.wording.question, 'Exact Question?');
  assert.equal(latestIndicator(config, rows).wordingChanged, null);
});
