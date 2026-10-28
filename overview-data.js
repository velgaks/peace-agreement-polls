import {waves} from './lib.js';
import {wordingKey} from './wording.js';

// These labels are editorial summaries. The overview also displays the source
// option verbatim, and links to the full question, distribution and methodology.
export const OVERVIEW_INDICATORS = [
  {
    series: 'GALLUP_NEGOTIATIONS',
    answer: 'Переговори для завершення війни якнайшвидше',
    label: 'Переговори для якнайшвидшого завершення війни'
  },
  {
    series: 'KIIS_TERRITORY_GENERAL',
    answer: 'Відкидають будь-які територіальні поступки',
    label: 'Відмова від будь-яких територіальних поступок'
  },
  {
    series: 'KIIS_WAR_ENDURANCE',
    answer: 'Стільки, скільки потрібно',
    label: 'Готовність терпіти війну стільки, скільки потрібно'
  },
  {
    series: 'KIIS_DONBAS_GUARANTEES_2026',
    answer: 'Категорично відкидають',
    label: 'Відкидання передачі Донбасу за гарантії безпеки'
  }
];

export const OVERVIEW_CHARTS = [
  'GALLUP_NEGOTIATIONS',
  'KIIS_TERRITORY_GENERAL',
  'KIIS_WAR_ENDURANCE',
  'KIIS_DONBAS_GUARANTEES_2026',
  'RATING_REALISTIC_END',
  'RATING_PEACE_OR_VICTORY'
];

const lookup = (records, id) => records instanceof Map ? records.get(id)
  : Array.isArray(records) ? records.find(record => record.id === id) : records?.[id];
const rowFor = (wave, answer) => wave?.rows.find(row => row.answer === answer) ?? null;
const valueFor = row => typeof row?.pct === 'number' && Number.isFinite(row.pct)
  && row.pct >= 0 && row.pct <= 1 ? row.pct : null;
const normalize = value => typeof value === 'string' ? value.replace(/\s+/g, ' ').trim()
  : Array.isArray(value) ? value.map(normalize)
  : value && typeof value === 'object'
    ? Object.fromEntries(Object.keys(value).sort().map(key => [key, normalize(value[key])]))
    : value;
const wordingFields = ['question', 'prompt', 'prompt_items', 'options', 'instructions',
  'statements', 'followups', 'experiment_dimensions', 'mapping'];

/**
 * Latest and preceding measurements within one instrument. Values retain the
 * registry's 0–1 units; change is in percentage points. A missing answer in
 * either of those two waves stays missing: older available answers never stand
 * in for the preceding measurement. Dates are returned exactly as registered.
 */
export function latestIndicator(config, dynamics, {polls = [], sources = [], wordingIndex} = {}) {
  const seriesWaves = waves(dynamics.filter(row => row.series === config.series));
  const latest = seriesWaves.at(-1) ?? null;
  const previous = seriesWaves.at(-2) ?? null;
  const latestRow = rowFor(latest, config.answer);
  const previousRow = rowFor(previous, config.answer);
  const value = valueFor(latestRow);
  const previousValue = valueFor(previousRow);
  const poll = lookup(polls, latest?.poll) ?? null;
  const previousPoll = lookup(polls, previous?.poll) ?? null;
  const wording = latest ? wordingIndex?.byWave.get(wordingKey(config.series, latest.poll)) ?? null : null;
  const previousWording = previous ? wordingIndex?.byWave.get(wordingKey(config.series, previous.poll)) ?? null : null;
  // The canonical series already separates pollsters; also guard against an
  // accidental mixed-pollster addition when its poll metadata is available.
  const samePollster = !(poll?.pollster && previousPoll?.pollster)
    || poll.pollster === previousPoll.pollster;
  const change = value !== null && previousValue !== null && samePollster
    ? Math.round((value - previousValue) * 100 * 1e10) / 1e10 : null;
  const wordingChanges = wording && previousWording ? wordingFields.filter(key =>
    JSON.stringify(normalize(wording[key] ?? null)) !== JSON.stringify(normalize(previousWording[key] ?? null))) : null;
  const latestSource = latestRow?.source ?? latest?.rows[0]?.source;
  const previousSource = previousRow?.source ?? previous?.rows[0]?.source;

  return {
    ...config,
    waves: seriesWaves,
    latest,
    previous,
    latestRow,
    previousRow,
    value,
    previousValue,
    change,
    samePollster,
    poll,
    previousPoll,
    source: lookup(sources, latestSource) ?? null,
    previousSource: lookup(sources, previousSource) ?? null,
    wording,
    previousWording,
    wordingChanges,
    wordingChanged: wordingChanges === null ? null : wordingChanges.length > 0
  };
}
