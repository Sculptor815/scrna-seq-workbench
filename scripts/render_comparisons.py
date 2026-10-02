"""Re-render five comparison figures from the committed public coordinate tables."""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,default=ROOT/'benchmarks/evidence')
    parser.add_argument('--outdir',type=Path,default=ROOT/'docs/figures')
    args=parser.parse_args(); args.outdir.mkdir(parents=True,exist_ok=True)
    titles={'kang':'Kang 2018 | Human PBMC','haber':'Haber 2017 | Mouse intestine',
            'paul':'Paul 2015 | Mouse myeloid progenitors','zeisel':'Zeisel 2015 | Mouse brain',
            'baron':'Baron 2016 | Human pancreas'}
    for name,title in titles.items():
        frame=pd.read_csv(args.evidence/name/'embedding.csv',dtype={'cluster':str})
        labels=sorted(set(frame.reference_broad)|set(frame.proposal))
        colors={label:plt.get_cmap('tab20')(i%20) for i,label in enumerate(labels)}
        colors['Unknown']='#a0a4aa'
        fig,axes=plt.subplots(1,3,figsize=(18,5.8))
        for ax,column,heading in zip(axes,['reference_broad','cluster','proposal'],
            ['Author/reference labels\non plugin UMAP','Plugin Leiden clusters','Plugin marker proposals\nHuman HPA-guided review pending']):
            for i,label in enumerate(sorted(frame[column].unique())):
                mask=frame[column]==label
                color=plt.get_cmap('tab20')(i%20) if column=='cluster' else colors[label]
                ax.scatter(frame.loc[mask,'umap_1'],frame.loc[mask,'umap_2'],s=3,alpha=.72,c=[color],label=label,rasterized=True)
            ax.set_title(heading,fontsize=12); ax.set_xticks([]); ax.set_yticks([])
            ax.set_xlabel('UMAP 1'); ax.set_ylabel('UMAP 2')
            ax.legend(loc='upper left',bbox_to_anchor=(1,1),fontsize=6,frameon=False,markerscale=3)
        fig.suptitle(f'{title} | scVI seed 0 | n={len(frame):,}',fontsize=16)
        fig.text(.5,.025,'All panels share our coordinates. Left is a label replot, NOT the original paper embedding. Seed 0 was fixed; no best-seed selection.',ha='center',fontsize=10)
        fig.tight_layout(rect=(0,.055,1,.94));fig.savefig(args.outdir/f'{name}-comparison.png',dpi=150,bbox_inches='tight');plt.close(fig)
        print(name,'comparison rendered')


if __name__=='__main__': main()
