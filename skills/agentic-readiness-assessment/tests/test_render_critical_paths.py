"""Pin the renderer behaviours a reader or report owner depends on most.

1. Hostile report text can only produce allowlisted markup and link targets.
2. Report text stays visible, and finding/evidence links reach their records.
3. Writing outputs never destroys the source, an existing file or a link target.
"""
import html
import importlib.util
import os
import random
import re
import subprocess
import sys
import tempfile
import types
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'scripts/render_report.py'
spec = importlib.util.spec_from_file_location('report_renderer_critical', SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


ALLOWED_TAGS = {
    'html', 'head', 'meta', 'title', 'style', 'body', 'main', 'h1', 'h2', 'h3', 'h4',
    'h5', 'h6', 'p', 'a', 'strong', 'code', 'pre', 'ul', 'ol', 'li', 'blockquote', 'hr',
    'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'section', 'span'}
ALLOWED_ATTRIBUTES = {
    'id', 'class', 'href', 'rel', 'scope', 'role', 'aria-label', 'tabindex',
    'data-language', 'lang', 'charset', 'name', 'content', 'http-equiv'}
HOSTILE_ATOMS = [
    '<script>alert(1)</script>', '<img src=x onerror=alert(1)>', '<svg onload=alert(1)>',
    '"', "'", '<', '>', '&', '`', '```', '~~~', '**', '[', ']', '(', ')', '\\', '\\|',
    '</code>', '</pre>', '</title>', '<!--', '<style>', '‮', '\t', ' ', 'x', '\n', '\n\n',
    '![x](https://example.test/a.png)', '[a](javascript:alert(1))', '[a](JaVaScRiPt:x)',
    '[a](data:text/html,<b>)', '[a](//evil.test)', '[a](../../etc/passwd)',
    '[a](/etc/passwd)', '[a](file:///etc/passwd)', '[a](https://u:p@example.test)',
    '[a](https://example.test/" onmouseover="x)', '[a](vbscript:x)', '[a](%2e%2e/x)',
    '[a](https://example.test)', '[a](artifacts/log.txt)', '[a](#f01)',
    '[a](mailto:team@example.test)', '[F01 upstream](https://example.test)', 'F01', 'E01',
    '# ', '## ', '### F01 - title', '### E01 - title', '| a | b |', '|---|---|', '- ',
    '1. ', '> ', '---', '**Kind:**', '**Why:**']


class MarkupAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.problems, self.ids, self.fragments, self.open_anchors = [], [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            self.problems.append(('tag', tag))
        for name, value in attrs:
            if name not in ALLOWED_ATTRIBUTES:
                self.problems.append(('attribute', name, value))
            if name == 'id':
                self.ids.append(value)
            if name == 'href':
                self.check_href(value or '')
        if tag == 'a':
            if self.open_anchors:
                self.problems.append(('nested anchor', attrs))
            self.open_anchors += 1

    def handle_endtag(self, tag):
        if tag == 'a':
            self.open_anchors -= 1

    def check_href(self, href):
        lowered = href.lower()
        path = href.split('#', 1)[0]
        if href.startswith('#'):
            self.fragments.append(href[1:])
        elif not lowered.startswith(('https://', 'http://', 'mailto:')):
            if ':' in path or path.startswith('/') or '..' in path.split('/'):
                self.problems.append(('href', href))


def audit(document):
    parser = MarkupAudit()
    parser.feed(document)
    return parser


def visible_text(fragment):
    return html.unescape(re.sub(r'<[^>]+>', '', fragment))


class HostileInputTests(unittest.TestCase):
    def test_hostile_corpus_emits_only_allowlisted_markup_and_targets(self):
        generator = random.Random(20261030)
        for case in range(400):
            source = ''.join(generator.choice(HOSTILE_ATOMS)
                             for _ in range(generator.randint(1, 40)))
            with self.subTest(case=case, source=source):
                self.assertEqual(audit(renderer.render_document(source)).problems, [])

    def test_hostile_title_cannot_leave_the_title_element(self):
        output = renderer.render_document('# </title><style>*{}</style><script>x</script>\n')
        head = output.split('</head>', 1)[0]
        self.assertEqual(head.count('<style>'), 1)
        self.assertNotIn('<script', output)


class RecordLinkTests(unittest.TestCase):
    def test_record_reference_inside_a_link_label_keeps_the_external_link_whole(self):
        output = renderer.markdown_to_html(
            '# T\n\n### F01 - Thing\n\nSee [the F01 upstream note](https://example.test/x).\n')
        self.assertEqual(audit(output).problems, [])
        self.assertIn('<a href="https://example.test/x" rel="noreferrer noopener">'
                      'the F01 upstream note</a>', output)

    def test_every_record_link_targets_an_existing_anchor(self):
        source = '\n'.join([
            '# T', '', '## What to improve', '#### F01 follow-up notes', '',
            '### F01 - Real finding', '', 'See F01, E01 and F07.', '',
            '## Evidence', '```', '### F07 - quoted from the previous report', '```', '',
            '### E01 - Baseline', 'Ran it.'])
        parsed = audit(renderer.markdown_to_html(source))
        self.assertEqual(sorted(set(parsed.fragments) - set(parsed.ids)), [])
        self.assertNotIn('f07', parsed.fragments)

    def test_record_anchor_belongs_to_the_record_not_an_earlier_heading(self):
        output = renderer.markdown_to_html(
            '# T\n\n#### F01 follow-up\n\n### F01 - Real\n\nSee F01.\n')
        self.assertIn('<h3 id="f01">', output)
        self.assertIn('<h4 id="f01-2">', output)


class TextPreservationTests(unittest.TestCase):
    def test_inline_triple_backticks_at_line_start_do_not_swallow_the_report(self):
        source = ('# T\n\n## Evidence\n```npm test``` exited 0.\n\n'
                  '### E01 - Baseline\n**Kind:** Executed\n')
        output = renderer.markdown_to_html(source)
        self.assertNotIn('<pre>', output)
        self.assertIn('<h3 id="e01">', output)
        self.assertIn('exited 0.', visible_text(output))
        self.assertIn('<code>npm test</code>', output)

    def test_real_fences_with_and_without_info_strings_still_render_as_code(self):
        output = renderer.markdown_to_html(
            '```sh\necho "<b>"\n```\n\n````\n```\nnested\n````\n\n~~~ text\nx ``` y\n~~~\n')
        self.assertEqual(output.count('<pre>'), 3)
        self.assertIn('data-language="sh"', output)
        self.assertIn('echo &quot;&lt;b&gt;&quot;', output)
        self.assertIn('```\nnested', html.unescape(output))

    def test_words_in_any_supported_block_remain_visible(self):
        prefixes = ['', '# ', '## ', '### ', '### F01 - ', '- ', '1. ', '2) ', '* ', '+ ',
                    '> ', '| ', '**Why:** ', '**Kind:** ', '    ']
        words = ['alpha', 'beta', 'gamma', 'delta', 'F01', 'E02', 'x|y', r'a\|b', '---',
                 '[link](https://example.test)', '`code`', '**bold**', '![i](a.png)',
                 '|---|---|', '<b>']
        generator = random.Random(7)
        for case in range(400):
            lines = []
            for _ in range(generator.randint(1, 8)):
                if generator.random() < 0.15:
                    lines.append(generator.choice(['```', '~~~', '````']))
                    continue
                lines.append(generator.choice(prefixes) + ' '.join(
                    generator.choice(words) for _ in range(generator.randint(0, 4))))
            source = '\n'.join(lines)
            text = visible_text(renderer.markdown_to_html(source))
            for word in ('alpha', 'beta', 'gamma', 'delta'):
                with self.subTest(case=case, word=word, source=source):
                    self.assertGreaterEqual(text.count(word), source.count(word))


class OutputSafetyTests(unittest.TestCase):
    REPORT = '# Report\n\n## TL:TR\n**Verdict:** Blocked\n'

    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                              capture_output=True, text=True)

    def test_failed_forced_replace_keeps_the_old_file_and_leaves_no_temporary(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'report.html'
            target.write_bytes(b'previous export')
            with mock.patch.object(renderer.os, 'replace', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    renderer._write_bytes(target, b'new export', True)
            self.assertEqual(target.read_bytes(), b'previous export')
            self.assertEqual(os.listdir(tmp), ['report.html'])

    def test_unforced_write_never_follows_a_dangling_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            victim = Path(tmp) / 'created-elsewhere.txt'
            output = Path(tmp) / 'report.html'
            source.write_text(self.REPORT, encoding='utf-8')
            output.symlink_to(victim)
            result = self.run_cli(source)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(victim.exists())
            self.assertNotIn('Traceback', result.stderr)

    def test_forced_write_replaces_a_symlink_not_its_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            victim = Path(tmp) / 'unrelated.txt'
            output = Path(tmp) / 'report.html'
            source.write_text(self.REPORT, encoding='utf-8')
            victim.write_text('keep me', encoding='utf-8')
            output.symlink_to(victim)
            result = self.run_cli(source, '--force')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(victim.read_text(encoding='utf-8'), 'keep me')
            self.assertFalse(output.is_symlink())
            self.assertIn('<!doctype html>', output.read_text(encoding='utf-8'))

    def test_force_refuses_an_output_that_links_to_the_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            output = Path(tmp) / 'view.html'
            source.write_text(self.REPORT, encoding='utf-8')
            output.symlink_to(source)
            result = self.run_cli(source, '--output', output, '--force')
            self.assertEqual(result.returncode, 1)
            self.assertIn('must be different', result.stderr)
            self.assertEqual(source.read_text(encoding='utf-8'), self.REPORT)

    def test_default_pdf_path_never_replaces_a_pdf_named_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.pdf'
            source.write_text(self.REPORT, encoding='utf-8')
            result = self.run_cli(source, '--pdf', '--force')
            self.assertEqual(result.returncode, 1)
            self.assertEqual(source.read_text(encoding='utf-8'), self.REPORT)
            self.assertFalse((Path(tmp) / 'report.html').exists())

    def test_output_directory_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            output = Path(tmp) / 'report.html'
            source.write_text(self.REPORT, encoding='utf-8')
            output.mkdir()
            (output / 'keep.txt').write_text('keep', encoding='utf-8')
            for arguments in ((), ('--force',)):
                with self.subTest(arguments=arguments):
                    result = self.run_cli(source, *arguments)
                    self.assertEqual(result.returncode, 1)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertEqual((output / 'keep.txt').read_text(encoding='utf-8'), 'keep')
            self.assertEqual(sorted(os.listdir(tmp)), ['report.html', 'report.md'])

    def test_invalid_utf8_report_is_a_clean_error_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            source.write_bytes(b'# Report\n\xff\xfe broken\n')
            result = self.run_cli(source)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Error:', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse((Path(tmp) / 'report.html').exists())

    def test_pdf_conversion_failure_is_reported_without_a_traceback(self):
        fake = types.ModuleType('weasyprint')

        class BrokenHTML:
            def __init__(self, **kwargs):
                pass

            def write_pdf(self):
                raise ValueError('synthetic layout failure')

        fake.HTML = BrokenHTML
        with mock.patch.dict(sys.modules, {'weasyprint': fake}):
            with self.assertRaises(RuntimeError) as raised:
                renderer._pdf_bytes(renderer.render_document(self.REPORT))
        self.assertIn('HTML output is still available', str(raised.exception))
        self.assertIn('synthetic layout failure', str(raised.exception))


if __name__ == '__main__':
    unittest.main()
