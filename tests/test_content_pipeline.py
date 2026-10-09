import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_site', ROOT / 'scripts/build_site.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class ContentPipelineTests(unittest.TestCase):
    def test_new_content_is_a_draft_and_duplicate_preserves_the_author_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            (root / 'content').mkdir()
            shutil.copy2(ROOT / 'scripts/new_content.py', root / 'scripts/new_content.py')
            (root / 'content/catalog.json').write_text('[]', encoding='utf-8')
            command = [sys.executable, str(root / 'scripts/new_content.py'), 'blog', 'sample-note', 'Sample', '--description', 'A small example']
            subprocess.run(command, check=True, capture_output=True)
            catalog = json.loads((root / 'content/catalog.json').read_text(encoding='utf-8'))
            self.assertTrue(catalog[0]['draft'])
            source = root / catalog[0]['source']
            source.write_text('Author text to preserve', encoding='utf-8')
            duplicate = subprocess.run(command, capture_output=True)
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertEqual(source.read_text(encoding='utf-8'), 'Author text to preserve')
            self.assertEqual(len(json.loads((root / 'content/catalog.json').read_text(encoding='utf-8'))), 1)

    def test_code_and_prose_cannot_inject_markup_or_script_links(self):
        content, _ = build.markdown('<script>alert(1)</script>\n\n```html\n<img src=x onerror=alert(1)>\n```')
        self.assertNotIn('<script>', content)
        self.assertIn('&lt;script&gt;', content)
        self.assertNotIn('<img src=x', content)
        with self.assertRaises(ValueError):
            build.markdown('[link](javascript:alert)')

    def test_incomplete_code_fence_does_not_silently_publish_truncated_content(self):
        with self.assertRaises(ValueError):
            build.markdown('## Reproduction\n\n```python\nprint(1)')

    def test_images_render_and_reject_missing_unsafe_or_external_paths(self):
        content, _ = build.markdown('Intro\n![Nest <example>](/assets/images/nest-overview.jpg)')
        self.assertIn('<p>Intro</p>', content)
        self.assertIn('alt="Nest &lt;example&gt;"', content)
        self.assertIn('<figcaption>Nest &lt;example&gt;</figcaption>', content)
        for invalid in ('![](/assets/images/nest-overview.jpg)', '![x](javascript:alert)', '![x](https://example.com/x.jpg)', '![x](/assets/images/missing.jpg)', '![x](/assets/images/../../README.md)'):
            with self.subTest(image=invalid), self.assertRaises(ValueError):
                build.markdown(invalid)

    def test_documented_python_lesson_examples_run_without_dependencies(self):
        import re
        source = (ROOT / 'content/learn/cache-identity.md').read_text(encoding='utf-8')
        samples = re.findall(r'```python\n(.*?)\n```', source, re.S)
        self.assertEqual(len(samples), 2)
        for sample in samples:
            result = subprocess.run([sys.executable, '-c', sample], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
