"""Compare reported findings by stable Key, without inferring that absent issues are fixed.

Reads two validated reports and writes a Markdown review aid to stdout. No repository
commands, remote calls or file writes. Exit 2 means scopes/identity cannot be compared.
"""
import argparse
import sys
from pathlib import Path

from validate_report import check_report, field, records, sections, strip_fences


def identity(value):
    return ' '.join((value or '').split()).rstrip('/')


def read_report(path):
    text = path.read_text(encoding='utf-8')
    errors, _ = check_report(text)
    if errors:
        raise ValueError(str(path) + ': ' + '; '.join(errors))
    body = dict(sections(strip_fences(text)))
    scope = body['Scope and limits']
    found = {}
    for fid, record in records(body['What to improve'], 'F'):
        key = field(record, 'Key')
        if not key:
            raise ValueError(str(path) + ': ' + fid + ' has no stable Key; map legacy findings manually.')
        if key in found:
            raise ValueError(str(path) + ': duplicate finding Key ' + key)
        found[key] = fid
    return dict(repository=identity(field(scope, 'Repository')), scope=identity(field(scope, 'Scope')),
                revision=field(scope, 'Revision') or 'Unspecified', findings=found)


def cell(value):
    return value.replace('|', r'\|').replace('\n', ' ')


def compare(previous, current):
    for label in ('repository', 'scope'):
        if not previous[label] or previous[label] != current[label]:
            raise ValueError('Reports have missing or different ' + label +
                             '; compare scope and map findings manually. No closure can be inferred.')
    lines = ['# Reassessment review aid', '',
             'This compares what two reports say. It does not verify repairs or their introduction dates.', '',
             '**Previous revision:** ' + cell(previous['revision']),
             '**Current revision:** ' + cell(current['revision']), '',
             '| Key | Previous | Current | Review status |', '|---|---|---|---|']
    old, new = previous['findings'], current['findings']
    for key in sorted(set(old) | set(new)):
        status = ('Still reported; review current evidence' if key in old and key in new else
                  'Not rechecked; absence is not proof of a fix' if key in old else
                  'Newly reported; introduction date unknown')
        lines.append('| ' + ' | '.join(map(cell, (key, old.get(key, '—'), new.get(key, '—'), status))) + ' |')
    if not old and not new:
        lines += ['', 'Neither report lists findings. This does not establish unchanged repository behavior.']
    lines += ['', 'Mark a prior finding Fixed only after its closure check succeeds on the current revision. '
              'Keep omitted or out-of-scope findings Not rechecked, with the reason.']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('previous', type=Path)
    parser.add_argument('current', type=Path)
    args = parser.parse_args(argv)
    try:
        print(compare(read_report(args.previous), read_report(args.current)), end='')
    except (OSError, UnicodeError, ValueError) as exc:
        print('Cannot compare: ' + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
