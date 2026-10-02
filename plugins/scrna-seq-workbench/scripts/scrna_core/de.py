import numpy as np
import pandas as pd
from .common import load_counts, require_columns, safe_name


def pseudobulk(a, celltype_key, donor_key, condition_key, case, control, design="paired", min_cells=20, min_donors=3):
    if not case or not control or case==control:
        raise ValueError("Case and control must be distinct nonempty condition names")
    if min_cells<1 or min_donors<3:
        raise ValueError("This release requires at least 3 donors per contrast and positive min_cells")
    require_columns(a.obs,[celltype_key,donor_key,condition_key])
    if {case,control}-set(a.obs[condition_key].astype(str)):
        raise ValueError("Requested contrast level is absent")
    if design not in ("paired","unpaired"):
        raise ValueError("Choose paired or unpaired")
    obs=a.obs.copy()
    for k in [celltype_key,donor_key,condition_key]:
        obs[k]=obs[k].astype(str)
    obs[celltype_key]=obs[celltype_key].str.strip()
    selected=obs[condition_key].isin([case,control])
    if design=="unpaired" and (obs[selected].groupby(donor_key)[condition_key].nunique()>1).any():
        raise ValueError("Unpaired mode requires different donors across conditions")
    x=a.layers["counts"]
    results={}; exclusions=[]
    for ct in sorted(obs[celltype_key].unique()):
        if ct.lower() in ("unknown","unassigned","doublet"):
            exclusions.append({"cell_type":ct,"reason":"unresolved_or_doublet_label"}); continue
        rows=[]; sums=[]
        mask=selected & obs[celltype_key].eq(ct)
        for (donor,condition),g in obs[mask].groupby([donor_key,condition_key],observed=True):
            if len(g)<min_cells:
                exclusions.append({"cell_type":ct,"donor":donor,"condition":condition,"n_cells":len(g),"reason":"too_few_cells"})
                continue
            idx=obs.index.get_indexer(g.index)
            sums.append(np.asarray(x[idx].sum(axis=0)).ravel())
            rows.append({"donor":donor,"condition":condition,"n_cells":len(g)})
        meta=pd.DataFrame(rows,columns=["donor","condition","n_cells"])
        if not len(meta):
            results[ct]={"status":"disabled","reason":"no_eligible_groups"}; continue
        pb=pd.DataFrame(sums,columns=a.var_names)
        if design=="paired":
            complete=[d for d,g in meta.groupby("donor") if set(g.condition)=={case,control}]
            for d in sorted(set(meta.donor)-set(complete)):
                exclusions.append({"cell_type":ct,"donor":d,"reason":"missing_eligible_side_of_requested_contrast"})
            keep=meta.donor.isin(complete)
            n=len(complete)
            if n<min_donors:
                results[ct]={"status":"disabled","reason":"insufficient_complete_pairs","n_pairs":n}; continue
            meta=meta[keep].reset_index(drop=True); pb=pb[keep.to_numpy()].reset_index(drop=True)
        else:
            counts=meta.groupby("condition").donor.nunique().to_dict()
            if any(counts.get(c,0)<min_donors for c in [case,control]):
                results[ct]={"status":"disabled","reason":"insufficient_independent_donors","donors_per_condition":counts}; continue
        ids=[f"pb_{i:04d}" for i in range(len(meta))]
        meta.index=ids; pb.index=ids
        results[ct]={"status":"ready","counts":pb,"metadata":meta}
    return results,exclusions


def run(args,report):
    if args.min_gene_counts < 1 or args.cpus < 1:
        raise ValueError("min_gene_counts and cpus must be positive")
    a=load_counts(args.input,args.metadata)
    if args.celltype_key=="cell_type" and not bool(a.uns.get("cell_type_reviewed",False)):
        raise ValueError("cell_type lacks a recorded review; supply reviewed labels in the annotation stage")
    if args.celltype_key=="cell_type_proposal":
        raise ValueError("Condition DE cannot treat unreviewed proposals as final labels")
    if args.celltype_key!="cell_type" and not args.labels_reviewed:
        raise ValueError("External annotation requires --labels-reviewed after checking its origin")
    results,exclusions=pseudobulk(a,args.celltype_key,args.donor_key,args.condition_key,args.case,args.control,
                                args.design,args.min_cells,args.min_donors)
    pd.DataFrame(exclusions,columns=["cell_type","donor","condition","n_cells","reason"]).to_csv(args.outdir/"exclusions.csv",index=False)
    formula="~ donor + condition" if args.design=="paired" else "~ condition"
    report.update(design=formula,contrast={"case":args.case,"control":args.control},per_cell_type={},
                  ignored_other_condition_cells=int((~a.obs[args.condition_key].astype(str).isin([args.case,args.control])).sum()))
    report["warnings"].append("Three donors is an operational minimum, not a power guarantee. Condition/capture confounding limits interpretation to associations.")
    report["warnings"].append("BH correction is per cell type; this is not a study-wide FDR guarantee across cell types.")
    eligible=0
    for ct,entry in results.items():
        if entry["status"]!="ready":
            report["per_cell_type"][ct]=entry; continue
        pb,meta=entry["counts"],entry["metadata"]
        tag=safe_name(ct)
        meta.to_csv(args.outdir/f"pseudobulk_metadata_{tag}.csv")
        pb.to_csv(args.outdir/f"pseudobulk_counts_{tag}.csv")
        keep=pb.sum(axis=0)>=args.min_gene_counts
        if not keep.any():
            report["per_cell_type"][ct]={"status":"disabled","reason":"no_genes_after_prefilter"}; continue
        from pydeseq2.dds import DeseqDataSet
        from pydeseq2.ds import DeseqStats
        fit=DeseqDataSet(counts=pb.loc[:,keep].round().astype(np.int64),metadata=meta,design=formula,n_cpus=args.cpus,refit_cooks=True)
        fit.deseq2()
        stats=DeseqStats(fit,contrast=["condition",args.case,args.control],n_cpus=args.cpus)
        stats.summary()
        res=stats.results_df.copy()  # retain NA padj rows; never pretend they weren't tested
        res.to_csv(args.outdir/f"de_{tag}.csv")
        eligible+=1
        report["per_cell_type"][ct]={"status":"complete","n_donors":int(meta.donor.nunique()),
                                     "n_pseudobulk_samples":len(meta),"n_genes_fit":len(res),
                                     "n_genes_with_padj":int(res.padj.notna().sum()),
                                     "n_padj_below_005":int(res.padj.lt(0.05).sum())}
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(5,4)); good=res.dropna(subset=["padj","log2FoldChange"])
        ax.scatter(good.log2FoldChange,-np.log10(good.padj.clip(lower=1e-300)),s=5)
        ax.set(xlabel=f"log2FC: {args.case} / {args.control}",ylabel="-log10 BH-adjusted p",title=ct)
        fig.tight_layout(); fig.savefig(args.outdir/f"volcano_{tag}.png",dpi=120); plt.close(fig)
    if not eligible:
        report["status"]="blocked"
        report["warnings"].append("No eligible cell type was fitted. Read exclusions; do not replace donor-level DE with cell-level tests.")
