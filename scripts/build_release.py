"""Build a source-only ZIP, including dot directories but excluding local data."""
import argparse
import hashlib
import os
import json
import subprocess
import sys
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'__pycache__', '.git', '.venv', '.pytest_cache', '.cache', 'runs', 'data', 'work', 'hpa_cache'}
SUFFIXES = {'.py', '.md', '.json', '.yaml', '.yml', '.txt', '.csv', '.png', '.html', '.cff'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--format', choices=['repository','plugin'], default='repository')
    args = ap.parse_args()
    if args.output.exists():
        raise ValueError('Release already exists; choose a new output path')
    subprocess.run([sys.executable, str(ROOT/'scripts/validate_package.py')], check=True)
    subprocess.run([sys.executable, str(ROOT/'scripts/verify_benchmark.py')], check=True)
    source = ROOT if args.format == 'repository' else ROOT/'plugins/scrna-seq-workbench'
    files = []
    for directory, subdirs, names in os.walk(source):
        subdirs[:] = sorted(d for d in subdirs if d not in SKIP and not (Path(directory)/d).is_symlink())
        for name in sorted(names):
            p = Path(directory)/name
            frozen_archive = p == ROOT/'benchmarks/frozen/plugin-v0.1.0.zip'
            if not p.is_symlink() and not name.startswith('.env') and (p.suffix in SUFFIXES or name in {'LICENSE', '.gitignore', '.gitattributes'} or frozen_archive):
                files.append(p)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'x', zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, (Path(source.name) / p.relative_to(source)).as_posix())
    with zipfile.ZipFile(args.output) as z:
        assert z.testzip() is None
        if args.format == 'repository':
            assert sum('/plugins/scrna-seq-workbench/skills/' in n and n.endswith('/SKILL.md') for n in z.namelist()) == 6
            assert sum('/.dsh/skills/' in n and n.endswith('/SKILL.md') for n in z.namelist()) == 6
            assert any('/.agents/plugins/marketplace.json' in n for n in z.namelist())
            assert f'{source.name}/benchmarks/frozen/plugin-v0.1.0.zip' in z.namelist()
            assert f'{source.name}/benchmarks/integrity_manifest.json' in z.namelist()
        else:
            assert sum(n.endswith('/SKILL.md') for n in z.namelist()) == 6
            assert not any('/benchmarks/' in n for n in z.namelist()), 'Evaluation must stay outside the plugin'
            assert not any(n.endswith('/score.py') for n in z.namelist()), 'Scoring must stay outside the plugin'
            assert f'{source.name}/plugin.json' in z.namelist()
            assert f'{source.name}/.claude-plugin/plugin.json' in z.namelist()
        prefix=f'{source.name}/' + ('plugins/scrna-seq-workbench/' if args.format == 'repository' else '')
        versions={json.loads(z.read(prefix+p))['version'] for p in
                  ('plugin.json','.codex-plugin/plugin.json','.claude-plugin/plugin.json')}
        assert len(versions)==1, 'Packaged plugin versions disagree'
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix('.zip.sha256').write_text(f'{digest}  {args.output.name}\n', encoding='utf-8')
    print(f'{len(files)} files; {args.output.stat().st_size} bytes; SHA256 {digest}')

if __name__ == '__main__':
    main()
