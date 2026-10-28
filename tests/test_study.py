import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('study', Path(__file__).resolve().parents[1] / 'tooling/study.py')
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class StudyTest(unittest.TestCase):
    def fixture(self, parent):
        task = parent / 'task'
        task.mkdir()
        config = parent / 'spec.json'
        config.write_text(json.dumps({'harbor_version_output': '0.24.0', 'tasks': [str(task)],
                         'agents': [{'id': x, 'harbor': {'name': x}} for x in ['a', 'b']]}))
        root = parent / 'study'
        study.prepare(config, root)
        return root, config

    def test_prepare_refuses_reset(self):
        with tempfile.TemporaryDirectory() as d:
            root, config = self.fixture(Path(d))
            with self.assertRaises(ValueError):
                study.prepare(config, root)

    def test_version_mismatch_never_launches(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = self.fixture(Path(d))
            with patch.object(study.subprocess, 'check_output', return_value='wrong'), patch.object(study.subprocess, 'run') as run:
                with self.assertRaises(RuntimeError):
                    study.run(root)
                run.assert_not_called()

    def test_orphan_never_relaunches(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = self.fixture(Path(d))
            with sqlite3.connect(root / 'ledger.sqlite') as db:
                db.execute("UPDATE cells SET state='running', attempts=1 WHERE id='0000-a'")
            with patch.object(study.subprocess, 'run') as run:
                with self.assertRaises(RuntimeError):
                    study.run(root, True)
                run.assert_not_called()

    def test_completed_never_relaunches(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = self.fixture(Path(d))
            with sqlite3.connect(root / 'ledger.sqlite') as db:
                db.execute("UPDATE cells SET state='completed', attempts=1")
            with patch.object(study.subprocess, 'check_output', return_value='0.24.0'), patch.object(study.subprocess, 'run') as run:
                study.run(root)
                run.assert_not_called()

    def test_exhausted_error_not_retried(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = self.fixture(Path(d))
            with sqlite3.connect(root / 'ledger.sqlite') as db:
                db.execute("UPDATE cells SET state='error', attempts=3")
            with patch.object(study.subprocess, 'check_output', return_value='0.24.0'), patch.object(study.subprocess, 'run') as run:
                study.run(root, True)
                run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
