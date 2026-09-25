"""Regression tests for the offline research tools, never fetching the web."""
from __future__ import annotations

import copy
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('research', ROOT/'scripts/research.py')
assert spec and spec.loader
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)


class DateTests(unittest.TestCase):
    def test_partial_dates_preserve_precision(self):
        self.assertEqual(research.date_precision(None), 'unknown')
        self.assertEqual(research.date_precision('2015'), 'year')
        self.assertEqual(research.date_precision('2015-07'), 'month')
        self.assertEqual(research.date_precision('2024-02-29'), 'day')

    def test_impossible_dates_are_rejected(self):
        for value in ('2025-02-29', '2015-13', '0000', '2026-9-1', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                research.date_precision(value)


class SchemaTests(unittest.TestCase):
    def test_missing_required_field(self):
        s = {'type':'object','required':['id'],'properties':{'id':{'type':'string'}},'additionalProperties':False}
        self.assertTrue(any('missing required' in e for e in research.schema_errors({}, s)))

    def test_unknown_field(self):
        s = {'type':'object','properties':{},'additionalProperties':False}
        self.assertTrue(research.schema_errors({'extra':1}, s))

    def test_unsupported_keyword(self):
        self.assertTrue(research.schema_errors('x', {'type':'string','unknownKeyword':True}))

    def test_boolean_is_not_integer(self):
        self.assertTrue(research.schema_errors(True, {'type':'integer'}))

    def test_optional_uri(self):
        schema = {'type':['string','null'],'format':'uri'}
        self.assertEqual(research.schema_errors(None, schema), [])
        self.assertEqual(research.schema_errors('https://example.org/x', schema), [])
        self.assertTrue(research.schema_errors('https://secret@example.org/x', schema))

    def test_duplicate_array_values(self):
        self.assertTrue(research.schema_errors(['x','x'], {'type':'array','uniqueItems':True}))


class RepositoryTests(unittest.TestCase):
    def test_repository_validates(self):
        self.assertEqual(research.validate(ROOT), [])

    def test_generated_views_current(self):
        self.assertEqual(research.build(ROOT, check=True), [])

    def test_counts_and_reading_statuses_match(self):
        s = research.stats_summary(ROOT)
        self.assertEqual(sum(s['source_review_status'].values()), s['counts']['sources'])
        self.assertEqual(s['counts']['sources'], len(list((ROOT/'sources/cards').glob('S*.md'))))

    def test_literal_search(self):
        results = research.search(ROOT, 'newsletter', 10)
        self.assertTrue(results)
        self.assertLessEqual(len(results), 10)
        self.assertTrue(all('path' in item for item in results))

    def test_empty_search_rejected(self):
        with self.assertRaises(ValueError):
            research.search(ROOT, '   ')

    def test_cli_stats(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = research.main(['--root', str(ROOT), 'stats'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())['name'], json.loads((ROOT/'person.json').read_text(encoding='utf-8'))['slug'])

    def test_cli_invalid_search_limit(self):
        with redirect_stderr(io.StringIO()):
            code = research.main(['--root', str(ROOT), 'search', 'x', '--limit', '0'])
        self.assertEqual(code, 2)

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            research._local_path(ROOT, ROOT, '../../outside.md')


class MutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('__pycache__','.git','.venv'))

    def edit(self, dataset, edit):
        p = self.root/'data'/f'{dataset}.json'
        value = json.loads(p.read_text(encoding='utf-8'))
        edit(value)
        p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    def test_unknown_reference_detected(self):
        self.edit('claims', lambda rows: rows[0]['source_ids'].append('S999'))
        self.assertTrue(any('unknown reference S999' in e for e in research.validate(self.root)))

    def test_duplicate_source_id_detected(self):
        self.edit('sources', lambda rows: rows.append(copy.deepcopy(rows[0])))
        self.assertTrue(any('duplicate IDs' in e for e in research.validate(self.root)))

    def test_date_precision_mismatch_detected(self):
        self.edit('sources', lambda rows: rows[0].update(published_at='2015-07', date_precision='year'))
        self.assertTrue(any('date precision mismatch' in e for e in research.validate(self.root)))

    def test_incomplete_experiment_detected(self):
        self.edit('experiments', lambda rows: rows.append({
            'id':'X001','title':'test','pattern_ids':[],'status':'completed',
            'started_on':'2026-09-25','design':'test','baseline':None,
            'result':None,'limitations':'test',
        }))
        self.assertTrue(any('needs actual result' in e for e in research.validate(self.root)))

    def test_stale_generated_file_detected_and_rebuilt(self):
        p = self.root/'sources/README.md'
        p.write_text('old\n', encoding='utf-8')
        self.assertIn('sources/README.md', research.build(self.root, check=True))
        research.build(self.root)
        self.assertEqual(research.build(self.root, check=True), [])

    def test_nonexistent_markdown_path_detected(self):
        p = self.root/'research/OVERVIEW.md'
        p.write_text(p.read_text(encoding='utf-8')+'\n[test](missing.md)\n', encoding='utf-8')
        self.assertTrue(any('missing local link missing.md' in e for e in research.validate(self.root)))

    def test_malformed_json_gives_errors_not_traceback(self):
        (self.root/'data/sources.json').write_text('{ broken', encoding='utf-8')
        self.assertTrue(research.validate(self.root))

    def test_obsolete_generated_card_removed(self):
        (self.root/'sources/cards/S999.md').write_text('obsolete\n', encoding='utf-8')
        self.assertIn('sources/cards/S999.md', research.build(self.root, check=True))
        research.build(self.root)
        self.assertFalse((self.root/'sources/cards/S999.md').exists())


if __name__ == '__main__':
    unittest.main()
