import unittest
from lms_engine.harness import Harness
from lms_engine.loop import run_loop

class LoopTests(unittest.TestCase):
    def test_success(self):
        result = run_loop(Harness.demo(), 'hello', 3)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['attempts'], 1)

    def test_retries_then_success(self):
        calls = []
        def execute(task, attempt):
            calls.append(attempt)
            return 'ok' if attempt == 2 else ''
        result = run_loop(Harness(execute, bool), 'hello', 3)
        self.assertEqual(calls, [1, 2])
        self.assertEqual(result['status'], 'success')

    def test_exhaustion(self):
        result = run_loop(Harness(lambda task, attempt: '', bool), 'hello', 2)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['attempts'], 2)

    def test_exception_is_bounded(self):
        def execute(task, attempt):
            raise RuntimeError('tool unavailable')
        result = run_loop(Harness(execute, bool), 'hello', 2)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['attempts'], 2)
        self.assertEqual(result['error'], 'RuntimeError')

    def test_invalid_input(self):
        for task, limit in [('', 2), ('  ', 2), ('hello', 0), ('hello', 101)]:
            with self.assertRaises(ValueError):
                run_loop(Harness.demo(), task, limit)

if __name__ == '__main__':
    unittest.main()
