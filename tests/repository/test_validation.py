"""Repository checks must reject broken packages without relying on their wording."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('repository_validation', ROOT / 'scripts/validate.py')
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


class RepositoryValidationTests(unittest.TestCase):
    def package(self, root):
        skill = root / 'skills/example-skill'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('---\nname: example-skill\ndescription: Inspect an example package.\n---\n')
        (skill / 'LICENSE').write_text('Synthetic license fixture')
        return skill

    def test_valid_new_skill_is_discovered_without_a_registry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.package(root)
            self.assertEqual(validation.validate_repository(root), [])

    def test_missing_entrypoint_or_mismatched_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = self.package(root)
            entrypoint = skill / 'SKILL.md'
            entrypoint.write_text(entrypoint.read_text().replace('name: example-skill', 'name: other-name'))
            self.assertTrue(validation.validate_repository(root))
            entrypoint.unlink()
            self.assertTrue(validation.validate_repository(root))

    def test_duplicate_metadata_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = self.package(root)
            (skill / 'SKILL.md').write_text('---\nname: example-skill\nname: example-skill\ndescription: Example.\n---\n')
            self.assertTrue(validation.validate_repository(root))

    def test_broken_resource_and_external_runtime_dependency_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = self.package(root)
            entrypoint = skill / 'SKILL.md'
            original = entrypoint.read_text()
            entrypoint.write_text(original + '\nRead `references/missing.md`.\n')
            self.assertTrue(validation.validate_repository(root))
            (root / 'README.md').write_text('Collection overview')
            entrypoint.write_text(original + '\n[Required runtime reference](../../README.md)\n')
            self.assertTrue(validation.validate_repository(root))

    def test_invalid_json_schema_and_python_syntax_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = self.package(root)
            schema = skill / 'bad.schema.json'
            schema.write_text('{"type": "not-a-json-schema-type"}')
            self.assertTrue(validation.validate_repository(root))
            schema.unlink()
            (skill / 'bad.py').write_text('def broken(:\n')
            self.assertTrue(validation.validate_repository(root))

    def test_broken_internal_schema_references_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = self.package(root)
            (skill / 'broken.schema.json').write_text('{"$ref": "#/$defs/missing"}')
            self.assertTrue(validation.validate_repository(root))

    def test_documentation_links_are_checked_but_fenced_examples_are_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.package(root)
            readme = root / 'README.md'
            readme.write_text('```markdown\n[Example](missing.md)\n```\n')
            self.assertEqual(validation.validate_repository(root), [])
            readme.write_text('[Actual broken link](missing.md)\n')
            self.assertTrue(validation.validate_repository(root))


if __name__ == '__main__':
    unittest.main()
