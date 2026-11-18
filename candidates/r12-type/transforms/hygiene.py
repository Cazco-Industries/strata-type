"""Source-name hygiene. Copyright lines stay verbatim."""
import re


def sans(folder):
    ds = folder / 'StrataSans.designspace'
    text = ds.read_text()
    text = text.replace('<string>Inter Display</string>', '<string>Strata Sans Display</string>')
    text = text.replace('<string>Inter</string>', '<string>Strata Sans</string>')
    ds.write_text(text)


def serif(folder):
    for fea in sorted(folder.glob('*.ufo/features.fea')):
        text = fea.read_text()
        text = re.sub(r'^nameid 7 "[^"]*";\n', '', text, flags=re.M)
        text = text.replace('nameid 25 "SourceSerif4Roman";', 'nameid 25 "StrataSerifRoman";')
        text = re.sub(r'PS Name: SourceSerif4-', 'PS Name: StrataSerif-', text)
        text = text.replace('@CASE_SOURCE', '@CASE_FROM')
        fea.write_text(text)
