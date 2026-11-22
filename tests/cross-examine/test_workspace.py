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
        for name in ('children-ai', 'finance-budget', 'b2b-saas', 'offline-timer-complete'):
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

    def complete_workspace(self):
        return json.loads((EXAMPLES / 'offline-timer-complete.json').read_text())

    def test_complete_profile_is_valid_with_reported_facts(self):
        document = self.complete_workspace()
        self.assertEqual(mod.validation_errors(document), [])
        self.assertEqual(document['features'][0]['confidence'], 'reported')

    def test_timestamps_are_checked_with_fresh_runtime_dependencies(self):
        for timestamp in ('not-a-timestamp', '2026-02-30T10:00:00Z', '2026-11-22T10:00:00'):
            document = self.complete_workspace()
            document['interview']['last_updated'] = timestamp
            self.assertTrue(mod.validation_errors(document))

    def test_completion_flags_do_not_make_empty_profile_complete(self):
        document = json.loads((SKILL / 'assets/workspace.template.json').read_text())
        document['interview']['status'] = 'discovery_complete'
        for coverage in document['interview']['coverage']:
            coverage.update(status='sufficient', reason='This label alone does not establish a product profile.')
        self.assertTrue(any('discovery_complete requires' in error for error in mod.validation_errors(document)))

    def test_completed_coverage_requires_substantive_reasons_at_any_stage(self):
        for status in ('in_progress', 'discovery_complete'):
            for coverage_status in ('sufficient', 'not_applicable'):
                with self.subTest(status=status, coverage_status=coverage_status):
                    document = self.complete_workspace()
                    document['interview']['status'] = status
                    document['interview']['coverage'][0].update(status=coverage_status, reason='  ')
                    self.assertTrue(mod.validation_errors(document))

    def test_completion_requires_history_update_time_and_data_paths(self):
        for section, field, value in (
            ('interview', 'question_history', []), ('interview', 'last_updated', None),
            ('distribution', 'platforms', []), ('distribution', 'channels', []),
            ('project', 'product_types', []),
        ):
            with self.subTest(field=field):
                document = self.complete_workspace()
                document[section][field] = value
                self.assertTrue(mod.validation_errors(document))
        document = self.complete_workspace()
        document['data_flows'] = []
        document['interview']['question_history'][1]['updated_ids'].remove('FLOW-0001')
        self.assertTrue(any('data flows' in error for error in mod.validation_errors(document)))

    def test_blocked_or_duplicate_domains_prevent_completion(self):
        document = self.complete_workspace()
        document['interview']['coverage'][0]['status'] = 'blocked_on_unknown'
        self.assertTrue(mod.validation_errors(document))
        document = self.complete_workspace()
        document['interview']['coverage'].append(copy.deepcopy(document['interview']['coverage'][0]))
        self.assertTrue(any('repeats' in error for error in mod.validation_errors(document)))

    def test_research_unknown_can_remain_if_owned_and_actionable(self):
        document = self.complete_workspace()
        unknown = {'id':'UNK-0001', 'question':'Does a later accessibility audit support the reported keyboard behavior?',
                   'risk_if_unresolved':'Some users may be unable to operate the timer', 'priority':'high',
                   'status':'research_needed', 'related_ids':['FEAT-0001'], 'owner':'Product developer',
                   'next_action':'Inspect keyboard behavior in the later implementation audit'}
        document['unknowns'].append(unknown)
        self.assertEqual(mod.validation_errors(document), [])
        unknown['next_action'] = ' '
        self.assertTrue(mod.validation_errors(document))

    def test_supported_and_contradicted_claims_require_reviewed_evidence_fields(self):
        document = json.loads((EXAMPLES / 'children-ai.json').read_text())
        claim = document['claims'][0]
        original_source = claim['source']
        for status in ('partially_verified', 'verified', 'contradicted'):
            with self.subTest(status=status):
                claim.update(verification=status, evidence_refs=[], notes='')
                self.assertTrue(mod.validation_errors(document))
                claim.update(evidence_refs=['synthetic-review/provider-contract.txt#retention'],
                             notes='Synthetic test review records the support or contradiction and its limits.')
                self.assertEqual(mod.validation_errors(document), [])
                self.assertEqual(claim['source'], original_source)

    def test_verified_facts_require_evidence_and_review_notes(self):
        document = self.complete_workspace()
        feature = document['features'][0]
        feature['confidence'] = 'verified'
        self.assertTrue(mod.validation_errors(document))
        feature.update(evidence_refs=['synthetic-review/timer-test.txt'], verification_notes='Synthetic test artifact reviewed for the specific countdown behavior.')
        self.assertEqual(mod.validation_errors(document), [])

    def test_verified_jurisdiction_requires_evidence_and_verified_confidence(self):
        document = json.loads((EXAMPLES / 'children-ai.json').read_text())
        jurisdiction = document['jurisdictions'][0]
        jurisdiction['applicability'] = 'applicable_verified'
        self.assertTrue(mod.validation_errors(document))
        jurisdiction.update(confidence='verified', evidence_refs=['synthetic-review/applicability.txt'],
                            verification_notes='Synthetic applicability review, not an actual legal conclusion.')
        self.assertEqual(mod.validation_errors(document), [])

    def test_resume_and_readonly_commands_preserve_history_ids_and_contradictions(self):
        document = self.complete_workspace()
        document['claims'] = [{'id':'CLM-0007', 'statement':'No duration data is processed', 'source':'developer_reported',
                               'verification':'contradicted', 'evidence_refs':['synthetic-review/duration-input.txt'],
                               'related_ids':['DATA-0001'], 'notes':'The earlier assertion conflicts with the recorded duration input; the deployment has not been inspected.'}]
        document['interview']['question_history'].append({
            'id':'Q-0010', 'question':'How does the no-data assertion fit the duration input?',
            'answer_summary':'Preserve the earlier assertion and distinguish transient local duration processing.',
            'answered_at':'2026-11-22T10:05:00+05:30', 'updated_ids':['CLM-0007','DATA-0001']})
        document['interview'].update(status='paused', last_updated='2026-11-22T10:05:00+05:30')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / '.product-assurance/workspace.json'
            target.parent.mkdir()
            target.write_text(json.dumps(document))
            original = target.read_bytes()
            for action, expected in (('init', 2), ('status', 0), ('validate', 0)):
                result = subprocess.run([sys.executable, str(SCRIPT), action, '--project-root', str(root)], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertEqual(target.read_bytes(), original)

    def test_cli_rejects_malformed_json_and_wrong_shapes_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'workspace.json'
            for contents in (b'{', b'[]', b'null', b'\xff', b'{"project": [], "interview": {}}'):
                target.write_bytes(contents)
                for action in ('validate', 'status'):
                    result = subprocess.run([sys.executable, str(SCRIPT), action, '--workspace', str(target)], capture_output=True, text=True)
                    self.assertIn(result.returncode, (1, 2), result.stderr)
                    self.assertNotIn('Traceback', result.stderr)

    def test_stdlib_commands_work_without_validation_dependency(self):
        with tempfile.TemporaryDirectory() as temporary:
            command = [sys.executable, '-I', '-S', str(SCRIPT)]
            for action, expected in (('init', 0), ('status', 0), ('validate', 3)):
                result = subprocess.run(command + [action, '--project-root', temporary], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                if action == 'validate':
                    self.assertIn('requirements.txt', result.stderr)
                if action == 'status':
                    self.assertIn('not performed', result.stdout)

    def test_v1_migration_preserves_source_and_requires_explicit_output(self):
        document = self.complete_workspace()
        document['schema_version'] = '1.0.0'
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'v1.json'
            target = Path(temporary) / 'v2.json'
            source.write_text(json.dumps(document))
            original = source.read_bytes()
            validate = subprocess.run([sys.executable, str(SCRIPT), 'validate', '--workspace', str(source)], capture_output=True, text=True)
            self.assertEqual(validate.returncode, 1)
            self.assertIn('migration', validate.stderr)
            command = [sys.executable, str(SCRIPT), 'migrate', '--workspace', str(source), '--output', str(target)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            migrated = json.loads(target.read_text())
            self.assertEqual(migrated.pop('schema_version'), '2.0.0')
            expected = copy.deepcopy(document)
            expected.pop('schema_version')
            self.assertEqual(migrated, expected)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(source.read_bytes(), original)

    def test_migration_reports_unsupported_old_completion_without_fabrication(self):
        document = json.loads((SKILL / 'assets/workspace.template.json').read_text())
        document['schema_version'] = '1.0.0'
        document['interview']['status'] = 'discovery_complete'
        for coverage in document['interview']['coverage']:
            coverage['status'] = 'sufficient'
        with tempfile.TemporaryDirectory() as temporary:
            source, target = Path(temporary) / 'v1.json', Path(temporary) / 'v2.json'
            source.write_text(json.dumps(document))
            original = source.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), 'migrate', '--workspace', str(source), '--output', str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(source.read_bytes(), original)
            migrated = json.loads(target.read_text())
            self.assertEqual(migrated['interview'], document['interview'])
            self.assertEqual(migrated['actors'], [])


if __name__=='__main__':
    unittest.main()
