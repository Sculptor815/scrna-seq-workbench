from __future__ import annotations

import hashlib
import json
import platform
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hashes(path):
    p = Path(path)
    if not p.exists():
        raise ValueError(f"Input does not exist: {p}")
    files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
    return {str(x.resolve()): sha256(x) for x in files}


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False,
                                    default=lambda x: str(x) if isinstance(x, Path) else x.item()), encoding="utf-8")


def read_json(path):
    def invalid(value):
        raise ValueError(f"Non-finite JSON value: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), parse_constant=invalid)


def versions():
    result = {"python": platform.python_version(), "platform": platform.platform()}
    for p in ("numpy", "pandas", "scipy", "scanpy", "anndata", "scvi-tools", "torch", "pydeseq2", "igraph"):
        try:
            result[p] = version(p)
        except PackageNotFoundError:
            result[p] = None
    return result


@contextmanager
def stage_run(stage, outdir, parameters, inputs):
    out = Path(outdir)
    inputs = list(inputs)
    for source in inputs:
        if source is not None and Path(source).is_dir() and out.resolve().is_relative_to(Path(source).resolve()):
            raise ValueError("Output directory must be outside input directories")
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"Output directory is not empty; choose a new run directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    now = lambda: datetime.now(timezone.utc).isoformat()
    report = {"schema_version": "1.0", "stage": stage, "status": "running", "started_utc": now(),
              "parameters": parameters, "versions": versions(), "inputs": {}, "artifacts": {},
              "warnings": [], "source_sha256": source_hashes()}
    write_json(out / "report.json", report)
    try:
        for p in inputs:
            if p is not None:
                report["inputs"].update(hashes(p))
        write_json(out / "report.json", report)
        yield report
        if report["status"] == "running":
            report["status"] = "complete"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        report["finished_utc"] = now()
        report["artifacts"] = {p.relative_to(out).as_posix(): sha256(p)
                               for p in sorted(out.rglob("*")) if p.is_file() and p != out / "report.json"}
        write_json(out / "report.json", report)


def validate_counts(x):
    import numpy as np
    from scipy import sparse
    if len(x.shape) != 2 or min(x.shape) == 0:
        raise ValueError("Counts must be a nonempty cells-by-genes matrix")
    d = x.data if sparse.issparse(x) else np.asarray(x).ravel()
    if not np.isfinite(d).all() or np.any(d < 0):
        raise ValueError("Counts must be finite and nonnegative")
    if not np.allclose(d, np.rint(d), rtol=0, atol=1e-6):
        raise ValueError("Counts must be integer-valued; normalized expression is not raw UMI counts")
    if not np.any(d > 0):
        raise ValueError("Counts contain no positive entries")


def source_hashes():
    root = Path(__file__).resolve().parents[2]
    files = list((root / "scripts").rglob("*.py")) + list(root.glob("requirements*.txt"))
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(files)}


def require_columns(obs, keys):
    for key in keys:
        if not key or key not in obs:
            raise ValueError(f"Missing metadata column: {key}")
        if obs[key].isna().any() or obs[key].astype(str).str.strip().eq("").any():
            raise ValueError(f"Missing/empty metadata values: {key}")


def load_counts(path, metadata=None, allow_x=False):
    import anndata as ad
    import pandas as pd
    p = Path(path)
    if p.suffix == ".h5ad":
        a = ad.read_h5ad(p)
    else:
        import scanpy as sc
        a = sc.read_10x_mtx(p, var_names="gene_symbols", make_unique=False) if p.is_dir() else sc.read_10x_h5(p)
    if not a.obs_names.is_unique or not a.var_names.is_unique:
        raise ValueError("Cell and gene identifiers must be unique; resolve duplicates with an explicit mapping")
    if "counts" not in a.layers:
        if not allow_x:
            raise ValueError("Missing layers['counts']; declare raw X via QC first")
        validate_counts(a.X)
        a.layers["counts"] = a.X.copy()
    validate_counts(a.layers["counts"])
    if metadata:
        meta = pd.read_csv(metadata, dtype=str).set_index("cell_id")
        if not meta.index.is_unique or set(meta.index) != set(a.obs_names):
            raise ValueError("Metadata must match all cell IDs exactly, one row per cell")
        meta = meta.loc[a.obs_names]
        for col in meta:
            if col in a.obs and not a.obs[col].astype(str).equals(meta[col]):
                raise ValueError(f"Metadata conflicts with existing column: {col}")
            a.obs[col] = meta[col]
    return a


def lognormalize(a):
    import scanpy as sc
    # Rebuild from declared counts. Never guess what an inherited .raw contains.
    a.X = a.layers["counts"].copy()
    a.raw = None
    a.uns.pop("log1p", None)
    sc.pp.normalize_total(a, target_sum=10000)
    sc.pp.log1p(a)
    a.layers["lognorm"] = a.X.copy()
    a.uns["scrna_expression"] = "X and lognorm: log1p(CP10K); counts: unnormalized UMI"


def safe_name(value):
    # Stable unique suffix avoids collisions between labels after sanitizing.
    s = str(value)
    return re.sub(r"[^a-zA-Z0-9_-]", "_", s)[:60] + "_" + hashlib.sha256(s.encode()).hexdigest()[:8]
