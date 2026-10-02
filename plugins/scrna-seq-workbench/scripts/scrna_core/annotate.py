import numpy as np
import pandas as pd
from .common import load_counts, lognormalize, read_json, require_columns, write_json


def read_panel(args, a):
    species=a.uns.get("scrna_species",args.species)
    if species!=args.species:
        raise ValueError("Declared species conflicts with input metadata")
    if args.panel:
        panel=read_json(args.panel)
        if panel.get("species")!=species or panel.get("tissue")!=args.tissue or not panel.get("source"):
            raise ValueError("Panel must declare matching species, tissue and an evidence source")
        markers=panel.get("markers",{})
        source=panel["source"]
    else:
        if species!="human":
            raise ValueError("HPA is human-only; use a species-matched curated panel")
        if not args.allowed_types:
            raise ValueError("HPA needs an explicit tissue-appropriate allowed-types JSON")
        policy=read_json(args.allowed_types)
        if policy.get("tissue")!=args.tissue or not policy.get("cell_types") or not policy.get("source"):
            raise ValueError("Allowed-types policy needs matching tissue, cell_types and rationale/source")
        expr=pd.read_csv(args.hpa_expression,sep="\t")
        required={"Gene name","Cell type","nCPM"}
        if not required.issubset(expr.columns):
            raise ValueError("HPA schema mismatch: expected Gene name, Cell type, nCPM")
        mat=expr.pivot_table(index="Gene name",columns="Cell type",values="nCPM",aggfunc="mean")
        allowed=policy["cell_types"]
        if set(allowed)-set(mat.columns):
            raise ValueError("An allowed HPA cell type is absent from this reference version")
        mat=mat[allowed].fillna(0)
        if len(allowed)<2:
            raise ValueError("At least two competing reference cell types are required")
        l=np.log2(mat+1); specificity=l-(l.sum(axis=1).to_numpy()[:,None]-l)/(len(allowed)-1)
        markers={ct:specificity[ct][(mat[ct]>=1) & (specificity[ct]>0)].nlargest(args.top_markers).index.tolist() for ct in allowed}
        source={"reference":"HPA nCPM matrix","tissue_policy":policy}
    if not isinstance(markers,dict) or len(markers)<2:
        raise ValueError("At least two marker sets are required")
    for ct,genes in markers.items():
        if not isinstance(ct,str) or not isinstance(genes,list) or not genes or not all(isinstance(g,str) and g for g in genes):
            raise ValueError("Marker panels must map cell type names to nonempty gene lists")
        if len(genes)!=len(set(genes)):
            raise ValueError("Duplicate marker genes would bias scores")
    return markers,source


def propose(a, cluster_key, markers, min_markers=2, min_overlap=0.5, min_score=0.5, min_margin=0.25):
    require_columns(a.obs,[cluster_key])
    clusters=a.obs[cluster_key].astype(str)
    x=a.layers["lognorm"]
    means={c:np.asarray(x[(clusters==c).to_numpy()].mean(axis=0)).ravel() for c in sorted(clusters.unique())}
    m=pd.DataFrame(means,index=a.var_names)
    z=m.sub(m.mean(axis=1),axis=0).div(m.std(axis=1).replace(0,np.nan),axis=0)
    rows=[]; evidence=[]
    for c in m.columns:
        scores={}
        for ct,genes in markers.items():
            present=[g for g in genes if g in m.index]
            informative=[g for g in present if np.isfinite(z.loc[g,c])]
            overlap=len(present)/len(genes)
            informative_overlap=len(informative)/len(genes)
            eligible=len(informative)>=min_markers and informative_overlap>=min_overlap
            score=float(z.loc[informative,c].mean()) if eligible else None
            if score is not None:
                scores[ct]=score
            evidence.append({"cluster":c,"candidate":ct,"score":score,"eligible":eligible,
                             "marker_overlap":overlap,"present_markers":";".join(present),
                             "informative_overlap":informative_overlap,"informative_markers":";".join(informative),
                             "missing_markers":";".join(g for g in genes if g not in m.index)})
        ranked=sorted(scores.items(),key=lambda kv:(-kv[1],kv[0]))
        best,score=ranked[0] if ranked else (None,None)
        runner=ranked[1][0] if len(ranked)>=2 else None
        margin=float(score-ranked[1][1]) if runner else None
        label="Unknown"; reason="insufficient_comparable_marker_evidence"
        if margin is not None:
            reason="weak_score_or_small_margin"
            if score>=min_score and margin>=min_margin:
                label=best; reason="marker_supported_proposal"
        rows.append({"cluster":c,"cell_type_proposal":label,"best_candidate":best,"score":score,
                     "runner_up":runner,"margin":margin,"reason":reason,"review_status":"pending",
                     "n_cells":int((clusters==c).sum())})
    return pd.DataFrame(rows),pd.DataFrame(evidence)


def apply_review(a, path, cluster_key, policy="legacy"):
    reviewed=pd.read_csv(path,dtype=str)
    if policy == "hpa-guided":
        from .annotation_policy import validate_hpa_review
        reviewed=validate_hpa_review(reviewed,a.obs[cluster_key].astype(str).unique(),a.var_names)
    for c in ("cluster","cell_type","reviewer","rationale"):
        require_columns(reviewed,[c])
    reviewed["cell_type"]=reviewed["cell_type"].str.strip()
    if reviewed.cluster.duplicated().any() or set(reviewed.cluster)!=set(a.obs[cluster_key].astype(str)):
        raise ValueError("Reviewed labels must match every cluster exactly once")
    lookup=reviewed.set_index("cluster")
    a.obs["cell_type"]=a.obs[cluster_key].astype(str).map(lookup.cell_type).astype("category")
    if policy == "hpa-guided":
        a.obs["cell_type_detail"]=a.obs[cluster_key].astype(str).map(lookup.cell_type_detail).astype("category")
        a.obs["annotation_decision"]=a.obs[cluster_key].astype(str).map(lookup.decision).astype("category")
        a.obs["atlas_aggregation_eligible"]=a.obs["annotation_decision"].eq("accept")
    a.uns["cell_type_reviewed"]=True
    return reviewed


def run(args,report):
    import scanpy as sc
    a=load_counts(args.input)
    require_columns(a.obs,[args.cluster_key])
    if (not 0<args.min_overlap<=1 or args.min_markers<2 or args.min_margin<0 or args.top_markers<2
            or not np.isfinite([args.min_score,args.min_margin]).all()):
        raise ValueError("Invalid annotation thresholds")
    lognormalize(a)
    markers,source=read_panel(args,a)
    table,evidence=propose(a,args.cluster_key,markers,args.min_markers,args.min_overlap,args.min_score,args.min_margin)
    policy=getattr(args,"annotation_policy","hpa-guided")
    from .annotation_policy import export_packet
    export_packet(a,args.cluster_key,markers,table,args.outdir)
    table.to_csv(args.outdir/"annotation_proposals.csv",index=False)
    evidence.to_csv(args.outdir/"annotation_evidence.csv",index=False)
    write_json(args.outdir/"markers_used.json",{"markers":markers,"source":source,"tissue":args.tissue,"species":args.species})
    a.obs["cell_type_proposal"]=a.obs[args.cluster_key].astype(str).map(table.set_index("cluster").cell_type_proposal).astype("category")
    # Do not silently retain an old 'cell_type' under a new proposal run.
    for old in ["cell_type","cell_type_detail","annotation_decision","atlas_aggregation_eligible"]:
        if old in a.obs:
            del a.obs[old]
    a.uns["cell_type_reviewed"]=False
    if args.reviewed_labels:
        apply_review(a,args.reviewed_labels,args.cluster_key,policy).to_csv(args.outdir/"reviewed_labels.csv",index=False)
    size=a.obs[args.cluster_key].value_counts()
    if len(size)>1 and size.min()>=2:
        sc.tl.rank_genes_groups(a,groupby=args.cluster_key,method="wilcoxon",use_raw=False,layer="lognorm")
        sc.get.rank_genes_groups_df(a,group=None).to_csv(args.outdir/"exploratory_markers.csv",index=False)
    else:
        report["warnings"].append("Cluster marker ranking skipped: need at least two groups and two cells in each.")
    a.write_h5ad(args.outdir/"annotated.h5ad")
    report.update(tissue=args.tissue,species=args.species,n_clusters=len(table),
                  annotation_policy=policy,hpa_exact_replication=False,
                  hpa_review_status="manual_review_recorded" if args.reviewed_labels and policy=="hpa-guided" else "pending" if policy=="hpa-guided" else "not_applicable",
                  unknown_clusters=int(table.cell_type_proposal.eq("Unknown").sum()),
                  reviewed=bool(args.reviewed_labels),label_column="cell_type" if args.reviewed_labels else "cell_type_proposal")
    report["warnings"].append("Scores are heuristic and relative to these clusters, not calibrated confidence probabilities. Review candidate evidence and tissue plausibility.")
    report["warnings"].append("Wilcoxon markers are exploratory; clusters and marker tests reuse the same cells.")
    report["warnings"].append("HPA-guided means a documented evidence/manual-review workflow, not reproduction of HPA's data, full marker collection, QC or atlas normalization. Mouse panels are an adaptation, not HPA reference labels.")
