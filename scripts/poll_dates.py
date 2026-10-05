"""Preserve published date precision; never turn a month into invented days."""
import datetime
import re


def validate_date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}(?:-\d{2})?', value):
        raise ValueError(f'Expected ISO day or month, got {value!r}')
    datetime.date.fromisoformat(value if len(value) == 10 else value + '-01')
    return value


def display_date(value):
    return '.'.join(reversed(validate_date(value).split('-')))


def normalize_periods(poll):
    periods = poll['fieldwork_periods']
    if not periods:
        raise ValueError(f"{poll['id']}: missing fieldwork period")
    labels = []
    previous_end = None
    for period in periods:
        start, end = validate_date(period['start']), validate_date(period['end'])
        if len(start) != len(end) or start > end:
            raise ValueError(f"{poll['id']}: inconsistent interval {period}")
        start_day = datetime.date.fromisoformat(start if len(start) == 10 else start + '-01')
        if previous_end is not None and start_day <= previous_end:
            raise ValueError(f"{poll['id']}: overlapping or unordered intervals")
        if len(end) == 10:
            previous_end = datetime.date.fromisoformat(end)
        else:
            year, month = map(int, end.split('-'))
            previous_end = datetime.date(year + (month == 12), month % 12 + 1, 1) - datetime.timedelta(days=1)
        labels.append(display_date(start) if start == end else f'{display_date(start)}–{display_date(end)}')
    # Outer bounds are for filtering only. The intervals remain authoritative,
    # notably for an aggregate of noncontiguous waves such as Gallup 2024.
    poll['start'] = periods[0]['start']
    poll['end'] = periods[-1]['end']
    poll['period'] = '; '.join(labels)
    lengths = {len(p[k]) for p in periods for k in ['start', 'end']}
    poll['date_precision'] = 'mixed' if len(lengths) > 1 else ('day' if lengths == {10} else 'month')
    poll['date_kind'] = 'aggregate' if len(periods) > 1 else 'single_wave'

