#!/usr/bin/env python
"""Analysis commands with count preservation and traceable output directories."""
from pathlib import Path
import argparse
import importlib
import json
import sys
from scrna_core.common import stage_run


def parser():
    ap=argparse.ArgumentParser(description=__doc__)
    subs=ap.add_subparsers(dest="stage",required=True)
    for name in ("report","qc","integrate","annotate","de","research"):
        p=subs.add_parser(name)
        p.add_argument("--outdir",type=Path,required=True,help="New/empty output directory; existing results are never overwritten")
        if name!="report":
            p.add_argument("--input",type=Path,required=True)
        if name=="report":
            p.add_argument("--metrics",type=Path,required=True); p.add_argument("--source",type=Path,required=True)
            p.add_argument("--matrix",type=Path)
        if name=="research":
            p.add_argument("--question",required=True)
            p.add_argument("--genes",nargs="+",required=True,help="Exact var_names; no guessed gene-ID mapping")
            p.add_argument("--celltype-key",required=True)
            p.add_argument("--donor-key",required=True)
            p.add_argument("--condition-key",required=True)
            p.add_argument("--label-source",required=True,help="Publication, file or review identifying label provenance")
            p.add_argument("--label-status",choices=["published","reviewed","exploratory"],required=True)
            p.add_argument("--min-cells",type=int,default=20)
        if name=="qc":
            p.add_argument("--config",type=Path,required=True); p.add_argument("--metadata",type=Path)
            p.add_argument("--sample-key",default="sample_id"); p.add_argument("--single-sample")
            p.add_argument("--species",choices=["human","mouse"],required=True)
            p.add_argument("--inspect-only",action="store_true"); p.add_argument("--doublets",action="store_true")
            p.add_argument("--remove-doublets",action="store_true"); p.add_argument("--capture-key",default="capture_id")
            p.add_argument("--expected-doublet-rate",type=float,default=0.06); p.add_argument("--seed",type=int,default=0)
        if name=="integrate":
            p.add_argument("--backend",choices=["scvi","harmony"],default="scvi",help="Default scVI; explicitly select harmony (harmonypy) for a CPU alternative with verified batches")
            p.add_argument("--backend-reason",help="Record the user's backend choice or delegated rationale; never fabricate consent")
            p.add_argument("--batch-key",help="Verified technical batch column; omit for no-batch scVI")
            p.add_argument("--species",choices=["human","mouse"],required=True)
            p.add_argument("--cell-cycle-genes",type=Path,help="JSON with species, source, s_genes, g2m_genes in exact var_names; required for mouse/non-symbol IDs")
            p.add_argument("--min-cycle-genes",type=int,default=5,help="Minimum matched genes per phase; inspect coverage even when this passes")
            p.add_argument("--skip-cell-cycle",action="store_true",help="Only for an explicit user override, recorded with its reason")
            p.add_argument("--cell-cycle-override-reason",help="Quote or identify the user's explicit override; never infer consent")
            p.add_argument("--hvg",type=int,default=3000); p.add_argument("--hvg-flavor",choices=["seurat","seurat_v3"],default="seurat_v3")
            p.add_argument("--latent",type=int,default=20); p.add_argument("--n-layers",type=int,default=2)
            p.add_argument("--dropout",type=float,default=0.1); p.add_argument("--neighbors",type=int,default=30)
            p.add_argument("--resolution",type=float,default=1); p.add_argument("--max-epochs",type=int,default=400)
            p.add_argument("--batch-size",type=int,default=256); p.add_argument("--early-stopping-patience",type=int,default=20)
            p.add_argument("--no-early-stopping",action="store_true"); p.add_argument("--train-size",type=float,default=0.9)
            p.add_argument("--neighbors-grid",nargs="+",type=int,default=[15,20,30,50])
            p.add_argument("--resolutions-grid",nargs="+",type=float,default=[0.3,0.5,0.8,1.0])
            p.add_argument("--device",choices=["cpu","gpu","auto"],default="auto",help="scVI: auto uses available CUDA, otherwise CPU; Harmony uses CPU"); p.add_argument("--seed",type=int,default=0)
        if name=="annotate":
            p.add_argument("--annotation-policy",choices=["hpa-guided","legacy"],default="hpa-guided",
                           help="HPA-guided evidence/manual review, or the historical marker-only review contract")
            group=p.add_mutually_exclusive_group(required=True)
            group.add_argument("--panel",type=Path); group.add_argument("--hpa-expression",type=Path)
            p.add_argument("--allowed-types",type=Path); p.add_argument("--reviewed-labels",type=Path)
            p.add_argument("--species",choices=["human","mouse"],required=True); p.add_argument("--tissue",required=True)
            p.add_argument("--cluster-key",default="leiden"); p.add_argument("--top-markers",type=int,default=20)
            p.add_argument("--min-markers",type=int,default=2); p.add_argument("--min-overlap",type=float,default=0.5)
            p.add_argument("--min-score",type=float,default=0.5); p.add_argument("--min-margin",type=float,default=0.25)
        if name=="de":
            p.add_argument("--metadata",type=Path); p.add_argument("--celltype-key",default="cell_type")
            p.add_argument("--donor-key",default="donor_id"); p.add_argument("--condition-key",default="condition")
            p.add_argument("--case",required=True); p.add_argument("--control",required=True)
            p.add_argument("--design",choices=["paired","unpaired"],required=True)
            p.add_argument("--min-cells",type=int,default=20); p.add_argument("--min-donors",type=int,default=3)
            p.add_argument("--min-gene-counts",type=int,default=10); p.add_argument("--cpus",type=int,default=1)
            p.add_argument("--labels-reviewed",action="store_true")
    return ap


def main(argv=None):
    args=parser().parse_args(argv)
    inputs=[v for k,v in vars(args).items() if isinstance(v,Path) and k!="outdir"]
    try:
        with stage_run(args.stage,args.outdir,vars(args),inputs) as report:
            module=importlib.import_module("scrna_core."+{"report":"report_review"}.get(args.stage,args.stage))
            if args.stage!="report":
                import matplotlib
                matplotlib.use("Agg")
            module.run(args,report)
        print(json.dumps({"status":report["status"],"report":str(args.outdir/"report.json")}))
        return 3 if report["status"]=="blocked" else 0
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
