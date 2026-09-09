"""Portable packaging checks: the copied skill must work without the repo root."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/agentic-readiness-assessment'


class PackageTests(unittest.TestCase):
    def test_versions_agree_with_self_contained_skill(self):
        match = re.search(r'^  version: "([^"]+)"$', (SKILL / 'SKILL.md').read_text(), re.M)
        self.assertIsNotNone(match)
        for path in ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json', 'gemini-extension.json'):
            with self.subTest(path=path):
                self.assertEqual(json.loads((ROOT / path).read_text())['version'], match[1])

    def test_referenced_resources_exist_in_copied_folder(self):
        for file in [SKILL / 'SKILL.md', *list((SKILL / 'references').glob('*.md'))]:
            for ref in re.findall(r'\]\(([^)]+)\)', file.read_text()):
                if '://' not in ref and not ref.startswith('#'):
                    self.assertTrue((file.parent / ref.split('#')[0]).is_file(), (file, ref))

    def test_copied_skill_keeps_license_and_notice(self):
        for name in ('LICENSE', 'NOTICE'):
            self.assertEqual((ROOT / name).read_bytes(), (SKILL / name).read_bytes())

    def test_fork_metadata_does_not_impersonate_upstream(self):
        for path in ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json'):
            data = json.loads((ROOT / path).read_text())
            self.assertEqual(data['repository'], 'https://github.com/joozio/agentic-readiness-assessment')
            self.assertEqual(data['author']['name'], 'joozio')
        market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        self.assertEqual(market['owner']['name'], 'joozio')

    def test_folder_can_run_its_checks_outside_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / SKILL.name
            shutil.copytree(SKILL, target, ignore=shutil.ignore_patterns('__pycache__'))
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(target / 'tests'), '-q'], cwd=tmp, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == '__main__':
    unittest.main()
