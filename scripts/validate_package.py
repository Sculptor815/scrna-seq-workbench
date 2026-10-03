"""Offline structural checks; host installation is a separate acceptance test."""
import ast
import json
import re
from pathlib import Path
from sync_adapters import synchronize

root=Path(__file__).resolve().parents[1]
plugin=root/'plugins'/'scrna-seq-workbench'
manifests=[plugin/'plugin.json',plugin/'.codex-plugin/plugin.json',plugin/'.claude-plugin/plugin.json']
data=[json.loads(p.read_text(encoding='utf-8')) for p in manifests]
assert len({(d['name'],d['version']) for d in data})==1
version=data[0]['version']
assert json.loads((root/'validation.json').read_text(encoding='utf-8'))['version']==version, 'Validation version differs'
assert f'Version **{version}' in (root/'README.md').read_text(encoding='utf-8'), 'README version differs'
assert re.search(r'^version: ["\x27]?'+re.escape(version)+r'["\x27]?$', (root/'CITATION.cff').read_text(encoding='utf-8'), re.M), 'Citation version differs'
assert version in (root/'RELEASE_NOTES.md').read_text(encoding='utf-8').splitlines()[0], 'Release notes version differs'
assert data[1]['skills']=='./skills/'
assert data[0]['extensions']['com.openai']['interface']['displayName']
for path in (root/'.agents/plugins/marketplace.json',root/'.claude-plugin/marketplace.json'):
    catalog=json.loads(path.read_text(encoding='utf-8'))
    for item in catalog['plugins']:
        source=item['source']
        rel=source['path'] if isinstance(source,dict) else source
        dest=(root/rel).resolve()
        assert dest.is_relative_to(root.resolve()) and dest==plugin.resolve()
        assert item['name']==data[0]['name']
        if 'version' in item:
            assert item['version']==data[0]['version']
skills=list((plugin/'skills').glob('*/SKILL.md'))
assert len(skills)==6
assert synchronize(check=True)==6
for skill in skills + list((root/'.dsh/skills').glob('*/SKILL.md')):
    text=skill.read_text(encoding='utf-8')
    assert text.startswith('---\n')
    front=text.split('---',2)[1]
    assert re.search(r'^name: '+re.escape(skill.parent.name)+r'$',front,re.M)
    assert re.search(r'^description: .+',front,re.M)
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if '://' not in target:
            dest=(skill.parent/target).resolve()
            assert dest.is_relative_to(root.resolve()) and dest.exists(),(skill,target)
for p in root.rglob('*.py'):
    if set(p.relative_to(root).parts) & {'work','runs','data','.git','.venv','__pycache__','.cache'}:
        continue
    ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
checked=0
for p in root.rglob('*.md'):
    if set(p.relative_to(root).parts) & {'work','runs','data','.git','.venv','__pycache__','.cache'}:
        continue
    checked+=1
    text=p.read_text(encoding='utf-8')
    assert not re.search(r'[\u3400-\u9fff]',text), f'Non-English Markdown: {p}'
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if '://' in target or target.startswith(('#','mailto:')):
            continue
        dest=(p.parent/target.split('#',1)[0]).resolve()
        assert dest.is_relative_to(root.resolve()) and dest.exists(),(p,target)
    for target in re.findall(r'(?:href|src)=["\x27]([^"\x27]+)["\x27]',text):
        if '://' in target or target.startswith(('#','mailto:','data:')):
            continue
        dest=(p.parent/target.split('#',1)[0]).resolve()
        assert dest.is_relative_to(root.resolve()) and dest.exists(),(p,target)
print(f'PASS: matching manifests, two marketplaces, six canonical skills, six Harness adapters, {checked} English Markdown files, links and Python syntax')
