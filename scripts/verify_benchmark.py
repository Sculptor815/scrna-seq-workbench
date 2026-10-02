"""Verify the committed benchmark without downloading data or rewriting records."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {'kang', 'haber', 'paul', 'zeisel', 'baron'}
TEXT = {'.json', '.csv', '.md', '.txt', '.py', '.yaml', '.yml'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest_file(path):
    content = path.read_bytes()
    if path.suffix in TEXT:
        content = content.replace(b'\r\n', b'\n')
    return hashlib.sha256(content).hexdigest()


def verify_archive(content, expected_digest, expected_files, version):
    require(hashlib.sha256(content).hexdigest() == expected_digest, 'Frozen ZIP hash mismatch')
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'Duplicate ZIP members')
        require(set(names) == set(expected_files), 'Frozen ZIP file inventory mismatch')
        for name, expected in expected_files.items():
            require(hashlib.sha256(archive.read(name)).hexdigest() == expected,
                    f'Frozen source hash mismatch: {name}')
        require(json.loads(archive.read('plugin.json'))['version'] == version,
                'Frozen plugin version mismatch')
    return len(expected_files)


def rows(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def check_dimensions(manifest, qc, metrics, dimensions):
    require({x['dataset'] for x in manifest} == DATASETS, 'Dataset inventory mismatch')
    require(len(manifest) == len(qc) == len(dimensions) == 5, 'Expected five dimension records')
    require(len(metrics) == 20, 'Expected 20 historical metric rows')
    for source in manifest:
        name = source['dataset']
        q = next(x for x in qc if x['dataset'] == name)
        d = next(x for x in dimensions if x['dataset'] == name)
        require(source['cells'] == int(q['cells_in']) == d['input_cells'], f'{name}: input cells')
        require(source['genes'] == int(q['genes_in']) == d['input_genes'], f'{name}: input genes')
        require(int(q['cells_out']) == d['qc_cells'], f'{name}: QC cells')
        require(int(q['genes_out']) == d['qc_genes'], f'{name}: QC genes')
        require(int(q['removed_cells']) == d['input_cells'] - d['qc_cells'], f'{name}: excluded cells')
        require(d['analysis_cells'] == min(6000, d['qc_cells']), f'{name}: analysis cell cap')
        require(d['analysis_genes'] == d['qc_genes'], f'{name}: analysis genes')
        subset = [x for x in metrics if x['dataset'] == name]
        require(len(subset) == 4 and {(x['backend'], x['seed']) for x in subset} ==
                {('pca', '0'), ('scvi', '0'), ('scvi', '1'), ('scvi', '2')}, f'{name}: run inventory')
        for m in subset:
            require(int(m['cells']) == d['analysis_cells'] and int(m['genes']) == d['analysis_genes'],
                    f'{name}: metric dimensions')


def verify(root=ROOT):
    benchmark = root/'benchmarks'
    lock = json.loads((benchmark/'integrity_manifest.json').read_text(encoding='utf-8'))
    frozen = lock['frozen_plugin']
    original = json.loads((benchmark/'legacy/plugin_source_hashes.json').read_text(encoding='utf-8'))
    require(frozen['files'] == original, 'Frozen hashes differ from the historical record')
    files = verify_archive((benchmark/frozen['archive']).read_bytes(), frozen['archive_sha256'],
                           original, frozen['plugin_version'])
    for relative, expected in lock['artifact_hashes'].items():
        path = (benchmark/relative).resolve()
        require(path.is_relative_to(benchmark.resolve()), 'Artifact outside benchmark directory')
        require(path.is_file() and digest_file(path) == expected, f'Artifact hash mismatch: {relative}')
    actual = {p.relative_to(benchmark).as_posix() for folder in ('legacy', 'evidence')
              for p in (benchmark/folder).rglob('*') if p.is_file()}
    pinned = {p for p in lock['artifact_hashes'] if p.startswith(('legacy/', 'evidence/'))}
    require(actual == pinned, 'Benchmark file inventory changed')
    manifest = json.loads((benchmark/'legacy/data_manifest.json').read_text(encoding='utf-8'))
    qc = rows(benchmark/'legacy/qc_summary.csv')
    metrics = rows(benchmark/'legacy/metrics.csv')
    dimensions = json.loads((benchmark/'dimensions.json').read_text(encoding='utf-8'))['datasets']
    check_dimensions(manifest, qc, metrics, dimensions)
    total = 0
    for name in sorted(DATASETS):
        evidence = benchmark/'evidence'/name
        frame = rows(evidence/'embedding.csv')
        metric = next(x for x in metrics if x['dataset'] == name and x['backend'] == 'scvi' and x['seed'] == '0')
        require(len(frame) == int(metric['cells']), f'{name}: embedding size')
        require(len({x['cell_id'] for x in frame}) == len(frame), f'{name}: duplicate cell IDs')
        require(all(math.isfinite(float(x[k])) for x in frame for k in ('umap_1', 'umap_2')),
                f'{name}: nonfinite coordinates')
        proposals = {x['cluster']: x['cell_type_proposal'] for x in rows(evidence/'annotation_proposals.csv')}
        require(all(proposals[x['cluster']] == x['proposal'] for x in frame), f'{name}: proposal mapping')
        accuracy = sum(x['reference_broad'] == x['proposal'] for x in frame)/len(frame)
        coverage = sum(x['proposal'] != 'Unknown' for x in frame)/len(frame)
        require(math.isclose(accuracy, float(metric['annotation_accuracy_broad']), abs_tol=1e-12),
                f'{name}: agreement mismatch')
        require(math.isclose(coverage, float(metric['annotation_coverage']), abs_tol=1e-12),
                f'{name}: coverage mismatch')
        require(all(x['decision'] == 'pending' for x in rows(evidence/'hpa_review.template.csv')),
                f'{name}: historical review status changed')
        total += len(frame)
    print(f'PASS: {files} frozen source files, {len(lock["artifact_hashes"])} artifacts, '
          f'five dimension records, 20 runs and {total} seed-0 cells')
    print('Checks use committed records. Original counts, training and historical execution require external run files.')


if __name__ == '__main__':
    verify()
