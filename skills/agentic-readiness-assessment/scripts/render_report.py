"""Render an agentic-readiness Markdown report as a self-contained HTML file.

Markdown remains the canonical report.  This optional, standard-library renderer
implements a deliberately small subset and keeps unfamiliar input as visible text.
PDF output is opt-in and uses an already-installed WeasyPrint package.
"""
import argparse
import html
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_ITEM = re.compile(r"^\s*([-+*]|\d+[.)])\s+(.+)$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
FIELD = re.compile(r"^\*\*[^*:\n]+:\*\*\s*")
TABLE_RULE = re.compile(r"^:?-{3,}:?$")
INLINE_TOKEN = re.compile(
    r"(`[^`\n]+`|!\[[^]\n]*\]\([^\n)]*\)|\[[^]\n]+\]\([^\n)]*\)|"
    r"\*\*[^*\n]+\*\*|\b[FE]\d{2,}\b)"
)


CSS = """
:root { color-scheme: light; --ink: #17212b; --muted: #56616d;
  --line: #d6dde5; --paper: #fff; --wash: #f5f7fa; --accent: #075985; }
* { box-sizing: border-box; }
html { background: var(--wash); font-size: 16px; }
body { margin: 0; color: var(--ink); background: var(--wash);
  font: 1rem/1.58 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { width: min(74rem, calc(100% - 2rem)); margin: 2rem auto;
  padding: clamp(1.25rem, 4vw, 3.5rem); background: var(--paper);
  border: 1px solid var(--line); border-radius: .8rem; }
h1, h2, h3, h4, h5, h6 { line-height: 1.22; margin: 1.6em 0 .55em;
  overflow-wrap: anywhere; }
h1 { margin-top: 0; font-size: clamp(1.8rem, 5vw, 2.7rem); }
h2 { padding-bottom: .3rem; border-bottom: 2px solid var(--line); }
h3 { color: #243b53; }
p, li, td, th { overflow-wrap: anywhere; }
.field { margin: .35rem 0; }
a { color: var(--accent); text-underline-offset: .15em; }
a:focus-visible { outline: 3px solid #f59e0b; outline-offset: 2px; }
code, pre { font-family: ui-monospace, "SFMono-Regular", Consolas, monospace; }
code { padding: .08em .28em; background: #edf2f7; border-radius: .25rem; }
pre { overflow-x: auto; padding: 1rem; background: #111827; color: #f9fafb;
  border-radius: .45rem; white-space: pre; }
pre code { padding: 0; color: inherit; background: transparent; }
blockquote { margin-left: 0; padding: .1rem 1rem; color: var(--muted);
  border-left: .3rem solid #94a3b8; }
.table-wrap { max-width: 100%; margin: 1rem 0; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: .65rem .75rem; text-align: left; vertical-align: top;
  border: 1px solid var(--line); }
th { background: #e8eef5; }
th:first-child, td:first-child { min-width: 8.5rem; }
th:nth-child(2), td:nth-child(2) { min-width: 6.5rem; }
hr { margin: 2rem 0; border: 0; border-top: 1px solid var(--line); }
.unsafe-link { color: var(--muted); }
@media (max-width: 36rem) {
  html { background: var(--paper); }
  main { width: 100%; margin: 0; border: 0; border-radius: 0; }
  ul, ol { padding-left: 1.4rem; }
}
@media print {
  @page { size: A4; margin: 17mm 18mm 18mm;
    @bottom-right { content: counter(page) " / " counter(pages);
      font: 9pt sans-serif; color: #56616d; }
  }
  html { font-size: 10pt; }
  html, body, main { background: #fff; }
  body { font-size: 10pt; line-height: 1.4; }
  main { width: auto; margin: 0; padding: 0; border: 0; }
  h1 { font-size: 23pt; margin: 0 0 5mm; }
  h2 { font-size: 15pt; margin-top: 6mm; }
  h3 { font-size: 11.5pt; margin-top: 5mm; }
  a { color: inherit; }
  h1, h2, h3 { break-after: avoid; }
  p, li { orphans: 3; widows: 3; }
  .field { break-inside: avoid; }
  .record { break-inside: avoid; }
  .table-wrap { overflow: visible; }
  th, td { padding: 2mm 2.5mm; }
  th:first-child, td:first-child { min-width: 25mm; }
  th:nth-child(2), td:nth-child(2) { min-width: 21mm; }
  th:nth-child(3), td:nth-child(3) { min-width: 21mm; }
  tr, blockquote { break-inside: avoid; }
  pre { white-space: pre-wrap; overflow-wrap: anywhere; }
}
""".strip()


def _plain(text):
    """Remove a few presentation markers for titles and generated identifiers."""
    return re.sub(r"[`*_]", "", text).strip()


def _safe_href(value):
    """Return a conservative link target, or None when it should remain text."""
    if not value or value != value.strip():
        return None
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        return None
    if any(char in value for char in ('\\', '"', "'", '<', '>')):
        return None
    if value.startswith('#'):
        return value if re.fullmatch(r"#[A-Za-z][A-Za-z0-9_.:-]*", value) else None
    try:
        parts = urlsplit(value)
        if parts.scheme in ('http', 'https'):
            if not parts.netloc or parts.username is not None or parts.password is not None:
                return None
            parts.port  # Trigger validation of malformed ports.
            hostname = parts.hostname or ''
            labels = hostname.split('.')
            if (not parts.netloc.isascii() or
                    any(not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?",
                                         label) for label in labels)):
                return None
            return value
        if parts.scheme == 'mailto':
            if parts.netloc or not parts.path or parts.query or parts.fragment:
                return None
            return value
        if parts.scheme or parts.netloc or value.startswith('/'):
            return None
    except ValueError:
        return None
    # Simple relative artifact links are useful, but parent traversal is not.
    if not re.fullmatch(r"[A-Za-z0-9._~/-]+(?:#[A-Za-z0-9_.:-]+)?", value):
        return None
    if '..' in value.split('#', 1)[0].split('/'):
        return None
    return value


def _render_inline(value, known_refs):
    pieces = []
    cursor = 0
    for match in INLINE_TOKEN.finditer(value):
        pieces.append(html.escape(value[cursor:match.start()], quote=True))
        token = match.group(0)
        if token.startswith('`'):
            pieces.append('<code>' + html.escape(token[1:-1], quote=True) + '</code>')
        elif token.startswith('!['):
            # Images can fetch resources automatically, so preserve their syntax as text.
            pieces.append(html.escape(token, quote=True))
        elif token.startswith('['):
            link = re.fullmatch(r"\[([^]]+)\]\(([^)]*)\)", token)
            label, raw_href = link.groups()
            href = _safe_href(raw_href)
            rendered_label = _render_inline(label, known_refs)
            if href is None:
                pieces.append('<span class="unsafe-link">' + rendered_label +
                              ' (<code>' + html.escape(raw_href, quote=True) + '</code>)</span>')
            else:
                rel = ' rel="noreferrer noopener"' if not href.startswith('#') else ''
                pieces.append('<a href="' + html.escape(href, quote=True) + '"' + rel + '>' +
                              rendered_label + '</a>')
        elif token.startswith('**'):
            pieces.append('<strong>' + _render_inline(token[2:-2], known_refs) + '</strong>')
        elif token in known_refs:
            pieces.append('<a class="record-ref" href="#' + token.lower() + '">' + token + '</a>')
        else:
            pieces.append(html.escape(token, quote=True))
        cursor = match.end()
    pieces.append(html.escape(value[cursor:], quote=True))
    return ''.join(pieces)


def _split_table_row(line):
    text = line.strip()
    if text.startswith('|'):
        text = text[1:]
    if text.endswith('|') and not text.endswith(r'\|'):
        text = text[:-1]
    cells, current = [], []
    position = 0
    while position < len(text):
        char = text[position]
        if char == '\\' and position + 1 < len(text) and text[position + 1] == '|':
            current.append('|')
            position += 2
            continue
        if char == '|':
            cells.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
        position += 1
    cells.append(''.join(current).strip())
    return cells


def _is_table(lines, index):
    if index + 1 >= len(lines) or '|' not in lines[index]:
        return False
    rule = _split_table_row(lines[index + 1])
    return bool(rule) and all(TABLE_RULE.fullmatch(cell) for cell in rule)


def _starts_block(lines, index):
    line = lines[index]
    return (not line.strip() or bool(HEADING.match(line)) or bool(FENCE.match(line)) or
            bool(FIELD.match(line)) or
            bool(LIST_ITEM.match(line)) or line.lstrip().startswith('>') or
            bool(re.fullmatch(r"\s*(?:-{3,}|\*{3,}|_{3,})\s*", line)) or
            _is_table(lines, index))


def _heading_id(label, used):
    record = re.match(r"([FE]\d{2,})\b", _plain(label))
    base = record.group(1).lower() if record else re.sub(
        r"[^a-z0-9]+", '-', _plain(label).lower()).strip('-')
    base = base or 'section'
    candidate, suffix = base, 2
    while candidate in used:
        candidate = base + '-' + str(suffix)
        suffix += 1
    used.add(candidate)
    return candidate


def markdown_to_html(markdown):
    """Render a safe, human-readable subset while retaining unknown text."""
    lines = markdown.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    known_refs = set(re.findall(r"^###\s+([FE]\d{2,})\b", markdown, re.MULTILINE))
    body, used_ids, table_count = [], set(), 0
    record_open = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)
            language = fence.group(2).strip()
            index += 1
            content = []
            while index < len(lines) and not re.match(
                    r"^\s*" + re.escape(marker[0]) + r"{" + str(len(marker)) + r",}\s*$",
                    lines[index]):
                content.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            language_attr = (' data-language="' + html.escape(language, quote=True) + '"'
                             if language else '')
            body.append('<pre><code' + language_attr + '>' +
                        html.escape('\n'.join(content), quote=True) + '</code></pre>')
            continue
        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            label = heading.group(2)
            if record_open and level <= 3:
                body.append('</section>')
                record_open = False
            if level == 3 and re.match(r'[FE]\d{2,}\s+[—–-]\s+', label):
                body.append('<section class="record">')
                record_open = True
            anchor = _heading_id(label, used_ids)
            body.append('<h{0} id="{1}">{2}</h{0}>'.format(
                level, anchor, _render_inline(label, known_refs)))
            index += 1
            continue
        if _is_table(lines, index):
            table_count += 1
            headers = _split_table_row(lines[index])
            index += 2
            rows = []
            while index < len(lines) and lines[index].strip() and '|' in lines[index]:
                rows.append(_split_table_row(lines[index]))
                index += 1
            body.append('<div class="table-wrap" role="region" aria-label="Table ' +
                        str(table_count) + '" tabindex="0"><table>')
            body.append('<thead><tr>' + ''.join(
                '<th scope="col">' + _render_inline(cell, known_refs) + '</th>' for cell in headers
            ) + '</tr></thead><tbody>')
            for row in rows:
                body.append('<tr>' + ''.join(
                    '<td>' + _render_inline(cell, known_refs) + '</td>' for cell in row
                ) + '</tr>')
            body.append('</tbody></table></div>')
            continue
        item = LIST_ITEM.match(line)
        if item:
            ordered = item.group(1)[0].isdigit()
            tag = 'ol' if ordered else 'ul'
            items = []
            while index < len(lines):
                item = LIST_ITEM.match(lines[index])
                if not item or item.group(1)[0].isdigit() != ordered:
                    break
                content = [item.group(2).strip()]
                index += 1
                while (index < len(lines) and lines[index].strip() and
                       not LIST_ITEM.match(lines[index]) and not _starts_block(lines, index)):
                    content.append(lines[index].strip())
                    index += 1
                items.append(' '.join(content))
            body.append('<' + tag + '>' + ''.join(
                '<li>' + _render_inline(value, known_refs) + '</li>' for value in items
            ) + '</' + tag + '>')
            continue
        if line.lstrip().startswith('>'):
            quote = []
            while index < len(lines) and lines[index].lstrip().startswith('>'):
                quote.append(lines[index].lstrip()[1:].lstrip())
                index += 1
            body.append('<blockquote><p>' + _render_inline(' '.join(quote), known_refs) +
                        '</p></blockquote>')
            continue
        if re.fullmatch(r"\s*(?:-{3,}|\*{3,}|_{3,})\s*", line):
            body.append('<hr>')
            index += 1
            continue
        if FIELD.match(line):
            field = [line.strip()]
            index += 1
            while (not line.startswith('**Kind:**') and
                   index < len(lines) and lines[index].strip() and
                   not FIELD.match(lines[index]) and not _starts_block(lines, index)):
                field.append(lines[index].strip())
                index += 1
            body.append('<p class="field">' +
                        _render_inline(' '.join(field), known_refs) + '</p>')
            continue
        paragraph = [line.strip()]
        index += 1
        while index < len(lines) and not _starts_block(lines, index):
            paragraph.append(lines[index].strip())
            index += 1
        body.append('<p>' + _render_inline(' '.join(paragraph), known_refs) + '</p>')
    if record_open:
        body.append('</section>')
    return '\n'.join(body)


def render_document(markdown):
    title_match = re.search(r"^#\s+(.+?)\s*$", markdown, re.MULTILINE)
    title = _plain(title_match.group(1)) if title_match else 'Agentic readiness report'
    policy = ("default-src 'none'; style-src 'unsafe-inline'; script-src 'none'; "
              "img-src 'none'; font-src 'none'; connect-src 'none'; media-src 'none'; "
              "object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'")
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="referrer" content="no-referrer">\n'
            '<meta http-equiv="Content-Security-Policy" content="' +
            html.escape(policy, quote=True) + '">\n<title>' + html.escape(title, quote=True) +
            '</title>\n<style>\n' + CSS + '\n</style>\n</head>\n<body>\n<main>\n' +
            markdown_to_html(markdown) + '\n</main>\n</body>\n</html>\n')


def _same_path(left, right):
    try:
        if left.exists() and right.exists() and os.path.samefile(left, right):
            return True
    except OSError:
        pass
    return left.resolve() == right.resolve()


def _check_outputs(source, outputs, force):
    for output in outputs:
        if _same_path(source, output):
            raise ValueError('source and output paths must be different: ' + str(output))
        if not output.parent.is_dir():
            raise ValueError('output directory does not exist: ' + str(output.parent))
        if output.exists() and not force:
            raise ValueError('refusing to overwrite existing output (use --force): ' + str(output))
    for position, output in enumerate(outputs):
        for other in outputs[position + 1:]:
            if _same_path(output, other):
                raise ValueError('HTML and PDF output paths must be different')


def _write_bytes(path, data, force):
    if not force:
        with path.open('xb') as stream:
            stream.write(data)
        return
    descriptor, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=str(path.parent))
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _pdf_bytes(html_text):
    try:
        from weasyprint import HTML
    except Exception as exc:
        raise RuntimeError(
            'PDF requested, but WeasyPrint is not installed and usable. Install it separately '
            'using its official instructions. The HTML output is ready; rerun with --pdf '
            'and --force if you want to replace that generated HTML.'
        ) from exc

    def deny_external_resource(url, *args, **kwargs):
        raise ValueError('external resource access is disabled during PDF rendering: ' + str(url))

    try:
        return HTML(string=html_text, base_url=None,
                    url_fetcher=deny_external_resource).write_pdf()
    except Exception as exc:
        raise RuntimeError('PDF conversion failed; the HTML output is still available: ' + str(exc)) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path, help='canonical Markdown report')
    parser.add_argument('-o', '--output', type=Path,
                        help='HTML destination (default: report name with .html suffix)')
    parser.add_argument('--pdf', nargs='?', const='', metavar='PATH',
                        help='also create PDF; omit PATH to use the report name with .pdf suffix')
    parser.add_argument('--force', action='store_true', help='replace existing output files')
    args = parser.parse_args(argv)
    source = args.report
    html_path = args.output or source.with_suffix('.html')
    pdf_path = None if args.pdf is None else (Path(args.pdf) if args.pdf else source.with_suffix('.pdf'))
    outputs = [html_path] + ([pdf_path] if pdf_path is not None else [])
    try:
        if not source.is_file():
            raise ValueError('report is not a readable file: ' + str(source))
        _check_outputs(source, outputs, args.force)
        markdown = source.read_text(encoding='utf-8')
        rendered = render_document(markdown)
        _write_bytes(html_path, rendered.encode('utf-8'), args.force)
        print('HTML written: ' + str(html_path))
        if pdf_path is not None:
            pdf = _pdf_bytes(rendered)
            _write_bytes(pdf_path, pdf, args.force)
            print('PDF written: ' + str(pdf_path))
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
