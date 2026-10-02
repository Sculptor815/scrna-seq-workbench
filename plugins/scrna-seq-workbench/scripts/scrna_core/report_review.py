"""Normalize verified vendor-report observations, without guessing missing values."""
from pathlib import Path
from html.parser import HTMLParser
import math

from .common import read_json, write_json

METRICS = {
    "estimated_cells": ("cells", "count"),
    "median_umi_per_cell": ("UMI/cell", "number"),
    "median_genes_per_cell": ("genes/cell", "number"),
    "mean_reads_per_cell": ("reads/cell", "number"),
    "sequencing_saturation_pct": ("percent", "percentage"),
    "reads_in_cells_pct": ("percent", "percentage"),
    "mapped_reads_pct": ("percent", "percentage"),
    "q30_rna_pct": ("percent", "percentage"),
}


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.hidden = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


def run(args, report):
    doc = read_json(args.metrics)
    for key in ("sample_id", "platform", "report_version", "species", "metrics"):
        if not doc.get(key):
            raise ValueError(f"Missing report field: {key}")
    if not args.source or not Path(args.source).is_file():
        raise ValueError("A source report or screenshot is required for the audit trail")
    source = Path(args.source)
    if source.suffix.lower() in (".html", ".htm"):
        parser = VisibleText(); parser.feed(source.read_text(encoding="utf-8", errors="replace"))
        (args.outdir / "report_visible_text.txt").write_text("\n".join(parser.parts), encoding="utf-8")
    found = {}
    for name, entry in doc["metrics"].items():
        if name not in METRICS:
            raise ValueError(f"Unknown normalized metric name: {name}")
        unit, kind = METRICS[name]
        val = entry.get("value")
        if val is not None:
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val) or val < 0:
                raise ValueError(f"Invalid numerical metric: {name}")
            if kind == "percentage" and val > 100:
                raise ValueError(f"Percent must be 0..100: {name}")
            if kind == "count" and int(val) != val:
                raise ValueError(f"Cell count must be an integer: {name}")
            if not entry.get("evidence") or entry.get("verified") is not True:
                raise ValueError(f"Value needs a checked source location/quote: {name}")
        if entry.get("unit") != unit:
            raise ValueError(f"Expected unit {unit}: {name}")
        found[name] = entry
    missing = [m for m in METRICS if m not in found or found[m].get("value") is None]
    report.update(sample_id=doc["sample_id"], platform=doc["platform"], metrics=found,
                  missing_metrics=missing, decision="review_required", matrix_supplied=bool(args.matrix))
    report["warnings"].append("Report-level summaries do not establish per-cell QC, doublet rate or biological replication.")
    if "dnbe" in doc["platform"].lower() or "mgi" in doc["platform"].lower():
        report["warnings"].append("Beads per droplet is not a cell-doublet fraction; retain the vendor's definition.")
    if not args.matrix:
        report["warnings"].append("A report alone cannot run downstream analysis; obtain the UMI count matrix and cell metadata.")
    write_json(args.outdir / "normalized_metrics.json", doc)
    lines = ["# 测序交付报告检查", f"样本：{doc['sample_id']}；平台：{doc['platform']}",
             "", "| 指标 | 值 | 单位 | 证据 |", "|---|---:|---|---|"]
    for name, e in found.items():
        lines.append(f"| {name} | {e.get('value')} | {e['unit']} | {str(e.get('evidence','')).replace('|','/')} |")
    lines += ["", "缺失指标：" + ", ".join(missing), "", "当前判断：需要结合建库方案、预期回收量、原始矩阵和样本间对比复核；不自动判定合格。",
              "", "下一步：核对样本表与原始 UMI 矩阵，再运行 scrna-qc。"]
    (args.outdir / "review.md").write_text("\n".join(lines), encoding="utf-8")
