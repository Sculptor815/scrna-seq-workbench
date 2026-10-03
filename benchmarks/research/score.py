"""Calculate developer ratings from a completed review; never run an analysis."""
import argparse
import hashlib
import json
from pathlib import Path

WEIGHTS = dict(data_suitability=20, analysis_relevance=25, evidence_reasoning=30,
               user_usefulness=15, interaction_efficiency=10)


def calculate(record):
    if record.get('schema_version') != '1.0':
        raise ValueError('Unsupported review schema')
    for key in ('case_id', 'run_id'):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError(f'Missing {key}')
    if record.get('review_status') not in ('pending', 'final'):
        raise ValueError('Invalid review_status')
    if record.get('completion') not in ('complete', 'incomplete', 'execution_error'):
        raise ValueError('Invalid completion')
    errors = record.get('critical_errors')
    if not isinstance(errors, list) or any(not isinstance(x, str) or not x.strip() for x in errors):
        raise ValueError('critical_errors must be a list of explanations')
    ready = record['review_status'] == 'final' and record['completion'] == 'complete'
    result = dict(case_id=record['case_id'], run_id=record['run_id'],
                  completion=record['completion'], review_status=record['review_status'],
                  eligible=False, weighted_score=None, critical_errors=errors,
                  weights=WEIGHTS, scope='Developer review calculation; not independent scientific verification')
    if not ready:
        return result
    records = record.get('review_record_paths')
    if not isinstance(records, list) or any(not isinstance(x, str) or not x.strip() for x in records) or len(set(records)) < 2:
        raise ValueError('Retain paths to at least two independent review records')
    dimensions = record.get('dimensions', {})
    if set(dimensions) != set(WEIGHTS):
        raise ValueError('All five dimensions are required')
    for name, dimension in dimensions.items():
        score = dimension.get('score')
        if type(score) is not int or not 0 <= score <= 4:
            raise ValueError(f'{name}: score must be an integer from 0 to 4')
        if not isinstance(dimension.get('rationale'), str) or not dimension['rationale'].strip():
            raise ValueError(f'{name}: rationale required')
        evidence = dimension.get('evidence')
        if not isinstance(evidence, list) or not evidence or any(not isinstance(x, str) or not x.strip() for x in evidence):
            raise ValueError(f'{name}: evidence paths or source locators required')
    result['weighted_score'] = sum(WEIGHTS[k] * dimensions[k]['score'] / 4 for k in WEIGHTS)
    result['eligible'] = not errors
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    raw = args.record.read_bytes()
    record = json.loads(raw)
    result = calculate(record)
    result['record_sha256'] = hashlib.sha256(raw).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')


if __name__ == '__main__':
    main()
