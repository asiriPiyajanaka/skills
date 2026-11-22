"""Deterministic tests for the discovery contract; not compliance correctness tests."""
from __future__ import annotations
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills' / 'cross-examine'
EXAMPLES = ROOT / 'examples' / 'cross-examine'
SCRIPT = SKILL / 'scripts' / 'workspace.py'
spec = importlib.util.spec_from_file_location('assurance_workspace', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class WorkspaceTests(unittest.TestCase):
    def test_examples_are_valid(self):
        for name in ('children-ai', 'finance-budget', 'b2b-saas'):
            with self.subTest(name=name):
                path = EXAMPLES / f'{name}.json'
                proc = subprocess.run([sys.executable, str(SCRIPT), 'validate', '--workspace', str(path)], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_init_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as path:
            command = [sys.executable, str(SCRIPT), 'init', '--project-root', path, '--name', 'Trial']
            first = subprocess.run(command, capture_output=True, text=True)
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 2)
            workspace = json.loads((Path(path)/'.product-assurance/workspace.json').read_text())
            self.assertEqual(workspace['project']['name'], 'Trial')
            p = subprocess.run([sys.executable, str(SCRIPT), 'validate', '--project-root', path], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_missing_related_entity_is_invalid(self):
        document = json.loads((EXAMPLES/'children-ai.json').read_text())
        document['features'][0]['actor_ids'] = ['ACT-9999']
        self.assertTrue(any('ACT-9999' in err for err in mod.cross_reference_errors(document)))

    def test_duplicate_id_is_invalid(self):
        document = json.loads((EXAMPLES/'children-ai.json').read_text())
        document['actors'][1]['id'] = document['actors'][0]['id']
        self.assertTrue(any('Duplicate ID' in err for err in mod.cross_reference_errors(document)))

    def test_question_history_links_must_exist(self):
        document = json.loads((EXAMPLES/'finance-budget.json').read_text())
        document['interview']['question_history'] = [{
            'id':'Q-0001','question':'What data is shared?', 'answer_summary':'Unknown',
            'answered_at':'2026-11-19T07:00:00+05:30','updated_ids':['DATA-9999']}]
        self.assertTrue(any('DATA-9999' in err for err in mod.cross_reference_errors(document)))

    def test_initial_state_has_no_fake_compliance_verdict(self):
        document = json.loads((SKILL/'assets/workspace.template.json').read_text())
        self.assertEqual(document['interview']['status'], 'not_started')
        self.assertEqual(len(document['interview']['coverage']), 12)
        self.assertEqual(document['jurisdictions'], [])
        self.assertEqual(document['claims'], [])

    def test_cannot_mark_discovery_complete_with_unassessed_domains(self):
        document = json.loads((EXAMPLES/'children-ai.json').read_text())
        document['interview']['status'] = 'discovery_complete'
        self.assertTrue(any('discovery_complete requires' in err for err in mod.cross_reference_errors(document)))

    def test_skill_metadata_and_guides(self):
        skillmd = (SKILL/'SKILL.md').read_text()
        self.assertTrue(skillmd.startswith('---\nname: cross-examine\n'))
        self.assertIn('description:', skillmd)
        for filename in ('interview-method.md','risk-triggers.md','workspace-contract.md'):
            self.assertTrue((SKILL/'references'/filename).is_file())

    def test_status_never_claims_launch_readiness(self):
        p = subprocess.run([sys.executable, str(SCRIPT),'status','--workspace',str(EXAMPLES/'b2b-saas.json')],capture_output=True,text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('NOT a legal compliance or launch-readiness verdict', p.stdout)
        self.assertIn('Tenant', p.stdout.lower().title())


if __name__=='__main__':
    unittest.main()
