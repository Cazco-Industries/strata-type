"""Source-name hygiene. Copyright lines stay verbatim."""
import plistlib
import re
from fontTools.designspaceLib import DesignSpaceDocument


def sans(folder):
    ds_path = folder / 'StrataSans.designspace'
    text = ds_path.read_text()
    text = text.replace('<string>Inter Display</string>', '<string>Strata Sans Display</string>')
    text = text.replace('<string>Inter</string>', '<string>Strata Sans</string>')
    ds_path.write_text(text)
    ds = DesignSpaceDocument.fromfile(ds_path)
    for inst in ds.instances:
        opsz = inst.location.get('Optical size') if inst.location else None
        if opsz == 32 or (inst.name and 'Display' in inst.name):
            style = inst.styleName or 'Regular'
            if not style.startswith('Display'):
                new_style = 'Display' if style == 'Regular' else f'Display {style}'
                inst.styleName = new_style
                inst.postScriptFontName = 'StrataSans-' + re.sub(r'[^A-Za-z0-9]', '', new_style)
                props = inst.lib.get('com.schriftgestaltung.properties')
                if isinstance(props, list):
                    for pair in props:
                        if isinstance(pair, list) and len(pair) == 2 and pair[0] == 'WWSSubfamilyName':
                            pair[1] = new_style
    ds.write(ds_path)


def serif(folder):
    for fea in sorted(folder.glob('*.ufo/features.fea')):
        text = fea.read_text()
        text = re.sub(r'^nameid 7 "[^"]*";\n', '', text, flags=re.M)
        text = text.replace('nameid 25 "SourceSerif4Roman";', 'nameid 25 "StrataSerifRoman";')
        text = re.sub(r'PS Name: SourceSerif4-', 'PS Name: StrataSerif-', text)
        text = text.replace('@CASE_SOURCE', '@CASE_FROM')
        text = text.replace('name "SmallText";', 'name "SmText";')
        fea.write_text(text)
    info_path = folder / 'StrataSerif-m04.ufo' / 'fontinfo.plist'
    if info_path.is_file():
        info = plistlib.loads(info_path.read_bytes())
        if info.get('styleName') == 'Text 1':
            info['styleName'] = 'Regular'
            info['postscriptFontName'] = 'StrataSerif-Regular'
            info['postscriptFullName'] = 'Strata Serif Regular'
            info['openTypeNameCompatibleFullName'] = 'Strata Serif Regular'
            info['openTypeNameUniqueID'] = 'StrataSerif-Regular;27.0.0.0'
            info_path.write_bytes(plistlib.dumps(info))
