from __future__ import annotations
import re
import numpy as np
import pandas as pd
from scipy import sparse
from .common import load_counts, require_columns, read_json, write_json

DEFAULTS = {"min_genes": 200, "max_genes": None, "min_counts": 1,
            "max_counts": None, "max_counts_quantile": None,
            "max_pct_mt": None, "max_pct_hb": None}


def config_for(config, sample):
    unknown = set(config) - {"defaults", "per_sample", "min_cells_per_gene"}
    if unknown:
        raise ValueError(f"Unknown QC config fields: {unknown}")
    overrides = config.get("per_sample", {}).get(str(sample), {})
    for block in (config.get("defaults", {}), overrides):
        if set(block) - set(DEFAULTS):
            raise ValueError("Unknown QC threshold name")
    cfg = DEFAULTS | config.get("defaults", {}) | overrides
    for key, value in cfg.items():
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int,float))
                                  or not np.isfinite(value) or value < 0):
            raise ValueError(f"Invalid QC threshold {key}")
    q = cfg["max_counts_quantile"]
    if q is not None and not 0 < q < 1:
        raise ValueError("max_counts_quantile must be between 0 and 1")
    for key in ("max_pct_mt", "max_pct_hb"):
        if cfg[key] is not None and cfg[key] > 100:
            raise ValueError("Percentage threshold cannot exceed 100")
    for lo,hi in (("min_genes","max_genes"),("min_counts","max_counts")):
        if cfg[lo] is not None and cfg[hi] is not None and cfg[lo] >= cfg[hi]:
            raise ValueError(f"{lo} must be smaller than {hi}")
    if cfg["max_counts"] is not None and q is not None:
        raise ValueError("Choose max_counts or max_counts_quantile, not both")
    return cfg


def metrics(a, species):
    x = a.layers["counts"]
    total = np.asarray(x.sum(axis=1)).ravel()
    genes = np.asarray((x > 0).sum(axis=1)).ravel()
    a.obs["total_counts"] = total
    a.obs["n_genes_by_counts"] = genes
    patterns = {"human": (r"^MT-", r"^RP[SL]", r"^HB(?:A[12]|B|D|E1|G[12]|Z)$"),
                "mouse": (r"^mt-", r"^Rp[sl]", r"^Hb[ab]-")}[species]
    matched = {}
    for key, pattern in zip(("mt","ribo","hb"), patterns):
        mask = np.array([bool(re.match(pattern, str(g))) for g in a.var_names])
        matched[key] = int(mask.sum()); a.var[key] = mask
        c = np.asarray(x[:, mask].sum(axis=1)).ravel()
        a.obs[f"pct_counts_{key}"] = np.divide(100*c, total, out=np.zeros_like(total,dtype=float), where=total>0)
    return matched


def filter_cells(obs, sample_key, config):
    require_columns(obs, [sample_key])
    extra = set(config.get("per_sample", {})) - set(obs[sample_key].astype(str))
    if extra:
        raise ValueError(f"Threshold overrides name absent samples: {extra}")
    reasons = pd.Series("", index=obs.index, dtype=object)
    applied, suggestions = {}, {}
    for sample, block in obs.groupby(sample_key, observed=True, sort=True):
        cfg = config_for(config, sample)
        if cfg["max_counts_quantile"] is not None:
            cfg["max_counts"] = float(block["total_counts"].quantile(cfg["max_counts_quantile"]))
        applied[str(sample)] = cfg
        suggestions[str(sample)] = {}
        for m in ("total_counts","n_genes_by_counts","pct_counts_mt"):
            vals = block[m]; med = float(vals.median()); mad = float((vals-med).abs().median())
            suggestions[str(sample)][m] = {"median":med,"mad":mad,
                                          "status":"degenerate_mad" if mad == 0 else "descriptive_only",
                                          "suggested_lower":max(0,med-3*1.4826*mad) if mad else None,
                                          "suggested_upper":med+3*1.4826*mad if mad else None}
        checks = [(block.total_counts <= 0,"zero_counts")]
        for key,col,lower in (("min_genes","n_genes_by_counts",True), ("max_genes","n_genes_by_counts",False),
                              ("min_counts","total_counts",True), ("max_counts","total_counts",False),
                              ("max_pct_mt","pct_counts_mt",False), ("max_pct_hb","pct_counts_hb",False)):
            if cfg[key] is not None:
                checks.append((block[col] < cfg[key] if lower else block[col] >= cfg[key],key))
        for bad, label in checks:
            idx=block.index[bad & reasons.loc[block.index].eq("")]
            reasons.loc[idx]=label
    return reasons, applied, suggestions


def run(args, report):
    a=load_counts(args.input, args.metadata, allow_x=True)
    if args.single_sample:
        if args.sample_key in a.obs and not a.obs[args.sample_key].astype(str).eq(args.single_sample).all():
            raise ValueError("--single-sample conflicts with existing sample IDs")
        a.obs[args.sample_key]=args.single_sample
    require_columns(a.obs,[args.sample_key])
    if a.obs[args.sample_key].nunique()==1:
        report["warnings"].append("One sample is not evidence of independent biological replicates.")
    cfg=read_json(args.config)
    matched=metrics(a,args.species)
    validate_gene_sets(matched, cfg, a.obs[args.sample_key].unique(), report)
    reasons, applied, suggestions=filter_cells(a.obs,args.sample_key,cfg)
    if args.doublets:
        import scanpy as sc
        require_columns(a.obs,[args.capture_key])
        if not 0 < args.expected_doublet_rate < 1:
            raise ValueError("Expected doublet rate must lie in (0,1)")
        a.obs["doublet_score"]=np.nan; a.obs["predicted_doublet"]=False
        for capture, group in a.obs.groupby(args.capture_key,observed=True):
            # Every physical capture is scored separately; sample/donor are not interchangeable.
            idx=group.index[reasons.loc[group.index].eq("")]
            if len(idx)<30:
                raise ValueError(f"Capture {capture}: fewer than 30 QC-eligible cells; do not silently skip requested doublet scoring")
            sub=a[idx].copy(); sub.X=sub.layers["counts"].copy()
            sc.pp.scrublet(sub,expected_doublet_rate=args.expected_doublet_rate,random_state=args.seed)
            a.obs.loc[idx,"doublet_score"]=sub.obs["doublet_score"]
            a.obs.loc[idx,"predicted_doublet"]=sub.obs["predicted_doublet"]
        if args.remove_doublets:
            reasons.loc[a.obs["predicted_doublet"] & reasons.eq("")]="predicted_doublet"
    elif args.remove_doublets:
        raise ValueError("--remove-doublets requires --doublets")
    ledger=a.obs.copy(); ledger.index.name="cell_id"
    ledger["retained"]=reasons.eq(""); ledger["first_exclusion_reason"]=reasons
    ledger.to_csv(args.outdir / "cell_qc.csv")
    write_json(args.outdir / "threshold_suggestions.json",suggestions)
    report.update(n_cells_in=a.n_obs,n_genes_in=a.n_vars,matched_gene_sets=matched,applied_thresholds=applied,
                  exclusion_counts=reasons[reasons.ne("")].value_counts().to_dict())
    report["warnings"].append("MAD suggestions are descriptive, not automatically applied; all metrics use prefilter genes.")
    if args.inspect_only:
        report.update(mode="inspect_only",n_cells_out=None)
        return
    filtered=a[reasons.eq("")].copy()
    if filtered.n_obs==0:
        raise ValueError("QC removed every cell; review cell_qc.csv and thresholds")
    nmin=cfg.get("min_cells_per_gene",3)
    if type(nmin) is not int or nmin<1:
        raise ValueError("min_cells_per_gene must be a positive integer")
    present=np.asarray((filtered.layers["counts"]>0).sum(axis=0)).ravel()
    pd.DataFrame({"gene_id":a.var_names,"n_retained_cells_expressing":present,"retained":present>=nmin}).to_csv(args.outdir/"gene_qc.csv",index=False)
    filtered=filtered[:,present>=nmin].copy()
    if filtered.n_vars<3:
        raise ValueError("Fewer than three genes remain")
    filtered.X=filtered.layers["counts"].copy(); filtered.raw=None
    filtered.uns["scrna_species"]=args.species
    filtered.uns["scrna_expression"]="X and counts: raw UMI, after cell/gene QC; all retained genes"
    filtered.write_h5ad(args.outdir/"filtered.h5ad")
    report.update(n_cells_out=filtered.n_obs,n_genes_out=filtered.n_vars,
                  retention_by_sample={str(s):{"input":int(len(g)),"retained":int(reasons.loc[g.index].eq("").sum())}
                                       for s,g in a.obs.groupby(args.sample_key,observed=True)})
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(12,3))
    for ax,m in zip(axes,("total_counts","n_genes_by_counts","pct_counts_mt")):
        for s,g in a.obs.groupby(args.sample_key,observed=True):
            ax.hist(g[m],bins=40,histtype="step",label=str(s))
        ax.set_title(m); ax.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(args.outdir/"qc_by_sample.png",dpi=120); plt.close(fig)


def validate_gene_sets(matched, config, samples, report):
    for key in ("mt", "hb", "ribo"):
        if matched[key]:
            continue
        report["warnings"].append(f"No {key} symbols matched; its zero percentage is not evidence of absence. Check identifiers.")
        threshold = f"max_pct_{key}"
        if threshold in DEFAULTS and any(config_for(config, s)[threshold] is not None for s in samples):
            raise ValueError(f"{key} filter requested but no matching genes; map identifiers or revise the explicit policy")
