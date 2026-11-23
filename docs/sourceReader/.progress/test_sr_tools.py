import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('sr_tools', Path(__file__).with_name('sr_tools.py'))
tools = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tools)


class SymbolToolsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = tools.symbols(['server/src/services/router.ts', 'server/src/providers/base.ts'])

    def test_real_function_and_method(self):
        self.assertEqual(len(tools.locate(self.rows, 'routeRequest')), 1)
        self.assertEqual(len(tools.locate(self.rows, 'BaseProvider.fetchWithTimeout')), 1)

    def test_registered_callback(self):
        rows = tools.symbols(['server/src/routes/proxy.ts'])
        matches = tools.locate(rows, "proxyRouter.post('/chat/completions')")
        self.assertEqual(len(matches), 1)
        self.assertLess(matches[0]['start'], matches[0]['end'])
        with tempfile.TemporaryDirectory(prefix='freellmapi-doc-test-', dir='/tmp') as directory:
            doc = Path(directory) / 'test.md'
            doc.write_text("`server/src/routes/proxy.ts` · `proxyRouter.post('/chat/completions')+9`\n")
            result = tools.verify([doc])
            self.assertEqual(result['errors'], [])

    def test_named_route_handler(self):
        rows = tools.symbols(['server/src/routes/proxy.ts'])
        match = tools.locate(rows, "proxyRouter.post('/decisions')")
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]['start'], match[0]['end'])

    def test_array_route_handler(self):
        rows = tools.symbols(['server/src/routes/proxy.ts'])
        symbol = "proxyRouter.get(['/models/:id', '/models/*rest'])"
        self.assertEqual(len(tools.locate(rows, symbol)), 1)

    def test_regex_route_handler(self):
        rows = tools.symbols(['server/src/routes/gemini.ts'])
        symbol = r"geminiRouter.post(/^\/models\/(.+):generateContent$/)"
        self.assertEqual(len(tools.locate(rows, symbol)), 1)
        with tempfile.TemporaryDirectory(prefix='freellmapi-doc-test-', dir='/tmp') as directory:
            doc = Path(directory) / 'test.md'
            doc.write_text(f'`server/src/routes/gemini.ts` · `{symbol}+0`\n')
            self.assertEqual(tools.verify([doc])['errors'], [])

    def test_factory_local_router_handler(self):
        rows = tools.symbols(['server/src/routes/update.ts'])
        match = tools.locate(rows, "createUpdateRouter.router.get('/release')")
        self.assertEqual(len(match), 1)
        self.assertLess(match[0]['start'], match[0]['end'])

    def test_production_then_test_fallback(self):
        rows = [dict(name='f', symbol='f', file='tests/f.ts'), dict(name='f', symbol='f', file='server/src/f.ts')]
        self.assertEqual(tools.locate(rows, 'f'), [rows[1]])
        self.assertEqual(tools.locate(rows[:1], 'f'), [rows[0]])

    def test_fenced_examples_are_not_links(self):
        self.assertEqual(list(tools.prose('```\n[x](missing.md)\n```\ntext')), [(4, 'text')])

    def test_path_boundaries(self):
        self.assertEqual(tools.PATH.findall('code_kernel.shutdown_kernels_for_delegated_child'), [])
        self.assertEqual(tools.PATH.findall('`client/src/App.tsx`'), ['client/src/App.tsx'])

    def test_url_route_is_not_repo_path(self):
        with tempfile.TemporaryDirectory(prefix='freellmapi-doc-test-', dir='/tmp') as directory:
            doc = Path(directory) / 'test.md'
            doc.write_text('| GET `/v1/openapi.json` | 文档 |\n`server/src/no-such-file.ts` 真的失效\n')
            result = tools.verify([doc], strict=True)
            self.assertEqual(len(result['errors']), 1)
            self.assertIn('no-such-file', result['errors'][0])

    def test_negative_controls(self):
        with tempfile.TemporaryDirectory(prefix='freellmapi-doc-test-', dir='/tmp') as directory:
            doc = Path(directory) / 'test.md'
            doc.write_text('# 检查\n`server/src/services/router.ts` · `routeRequest+0`\n')
            self.assertEqual(tools.verify([doc])['errors'], [])
            doc.write_text('# 检查\n`server/src/services/router.ts` · `routeRequest+999999`\n`server/src/providers/base.ts` · `routeRequest+0`\n[broken](missing.md)\n[x](#missing)\n')
            self.assertEqual(len(tools.verify([doc])['errors']), 4)


if __name__ == '__main__':
    unittest.main()
