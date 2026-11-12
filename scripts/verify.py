"""Focused invariant checks: blind output, license naming, SVG/WOFF2 geometry."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from PIL import Image,PngImagePlugin
from fontTools.ttLib import TTFont,newTable
from common import ROOT,rename_binary,FORBIDDEN,candidate_faces,ROUNDED_CORE,FACES
from blindcheck import clean_png,check
from icons import parse_svg,validate,huge_svg,build_icons
from newlabel import labels

GOOD='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18"/></svg>'

class Invariants(unittest.TestCase):
    def setUp(self):
        (ROOT/'build').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'build');self.base=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_all_names_including_copyright_urls_and_private_ids(self):
        font=TTFont();font['name']=newTable('name');font['name'].names=[]
        for i in [0,1,3,4,6,7,10,13,14,16,25,256]:font['name'].setName('Inter Source Serif Fira Code',i,3,1,0x409)
        rename_binary(font,'Strata Sans')
        self.assertFalse(any(FORBIDDEN.search(n.toUnicode()) for n in font['name'].names))
    def test_reject_fills_transforms_and_scripts(self):
        self.assertEqual(validate(ET.fromstring(GOOD)),[])
        for svg in [GOOD.replace('fill="none"','fill="black"'),GOOD.replace('<path ','<path transform="rotate(2)" '),GOOD.replace('<path d="M3 12h18"/>','<script/>')]:
            self.assertTrue(validate(ET.fromstring(svg)))
    def test_blind_png_roundtrip_and_metadata(self):
        image=Image.effect_noise((512,256),100).convert('RGB');path=self.base/'amber-reed-123.png'
        meta=PngImagePlugin.PngInfo();meta.add_text('face','Inter')
        image.save(path,pnginfo=meta);clean_png(path)
        self.assertEqual(check(self.base),1)
        with Image.open(path) as decoded:self.assertEqual(image.tobytes(),decoded.tobytes())
        (self.base/'bad.json').write_text('{"font":"baseline"}')
        with self.assertRaises(ValueError):check(self.base)
    def test_icon_render_resize_preserves_child_geometry(self):
        from specimens import re_size
        resized=re_size(GOOD.replace('<path d="M3 12h18"/>','<rect x="3" y="3" width="18" height="18"/>'),16)
        root=ET.fromstring(resized)
        rect=list(root)[0]
        self.assertEqual((root.get('width'),rect.get('width'),rect.get('height')),('16','18','18'))
    def test_labels_are_unique_and_preserved(self):
        path=self.base/'map.json';first=labels(path,['one','two']);self.assertNotEqual(first['one'],first['two'])
        self.assertEqual(labels(path,['one'])['one'],first['one'])
    def test_optional_rounded_discovery_and_numeric_coverage(self):
        self.assertEqual(candidate_faces(self.base),FACES)
        (self.base/'fonts/sans-rounded').mkdir(parents=True)
        self.assertIn('sans-rounded',candidate_faces(self.base))
        self.assertTrue(set(map(ord,'72°−3°104°F18℃08:00100%'))<=ROUNDED_CORE)
        self.assertNotIn(ord('a'),ROUNDED_CORE)
    def test_new_rounded_sources_invalidate_three_face_build(self):
        import json
        from unittest.mock import patch
        from gate import checked_build
        out=self.base/'build/probe';out.mkdir(parents=True)
        (out/'build.json').write_text(json.dumps({'faces':dict.fromkeys(FACES)}))
        (self.base/'fonts/sans-rounded').mkdir(parents=True)
        with patch('gate.ROOT',self.base),patch('gate.candidate',return_value=self.base):
            with self.assertRaisesRegex(ValueError,'Changed face set'):checked_build('probe')
    def test_reviewer_identity_words_are_rejected(self):
        from blindcheck import PATTERN
        for word in ['lumen','quartz','opus','sol','claude','codex','gpt']:
            self.assertIsNotNone(PATTERN.search(word.upper().encode()))
    def test_review_assembly_excludes_engine_details(self):
        import json
        from review_set import assemble
        stage=self.base/'stage';stage.mkdir()
        filename='fern-pine-123-01.png'
        Image.new('RGB',(8,8),'white').save(stage/filename)
        row={'label':'fern-pine-123','image':filename,'sheet':'10','theme':'light','engine':'webkit','width':8,'height':8,'scale':2}
        (stage/'index.json').write_text(json.dumps({'sheets':[row]}))
        out=self.base/'round/renders';guide=out.parent/'SHEETS.md'
        self.assertEqual(assemble([stage],out,guide),1)
        self.assertNotIn('engine',json.loads((out/'index.json').read_text())['sheets'][0])
        self.assertNotIn('webkit',guide.read_text())
    def test_regenerated_outline_comparison_checks_components_and_points(self):
        from compare_outlines import sources
        a=self.base/'a';b=self.base/'b';a.mkdir();b.mkdir()
        text='<glyph name="one"><advance width="10"/><outline><contour><point x="1" y="2" type="line"/></contour><component base="two" xOffset="3"/></outline></glyph>'
        (a/'one.glif').write_text(text);(b/'one.glif').write_text(text.replace('x="1"','x="1.0"'))
        self.assertEqual(sources(a,b)['glyph_records'],1)
        (b/'one.glif').write_text(text.replace('xOffset="3"','xOffset="4"'))
        with self.assertRaises(ValueError):sources(a,b)
    def test_iconfont_is_expanded_stroke_not_open_centerline(self):
        source=self.base/'input';source.mkdir();(source/'line.svg').write_text(GOOD)
        build_icons(source,self.base/'output')
        font=TTFont(self.base/'output/StrataIcons.woff2');glyph=font['glyf'][font.getBestCmap()[0xe000]]
        self.assertGreater(glyph.numberOfContours,0);self.assertGreater(glyph.yMax-glyph.yMin,70)
        self.assertGreater(glyph.xMax-glyph.xMin,700)
    def test_free_package_is_parsed_as_data(self):
        self.assertEqual(validate(ET.fromstring(huge_svg('Sun03'))),[])

def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Invariants)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)

if __name__=='__main__':main()
