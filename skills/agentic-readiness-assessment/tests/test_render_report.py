"""Deterministic safety and preservation checks for the optional report renderer."""
import html
import importlib.util
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'scripts/render_report.py'
spec = importlib.util.spec_from_file_location('report_renderer', SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


REPORT = '''# Fixture readiness & delivery

## TL:TR
**Verdict:** Needs improvements
**Confidence:** High
**Delegation:** Delegate bounded CLI work; retain review for release changes.

- The feedback loop is useful and one release boundary remains manual.

## Readiness checks
| Check | State | What this means |
|---|---|---|
| Setup | Passed | A clean setup worked (E01). |
| Deliverable | Passed | The CLI ran (E01). |
| Primary checks | Passed | Behavioral tests passed (E01). |
| Probe | Gap | A packaging defect escaped (E02; F01). |

| Task | Advice | Basis |
|---|---|---|
| Change parser | Delegate | Demonstrated |
| Publish release | Retain review | Inspected |

## What to improve
### F01 - Detect packaged-resource regressions
**Priority:** P1
**Owner:** Repo
**Basis:** Demonstrated
**Task:** Package and verify the installed artifact.
**Effort:** Small
**Key:** packaging-gate
**Why:** Source-tree checks hide a missing resource.
**Evidence:** E02 and [upstream guidance](https://example.test/guidance).
**Change:** Exercise the installed artifact.
**Verify:** Removing the resource fails the package check.

Reassessment status: open until a packaged-artifact probe passes.

## What already works
The baseline command is quick and meaningful (E01).

## Scope and limits
**Scope:** Full synthetic fixture.
**Coverage:** Full
**Mode:** Executed
**Revision:** Synthetic snapshot.
**Skill version:** 5.1.0

No private repository content is present.

## Evidence
### E01 - Baseline checks
**Kind:** Executed
**Supports:** Setup, CLI delivery and behavioral feedback.
**Limits:** One interpreter and no release publication.
`python3 -m unittest`, cwd fixture, exit 0.

### E02 - Package probe
**Kind:** Executed
**Supports:** F01 and the Probe gap.
**Limits:** Synthetic artifact only.
The missing resource was not detected; exact source bytes were restored.
'''


class RenderTests(unittest.TestCase):
    def run_cli(self, *arguments, isolated=False):
        command = [sys.executable]
        if isolated:
            command.append('-S')
        command.extend([str(SCRIPT), *map(str, arguments)])
        return subprocess.run(command, capture_output=True, text=True)

    def test_future_additive_fields_and_nested_task_table_are_preserved(self):
        output = renderer.render_document(REPORT)
        for phrase in (
                'Delegation:', 'Task', 'Retain review', 'Basis:', 'Demonstrated',
                'Effort:', 'packaging-gate', 'Reassessment status:', 'Supports:',
                'Limits:', 'exact source bytes were restored'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, html.unescape(output))
        self.assertEqual(output.count('<table>'), 2)

    def test_table_preserves_backslashes_and_decodes_only_escaped_pipes(self):
        source = REPORT.replace(
            '| Change parser | Delegate | Demonstrated |',
            r'| Change parser | `C:\repo\reports` | one \| two |')
        output = html.unescape(renderer.render_document(source))
        self.assertIn(r'C:\repo\reports', output)
        self.assertIn('one | two', output)

    def test_report_text_and_raw_html_are_escaped(self):
        hostile = REPORT.replace(
            '# Fixture readiness & delivery',
            '# </title><script>alert("title")</script>')
        hostile += '''\n<p onclick="alert(1)">raw</p>
[unsafe](javascript:alert(1)) [local](file:///etc/passwd)
![remote](https://example.test/tracker.png)
```
</code><script>alert("code")</script>
```
'''
        output = renderer.render_document(hostile)
        self.assertNotIn('<script', output.lower())
        self.assertNotIn('<img', output.lower())
        self.assertNotIn('href="javascript:', output.lower())
        self.assertNotIn('href="file:', output.lower())
        self.assertIn('&lt;p onclick=&quot;alert(1)&quot;&gt;raw&lt;/p&gt;', output)
        self.assertIn('![remote](https://example.test/tracker.png)', html.unescape(output))

    def test_safe_external_relative_and_record_links_are_clickable(self):
        source = REPORT.replace(
            'The baseline command is quick and meaningful (E01).',
            'See [log](artifacts/check.txt), [mail](mailto:team@example.test), E01 and F01.')
        output = renderer.render_document(source)
        self.assertIn('id="f01"', output)
        self.assertIn('id="e01"', output)
        self.assertIn('href="#f01"', output)
        self.assertIn('href="#e01"', output)
        self.assertIn('href="https://example.test/guidance"', output)
        self.assertIn('href="artifacts/check.txt"', output)
        self.assertIn('href="mailto:team@example.test"', output)

    def test_html_is_single_file_and_does_not_auto_fetch_resources(self):
        output = renderer.render_document(REPORT)
        lowered = output.lower()
        self.assertIn('content-security-policy', lowered)
        self.assertIn("default-src &#x27;none&#x27;", lowered)
        for marker in ('<script', '<link', '<img', '<iframe', ' src=', '@import', 'url('):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, lowered)

    def test_cli_writes_utf8_html_without_changing_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report café.md'
            output = Path(tmp) / 'result.html'
            source.write_text(REPORT + '\nUnicode: Zażółć 🧪\n', encoding='utf-8')
            before = source.read_bytes()
            result = self.run_cli(source, '--output', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_bytes(), before)
            self.assertIn('Zażółć 🧪', output.read_text(encoding='utf-8'))

    def test_existing_output_is_preserved_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            output = Path(tmp) / 'report.html'
            source.write_text(REPORT, encoding='utf-8')
            output.write_text('keep me', encoding='utf-8')
            result = self.run_cli(source)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(output.read_text(encoding='utf-8'), 'keep me')
            self.assertIn('--force', result.stderr)
            forced = self.run_cli(source, '--force')
            self.assertEqual(forced.returncode, 0, forced.stderr)
            self.assertIn('<!doctype html>', output.read_text(encoding='utf-8'))

    def test_force_never_allows_source_output_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            source.write_text(REPORT, encoding='utf-8')
            before = source.read_bytes()
            result = self.run_cli(source, '--output', source, '--force')
            self.assertEqual(result.returncode, 1)
            self.assertEqual(source.read_bytes(), before)
            self.assertIn('must be different', result.stderr)

    def test_html_and_pdf_destinations_cannot_collide(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            output = Path(tmp) / 'combined.out'
            source.write_text(REPORT, encoding='utf-8')
            result = self.run_cli(source, '--output', output, '--pdf', output)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(output.exists())

    def test_missing_pdf_backend_is_actionable_and_keeps_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'report.md'
            html_output = Path(tmp) / 'report.html'
            pdf_output = Path(tmp) / 'report.pdf'
            source.write_text(REPORT, encoding='utf-8')
            result = self.run_cli(source, '--pdf', isolated=True)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(html_output.is_file())
            self.assertFalse(pdf_output.exists())
            self.assertIn('WeasyPrint is not installed and usable', result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_pdf_backend_cannot_fetch_network_or_local_resources(self):
        attempts = []
        fake = types.ModuleType('weasyprint')

        class FakeHTML:
            def __init__(self, *, string, base_url, url_fetcher):
                self.fetch = url_fetcher
                self.base_url = base_url

            def write_pdf(self):
                for url in ('file:///etc/passwd', 'https://example.test/tracker'):
                    with self_case.assertRaises(ValueError):
                        self.fetch(url)
                    attempts.append(url)
                self_case.assertIsNone(self.base_url)
                return b'%PDF-synthetic'

        self_case = self
        fake.HTML = FakeHTML
        previous = sys.modules.get('weasyprint')
        sys.modules['weasyprint'] = fake
        try:
            self.assertEqual(renderer._pdf_bytes(renderer.render_document(REPORT)), b'%PDF-synthetic')
        finally:
            if previous is None:
                del sys.modules['weasyprint']
            else:
                sys.modules['weasyprint'] = previous
        self.assertEqual(len(attempts), 2)


if __name__ == '__main__':
    unittest.main()
