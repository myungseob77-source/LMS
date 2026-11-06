import unittest
from lms_engine.graph import build_graph, run_graph
from lms_engine.harness import Harness

class GraphTests(unittest.TestCase):
    def test_success(self):
        self.assertEqual(run_graph(Harness.demo(), 'hello')['status'], 'success')

    def test_retry_success(self):
        h = Harness(lambda task, attempt: 'ok' if attempt == 3 else '', bool)
        result = run_graph(h, 'hello')
        self.assertEqual((result['status'], result['attempts']), ('success', 3))

    def test_maximum_exhaustion(self):
        result = run_graph(Harness(lambda task, attempt: '', bool), 'hello', 100)
        self.assertEqual((result['status'], result['attempts']), ('failed', 100))

    def test_verifier_exception(self):
        def verify(output):
            raise ValueError('private detail')
        result = run_graph(Harness(lambda task, attempt: 'ok', verify), 'hello', 2)
        self.assertEqual((result['status'], result['attempts']), ('failed', 2))
        self.assertEqual(result['error'], 'ValueError')
        self.assertNotIn('private detail', str(result))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            run_graph(Harness.demo(), '', 3)

    def test_mermaid(self):
        diagram = build_graph(Harness.demo()).get_graph().draw_mermaid()
        for node in ('plan', 'execute', 'verify'):
            self.assertIn(node, diagram)
