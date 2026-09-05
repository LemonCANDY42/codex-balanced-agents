"""Release invariants across the two distributed presets."""
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'explore_luna', 'explore_terra', 'explore_astra', 'explore_astra_high',
    'plan_astra', 'plan_astra_xhigh', 'worker_luna', 'worker_terra', 'worker_sol',
    'worker_astra_low', 'worker_astra', 'worker_astra_high', 'reviewer_sol', 'reviewer_astra',
}
CHANGED = {'explore_luna', 'worker_luna', 'explore_terra', 'worker_terra'}

class PackageTests(unittest.TestCase):
    def test_presets_differ_only_in_documented_effort(self):
        groups = {}
        for preset in ('quality', 'balanced'):
            groups[preset] = {}
            for p in (ROOT / 'presets' / preset / 'agents').glob('*.toml'):
                d = tomllib.loads(p.read_text(encoding='utf-8'))
                self.assertEqual(d['name'], p.stem)
                # Prevent accidental re-export of local settings, endpoints or tool inventory.
                self.assertEqual(set(d), {'name', 'description', 'model', 'model_reasoning_effort', 'developer_instructions'})
                self.assertTrue(d['developer_instructions'].strip())
                self.assertNotRegex(p.read_text(encoding='utf-8'), r'/Users/|/home/|/Applications/|/opt/homebrew/|[A-Z]:\\Users\\')
                groups[preset][p.stem] = d
            self.assertEqual(set(groups[preset]), EXPECTED)
        for name in EXPECTED:
            q, b = groups['quality'][name], groups['balanced'][name]
            if name in CHANGED:
                self.assertEqual(q['model_reasoning_effort'], 'xhigh')
                self.assertEqual(b['model_reasoning_effort'], 'medium')
                q = {**q, 'model_reasoning_effort': 'medium'}
            self.assertEqual(q, b, name)

    def test_local_document_links_resolve(self):
        for p in ROOT.rglob('*.md'):
            for dest in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
                if '://' in dest or dest.startswith('#'):
                    continue
                self.assertTrue((p.parent / dest.split('#')[0]).exists(), (p, dest))
