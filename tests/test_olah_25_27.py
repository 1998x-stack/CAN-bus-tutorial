from pathlib import Path
import re, xml.etree.ElementTree as ET, unittest, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
class CheckChapters(unittest.TestCase):
    def test_chapters(self):
        for n in (25,26,27):
            p=(ROOT/f'{n}.html').read_text(encoding='utf-8')
            self.assertEqual(len(re.findall(r'<h1\b',p)),1)
            self.assertIn('name="viewport"',p)
            self.assertIn('aria-live="polite"',p)
            self.assertIn('id="references"',p)
            img=re.search(r'src="(assets/olah-ch[^"]+\.svg)"',p)
            self.assertIsNotNone(img)
            svg=ET.parse(ROOT/img.group(1)).getroot()
            self.assertIn('viewBox',svg.attrib)
            self.assertEqual(len(svg.findall('{http://www.w3.org/2000/svg}title')),1)
    def test_load(self):
        self.assertAlmostEqual((47+8*8)*1000/500000*100,22.2)
    @unittest.skipUnless(shutil.which('cc'),'No C compiler')
    def test_c_example(self):
        with tempfile.TemporaryDirectory() as t:
            exe=str(Path(t)/'can27')
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(ROOT/'examples/can_ch27_pipeline.c'),'-o',exe],check=True)
            self.assertIn('assertions passed',subprocess.check_output([exe],text=True))
