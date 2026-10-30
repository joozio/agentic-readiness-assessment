"""Check a v5 human report using only Python's standard library.

This checks shape and internal consistency, not the truth of claimed evidence.
No files are changed. Return 1 for errors, 0 for a valid report (including warnings).
"""
import argparse
import re
import sys
from pathlib import Path

SECTIONS = ('TL:TR', 'Readiness checks', 'What to improve', 'What already works',
            'Scope and limits', 'Evidence')
CHECKS = ('Setup', 'Deliverable', 'Primary checks', 'Probe')
VERDICTS = ('Ready for bounded changes', 'Needs improvements', 'Blocked', 'Inconclusive')
STATES = ('Passed', 'Gap', 'Unverified', 'N/A')
KINDS = ('Executed', 'CI', 'Inspected', 'Not run')
TASK_STATES = ('Supported', 'Conditional', 'Unverified', 'Blocked')


def field(body, label):
    matches = re.findall(r'^\*\*' + re.escape(label) + r':\*\*[ \t]*([^\n]*)$', body, re.M)
    return (matches[0].strip() or None) if len(matches) == 1 else None


def refs(text, prefix):
    return set(re.findall(r'\b' + prefix + r'\d{2,}\b', text))


def sections(text):
    matches = list(re.finditer(r'^## (.+?)\s*$', text, re.M))
    return [(m[1], text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)])
            for i, m in enumerate(matches)]


def records(body, prefix):
    matches = list(re.finditer(r'^### (' + prefix + r'\d{2,})[ \t]+[—–-][ \t]+\S.*$', body, re.M))
    return [(m[1], body[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(body)])
            for i, m in enumerate(matches)]


def strip_fences(text):
    # Fenced examples/logs are not report metadata or declarations.
    return re.sub(r'^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$', '', text, flags=re.M | re.S)


def check_report(text):
    errors, warnings = [], []
    text = text[1:] if text.startswith('\ufeff') else text  # UTF-8 BOM from some editors
    clean = strip_fences(text)
    parts = sections(clean)
    if tuple(name for name, _ in parts) != SECTIONS:
        errors.append('Use the six report sections in order, starting with ## TL:TR.')
        return errors, warnings
    body = dict(parts)
    if not re.search(r'^# \S', clean, re.M):
        errors.append('Missing descriptive report title.')
    verdict = field(body['TL:TR'], 'Verdict')
    confidence = field(body['TL:TR'], 'Confidence')
    if verdict not in VERDICTS:
        errors.append('Missing, duplicate or invalid Verdict.')
    if confidence not in ('High', 'Medium', 'Low'):
        errors.append('Missing, duplicate or invalid Confidence.')
    scope = body['Scope and limits']
    for label in ('Scope', 'Coverage', 'Mode', 'Revision', 'Skill version'):
        if field(scope, label) is None:
            errors.append('Missing or duplicate scope field: ' + label)
    if field(scope, 'Coverage') not in ('Full', 'Partial'):
        errors.append('Coverage must be Full or Partial.')
    if field(scope, 'Mode') not in ('Executed', 'Read-only'):
        errors.append('Mode must be Executed or Read-only.')
    version = re.fullmatch(r'5\.(\d+)\.\d+(?:[-+][\w.-]+)?', field(scope, 'Skill version') or '')
    if not version:
        errors.append('Skill version must identify the v5 contract.')
    extended = bool(version and int(version[1]) >= 1)
    if extended:
        if not field(scope, 'Repository'):
            errors.append('Missing or duplicate scope field: Repository')
        if not field(body['TL:TR'], 'Delegation'):
            errors.append('TL:TR needs one task-specific Delegation field.')

    evidence_list = records(body['Evidence'], 'E')
    finding_list = records(body['What to improve'], 'F')
    for label, items in (('evidence', evidence_list), ('finding', finding_list)):
        ids = [key for key, _ in items]
        if len(ids) != len(set(ids)):
            errors.append('Duplicate ' + label + ' IDs.')
    evidence = dict(evidence_list)
    findings = dict(finding_list)
    if not evidence:
        errors.append('At least one evidence record is required, including for read-only audits.')
    kinds = {}
    for key, record in evidence.items():
        kinds[key] = field(record, 'Kind')
        if kinds[key] not in KINDS:
            errors.append(key + ': missing, duplicate or invalid evidence Kind.')
        if len(record.split()) < 8:
            errors.append(key + ': describe the observation, not only its Kind.')
    for prefix, declared in (('E', evidence), ('F', findings)):
        for key in sorted(refs(clean, prefix) - set(declared)):
            errors.append('Undefined reference: ' + key)

    stable_keys = set()
    for key, record in findings.items():
        for label in ('Priority', 'Owner', 'Why', 'Evidence', 'Change', 'Verify'):
            if field(record, label) is None:
                errors.append(key + ': missing or duplicate field ' + label)
        if field(record, 'Priority') not in ('P1', 'P2', 'P3'):
            errors.append(key + ': Priority must be P1, P2 or P3.')
        if field(record, 'Owner') not in ('Repo', 'Environment', 'External'):
            errors.append(key + ': invalid Owner.')
        if not refs(field(record, 'Evidence') or '', 'E'):
            errors.append(key + ': Evidence needs an E ID.')
        if extended:
            for label in ('Key', 'Basis', 'Task', 'Effort'):
                if not field(record, label):
                    errors.append(key + ': missing or duplicate field ' + label)
            stable_key = field(record, 'Key') or ''
            if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', stable_key):
                errors.append(key + ': Key must be a lowercase hyphenated problem slug.')
            if stable_key in stable_keys:
                errors.append(key + ': duplicate stable Key.')
            stable_keys.add(stable_key)
            basis = field(record, 'Basis')
            if basis not in ('Demonstrated', 'Inspected', 'Hypothesis'):
                errors.append(key + ': Basis must be Demonstrated, Inspected or Hypothesis.')
            if field(record, 'Effort') not in ('Small', 'Medium', 'Large', 'Unknown'):
                errors.append(key + ': Effort must be Small, Medium, Large or Unknown.')
            if basis == 'Demonstrated' and not any(kinds.get(k) in ('Executed', 'CI')
                    for k in refs(field(record, 'Evidence') or '', 'E')):
                errors.append(key + ': Demonstrated failure needs Executed or CI evidence.')
            if basis == 'Hypothesis' and field(record, 'Priority') != 'P3':
                errors.append(key + ': Hypothesis is an investigation, requiring P3.')
            if basis == 'Inspected' and field(record, 'Priority') == 'P1':
                warnings.append(key + ': review the high-consequence causal chain and existing controls for inspected P1.')

    rows = {}
    for line in body['Readiness checks'].splitlines():
        if not line.startswith('|'):
            continue
        cells = [s.strip() for s in re.split(r'(?<!\\)\|', line)[1:-1]]
        if cells and cells[0] in CHECKS:
            if cells[0] in rows:
                errors.append('Duplicate readiness row: ' + cells[0])
            rows[cells[0]] = cells
    for name in CHECKS:
        row = rows.get(name, [])
        if len(row) != 3 or row[1] not in STATES:
            errors.append(name + ': expected a three-column check row with a valid State.')
            continue
        linked = refs(row[2], 'E')
        if not linked:
            errors.append(name + ': readiness row needs an evidence reference.')
        if row[1] == 'Passed' and not any(kinds.get(key) in ('Executed', 'CI') for key in linked):
            errors.append(name + ': Passed needs executed or exact-revision CI evidence.')
        if row[1] == 'Gap' and not any(field(findings.get(k, ''), 'Owner') == 'Repo'
                                     and (not extended or field(findings.get(k, ''), 'Basis') != 'Hypothesis')
                                     for k in refs(row[2], 'F')):
            errors.append(name + ': Gap must name a Repo finding ID, not a host limitation.')
        if row[1] == 'N/A' and name not in ('Setup', 'Deliverable'):
            errors.append(name + ': use Unverified rather than N/A.')
    states = {name: row[1] for name, row in rows.items() if len(row) == 3}
    substantive = [r for r in findings.values() if field(r, 'Owner') in ('Repo', 'External')
                   and (not extended or field(r, 'Basis') != 'Hypothesis')]
    p1 = any(field(r, 'Priority') == 'P1' for r in substantive)
    repo_gap = any(field(r, 'Owner') == 'Repo' for r in findings.values())
    known_gap = 'Gap' in states.values() or bool(substantive)
    if verdict == 'Ready for bounded changes':
        if len(states) != 4 or any(s not in ('Passed', 'N/A') for s in states.values()):
            errors.append('Ready requires all four checks Passed (justified setup/deliverable N/A allowed).')
        if p1 or confidence == 'Low' or field(scope, 'Coverage') != 'Full':
            errors.append('Ready requires full declared coverage, High/Medium confidence and no Repo/External P1.')
    if verdict == 'Blocked' and (not repo_gap or not any(states.get(k) == 'Gap' for k in CHECKS[:3])):
        errors.append('Blocked requires a Repo finding and a setup/deliverable/primary-check Gap.')
    if verdict == 'Needs improvements' and not known_gap:
        errors.append('Needs improvements requires a verified Repo/External gap, not host limitations alone.')
    if verdict == 'Inconclusive' and ('Gap' in states.values() or p1):
        errors.append('A demonstrated readiness Gap or Repo/External P1 needs a negative verdict.')
    if field(scope, 'Mode') == 'Read-only' and 'Executed' in kinds.values():
        errors.append('Read-only mode cannot contain Executed assessment evidence.')
    if confidence == 'High' and (field(scope, 'Coverage') == 'Partial' or states.get('Primary checks') == 'Unverified'):
        errors.append('High confidence conflicts with partial coverage or unverified primary checks.')
    if extended:
        tasks = []
        in_tasks = False
        for line in body['Readiness checks'].splitlines():
            if not line.startswith('|'):
                in_tasks = False
                continue
            cells = [s.strip() for s in re.split(r'(?<!\\)\|', line)[1:-1]]
            if cells == ['Change task', 'State', 'Boundary and evidence']:
                in_tasks = True
                continue
            if in_tasks and not all(re.fullmatch(r':?-+:?', cell) for cell in cells):
                tasks.append(cells)
        if not tasks:
            errors.append('Add the Change task / State / Boundary and evidence table.')
        names = set()
        for row in tasks:
            if len(row) != 3 or row[1] not in TASK_STATES or not row[0]:
                errors.append('Each change task needs three columns and a valid task State.')
                continue
            name, state, boundary = row
            if name in names:
                errors.append('Duplicate change task: ' + name)
            names.add(name)
            linked = refs(boundary, 'E')
            if not linked:
                errors.append(name + ': task boundary needs an evidence reference.')
            executed = any(kinds.get(k) in ('Executed', 'CI') for k in linked)
            if state in ('Supported', 'Blocked') and not executed:
                errors.append(name + ': ' + state + ' needs Executed or CI evidence.')
            if state == 'Blocked' and not any(field(findings.get(k, ''), 'Owner') == 'Repo'
                    and field(findings.get(k, ''), 'Basis') == 'Demonstrated' for k in refs(boundary, 'F')):
                errors.append(name + ': Blocked task must name a Demonstrated Repo finding.')
        if verdict == 'Ready for bounded changes' and any(len(r) != 3 or r[1] != 'Supported' for r in tasks):
            errors.append('Ready requires every assessed change task Supported.')
        if verdict == 'Blocked' and any(len(r) != 3 or r[1] != 'Blocked' for r in tasks):
            errors.append('Blocked requires every assessed change task Blocked; preserve useful paths with Needs improvements.')
    for line in clean.splitlines():
        if line.startswith('|'):
            columns = re.split(r'(?<!\\)\|', line)[1:-1]
            if not line.endswith('|') or len(columns) > 5:
                errors.append('Malformed or oversized table row; use at most five columns.')
                break
    if len(body['TL:TR'].split()) > 180:
        warnings.append('TL:TR exceeds 180 words; shorten the decision summary.')
    if len(text.split()) > 1400:
        warnings.append('Report exceeds 1,400 words; consider removing repetition or linking long logs.')
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args(argv)
    try:
        text = args.report.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        print('Cannot read report: ' + str(exc), file=sys.stderr)
        return 1
    errors, warnings = check_report(text)
    for message in warnings:
        print('Warning: ' + message, file=sys.stderr)
    for message in errors:
        print('Error: ' + message, file=sys.stderr)
    if not errors:
        print('Report structure and consistency: valid. Evidence truth requires human review.')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
