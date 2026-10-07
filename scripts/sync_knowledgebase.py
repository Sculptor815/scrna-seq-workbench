"""Ship the owner-maintained policy inside the standalone plugin, without drift."""
import argparse
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'collaboration/knowledgebase/README.md'
TARGET = ROOT / 'plugins/scrna-seq-workbench/references/knowledgebase.md'


def synchronize(check=False):
    expected = SOURCE.read_text(encoding='utf-8').replace('\r\n', '\n')
    def rewrite(match):
        target = match.group(1)
        if '://' in target or target.startswith(('#', 'mailto:')):
            return match.group(0)
        path, sep, fragment = target.partition('#')
        resolved = (SOURCE.parent / path).resolve()
        plugin = ROOT / 'plugins/scrna-seq-workbench'
        if not resolved.is_relative_to(plugin.resolve()) or not resolved.exists():
            raise ValueError(f'Knowledge link must resolve inside the shipped plugin: {target}')
        relative = Path(os.path.relpath(resolved, TARGET.parent)).as_posix()
        return '](' + relative + (sep + fragment if sep else '') + ')'
    expected = re.sub(r'\]\(([^)]+)\)', rewrite, expected)
    current = TARGET.read_text(encoding='utf-8') if TARGET.exists() else None
    if current != expected:
        if check:
            raise ValueError('Bundled knowledge base is stale; run python scripts/sync_knowledgebase.py')
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(expected, encoding='utf-8', newline='\n')
    return TARGET


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    synchronize(args.check)
    print('PASS: bundled knowledge base ' + ('checked' if args.check else 'synchronized'))
